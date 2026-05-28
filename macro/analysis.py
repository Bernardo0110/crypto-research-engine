import numpy as np
from config.mappings import SENSIBILIDADE_MACRO, LIMIARES_MACRO, PESOS_MACRO


def _score_fear_greed(valor: float) -> float:
    """
    Fear & Greed 0–100:
    Extremo Medo (<20) ou Extremo Ganância (>80) → risco elevado.
    Zona neutra (40–60) → melhor ponto de entrada/saída.
    """
    if np.isnan(valor):
        return np.nan
    if valor <= 20:
        return 3.0   # extremo medo — bearish mas possível oportunidade
    if valor <= 40:
        return 5.5   # medo moderado
    if valor <= 60:
        return 7.5   # neutro — saudável
    if valor <= 80:
        return 6.0   # ganância — cuidado com sobrecompra
    return 3.5       # extremo ganância — risco de reversão


def _score_btc_dominance(dominance: float, categoria: str | None) -> float:
    """
    BTC Dominance alta (>55%) é bearish para altcoins, bullish para BTC.
    BTC Dominance baixa (<40%) sugere season de altcoins.
    """
    if np.isnan(dominance):
        return np.nan

    eh_btc = categoria in ("layer1_btc", None) and categoria != "defi"

    if eh_btc:
        # Para BTC: alta dominance é positiva
        if dominance >= 55:
            return 8.0
        if dominance >= 45:
            return 6.5
        return 4.5
    else:
        # Para altcoins: alta dominance é negativa
        if dominance >= 60:
            return 3.0
        if dominance >= 50:
            return 5.0
        if dominance >= 40:
            return 7.0
        return 8.5   # altseason


def _score_funding_rate(funding: float) -> float:
    """
    Funding rate positivo elevado → mercado long demais → risco de squeeze.
    Funding negativo → mercado short demais → possível squeeze para cima.
    """
    if np.isnan(funding):
        return np.nan
    funding_pct = funding * 100  # converte para percentual

    if funding_pct > 0.1:
        return 3.0   # longs excessivos — bearish
    if funding_pct > 0.05:
        return 5.0   # levemente positivo
    if funding_pct >= -0.01:
        return 7.5   # neutro — saudável
    if funding_pct >= -0.05:
        return 6.0   # shorts moderados — potencial squeeze up
    return 8.0       # shorts extremos — potencial reversão forte


def _score_halving(pct_ciclo: float, fase: str) -> float:
    """
    Posição no ciclo de halving:
    Pré-halving e pós-halving imediato → historicamente bullish.
    Bear market (>60% do ciclo) → historicamente bearish.
    """
    if np.isnan(pct_ciclo):
        return np.nan

    scores_fase = {
        "acumulacao":     6.5,
        "pre_halving":    8.0,
        "pos_halving":    8.5,
        "bull_peak":      6.0,
        "bear_inicio":    4.0,
        "bear_profundo":  3.0,
        "desconhecida":   5.0,
    }
    return scores_fase.get(fase, 5.0)


def _score_trends(trends_media: float) -> float:
    """Google Trends 0–100 — interesse de busca como proxy de adoção."""
    if np.isnan(trends_media):
        return np.nan
    if trends_media >= 70:
        return 9.0
    if trends_media >= 50:
        return 7.5
    if trends_media >= 30:
        return 6.0
    if trends_media >= 15:
        return 4.5
    return 3.0


def calcular_scores_macro(macro: dict, categoria: str | None) -> dict:
    """
    Calcula scores individuais das variáveis macro e agrega no score macro final.
    Pesos redistribuídos proporcionalmente para variáveis ausentes.
    """
    fear_greed   = macro.get("fear_greed_atual", np.nan)
    btc_dom      = macro.get("btc_dominance", np.nan)
    funding      = macro.get("funding_rate_atual", np.nan)
    pct_ciclo    = macro.get("pct_ciclo_completo", np.nan)
    fase_ciclo   = macro.get("fase_ciclo", "desconhecida")
    trends_media = macro.get("trends_media_3m", np.nan)

    # Converte pct_ciclo de 0–100 para 0.0–1.0 para _score_halving
    pct_ciclo_dec = pct_ciclo / 100 if not np.isnan(pct_ciclo) else np.nan

    scores_individuais = {
        "score_fear_greed":   _score_fear_greed(fear_greed),
        "score_btc_dominance": _score_btc_dominance(btc_dom, categoria),
        "score_funding_rate": _score_funding_rate(funding),
        "score_halving":      _score_halving(pct_ciclo_dec, fase_ciclo),
        "score_trends":       _score_trends(trends_media),
    }

    # Aplica sensibilidade por categoria (multiplicador 0.5–1.5)
    sensibilidades = SENSIBILIDADE_MACRO.get(categoria, {})
    peso_total = 0.0
    score_ponderado = 0.0

    for chave, peso_base in PESOS_MACRO.items():
        s = scores_individuais.get(chave, np.nan)
        if np.isnan(s):
            continue
        sens = sensibilidades.get(chave, 1.0)
        peso_ajustado = peso_base * sens
        score_ponderado += s * peso_ajustado
        peso_total += peso_ajustado

    score_final = round(score_ponderado / peso_total, 2) if peso_total > 0 else np.nan

    return {
        **scores_individuais,
        "score_macro": score_final,
    }


def interpretar_macro(macro: dict, scores_macro: dict) -> dict:
    """
    Gera sinais textuais de alto nível para cada variável macro.
    Usado pelo PDF e pelo prompt do Gemini.
    """
    sinais = {}

    fg = macro.get("fear_greed_atual", np.nan)
    if not np.isnan(fg):
        label = macro.get("fear_greed_label", "")
        sinais["fear_greed"] = f"{int(fg)}/100 ({label})"

    dom = macro.get("btc_dominance", np.nan)
    if not np.isnan(dom):
        sinais["btc_dominance"] = f"{dom:.1f}%"

    funding = macro.get("funding_rate_atual", np.nan)
    if not np.isnan(funding):
        sinal = "positivo (longs dominam)" if funding > 0 else "negativo (shorts dominam)"
        sinais["funding_rate"] = f"{funding*100:.4f}% — {sinal}"

    fase = macro.get("fase_ciclo", "desconhecida")
    dias = macro.get("dias_desde_halving", np.nan)
    proximo = macro.get("proximo_halving", "N/D")
    if fase != "desconhecida":
        sinais["halving"] = f"Fase: {fase} | {int(dias) if not np.isnan(dias) else 'N/D'} dias desde último halving | próximo: {proximo}"

    trends = macro.get("trends_media_3m", np.nan)
    if not np.isnan(trends):
        sinais["google_trends"] = f"{trends:.0f}/100 (média 3 meses)"

    return sinais