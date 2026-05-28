import numpy as np
from config.mappings import classificar_score, NOMES_SCORE_INTEGRADO


def _fmt_usd(valor: float, casas: int = 2) -> str:
    if np.isnan(valor):
        return "N/D"
    if valor >= 1e9:
        return f"${valor/1e9:.{casas}f}B"
    if valor >= 1e6:
        return f"${valor/1e6:.{casas}f}M"
    if valor >= 1e3:
        return f"${valor/1e3:.{casas}f}K"
    return f"${valor:,.{casas}f}"


def _fmt_pct(valor: float, sinal: bool = True) -> str:
    if np.isnan(valor):
        return "N/D"
    prefixo = "+" if sinal and valor > 0 else ""
    return f"{prefixo}{valor:.1f}%"


def _fmt_x(valor: float) -> str:
    if np.isnan(valor):
        return "N/D"
    return f"{valor:.2f}x"


# ── Narrativa quantitativa ────────────────────────────────────────────────────

def narrativa_quant(metricas: dict, scores: dict, nome: str, simbolo: str,
                    nome_bench: str) -> dict:
    sharpe  = metricas.get("sharpe_1a", np.nan)
    sortino = metricas.get("sortino_1a", np.nan)
    cagr    = metricas.get("cagr_2a", np.nan)
    mdd     = metricas.get("max_drawdown", np.nan)
    beta    = metricas.get("beta_1a", np.nan)
    alpha   = metricas.get("alpha_1a", np.nan)
    vol     = metricas.get("volatilidade_1a", np.nan)
    corr    = metricas.get("correlacao_btc", np.nan)

    score_q = scores.get("score_quant", np.nan)
    label_q, _ = classificar_score(score_q) if not np.isnan(score_q) else ("N/D", "")

    # Avaliação de risco/retorno
    if not np.isnan(sharpe):
        if sharpe >= 1.5:
            texto_sharpe = f"O Sharpe de {sharpe:.2f} indica retorno por unidade de risco excelente."
        elif sharpe >= 0.8:
            texto_sharpe = f"O Sharpe de {sharpe:.2f} indica perfil de risco/retorno adequado."
        elif sharpe >= 0:
            texto_sharpe = f"O Sharpe de {sharpe:.2f} é positivo mas modesto — retorno acima do risk-free, porém com volatilidade relevante."
        else:
            texto_sharpe = f"O Sharpe negativo de {sharpe:.2f} indica que o ativo não compensou adequadamente o risco assumido no período."
    else:
        texto_sharpe = "Dados insuficientes para calcular Sharpe Ratio."

    # Beta relativo ao benchmark
    if not np.isnan(beta):
        if beta > 1.3:
            texto_beta = f"O Beta de {beta:.2f} indica alta sensibilidade ao {nome_bench} — amplifica tanto ganhos quanto perdas."
        elif beta > 0.7:
            texto_beta = f"Com Beta de {beta:.2f}, o {simbolo} se move próximo ao {nome_bench}."
        else:
            texto_beta = f"Beta de {beta:.2f} indica baixa correlação com o {nome_bench} — comportamento mais independente."
    else:
        texto_beta = ""

    return {
        "score_quant":    round(score_q, 1) if not np.isnan(score_q) else "N/D",
        "label_quant":    label_q,
        "texto_sharpe":   texto_sharpe,
        "texto_beta":     texto_beta,
        "cagr_fmt":       _fmt_pct(cagr * 100 if not np.isnan(cagr) else np.nan),
        "mdd_fmt":        _fmt_pct(mdd * 100 if not np.isnan(mdd) else np.nan, sinal=False),
        "vol_fmt":        _fmt_pct(vol * 100 if not np.isnan(vol) else np.nan, sinal=False),
        "sharpe_fmt":     f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/D",
        "sortino_fmt":    f"{sortino:.2f}" if not np.isnan(sortino) else "N/D",
        "beta_fmt":       f"{beta:.2f}" if not np.isnan(beta) else "N/D",
        "alpha_fmt":      _fmt_pct(alpha * 100 if not np.isnan(alpha) else np.nan),
        "corr_fmt":       f"{corr:.2f}" if not np.isnan(corr) else "N/D",
    }


# ── Narrativa fundamentalista ─────────────────────────────────────────────────

def narrativa_fundamental(pilares: dict, scores_fund: dict, dados_mercado: dict,
                           nome: str) -> dict:
    fdv_mcap   = pilares.get("tokenomics", {}).get("fdv_mcap_ratio", np.nan)
    inflacao   = pilares.get("tokenomics", {}).get("inflacao_supply", np.nan)
    tvl        = pilares.get("protocol_revenue", {}).get("tvl_usd", np.nan)
    mcap_tvl   = pilares.get("protocol_revenue", {}).get("mcap_tvl_ratio", np.nan)
    commits    = pilares.get("developer", {}).get("github_commits_4s", np.nan)
    score_f    = scores_fund.get("score_fundamental", np.nan)
    label_f, _ = classificar_score(score_f) if not np.isnan(score_f) else ("N/D", "")

    # FDV/MCap
    if not np.isnan(fdv_mcap):
        if fdv_mcap <= 1.2:
            texto_dilution = f"Com FDV/MCap de {fdv_mcap:.2f}x, o supply está quase completamente circulante — risco de diluição baixo."
        elif fdv_mcap <= 3:
            texto_dilution = f"FDV/MCap de {fdv_mcap:.2f}x indica pressão moderada de desbloqueios futuros."
        else:
            texto_dilution = f"FDV/MCap de {fdv_mcap:.2f}x sinaliza pressão significativa de diluição futura — tokens ainda bloqueados representam múltiplos do MCap atual."
    else:
        texto_dilution = "Dados de supply insuficientes para avaliar pressão de diluição."

    # TVL (DeFi)
    texto_tvl = ""
    if not np.isnan(tvl):
        if not np.isnan(mcap_tvl):
            if mcap_tvl < 1:
                texto_tvl = f"MCap/TVL de {mcap_tvl:.2f}x indica protocolo negociando abaixo do seu TVL — potencialmente subvalorizado."
            elif mcap_tvl < 5:
                texto_tvl = f"MCap/TVL de {mcap_tvl:.2f}x está dentro de uma faixa razoável para protocolos DeFi maduros."
            else:
                texto_tvl = f"MCap/TVL elevado de {mcap_tvl:.2f}x sugere valuation premium em relação ao TVL — exige justificativa de crescimento."

    # Developer
    texto_dev = ""
    if not np.isnan(commits):
        if commits >= 50:
            texto_dev = f"Atividade de desenvolvimento intensa: {int(commits)} commits nas últimas 4 semanas."
        elif commits >= 20:
            texto_dev = f"Desenvolvimento ativo com {int(commits)} commits nas últimas 4 semanas."
        elif commits > 0:
            texto_dev = f"Atividade de desenvolvimento modesta: {int(commits)} commits recentes."
        else:
            texto_dev = "Zero commits recentes detectados — desenvolvimento pode estar estagnado."

    return {
        "score_fundamental": round(score_f, 1) if not np.isnan(score_f) else "N/D",
        "label_fundamental": label_f,
        "texto_dilution":    texto_dilution,
        "texto_tvl":         texto_tvl,
        "texto_dev":         texto_dev,
        "fdv_mcap_fmt":      _fmt_x(fdv_mcap),
        "inflacao_fmt":      _fmt_pct(inflacao * 100 if not np.isnan(inflacao) else np.nan, sinal=False),
        "tvl_fmt":           _fmt_usd(tvl) if not np.isnan(tvl) else "N/D",
        "mcap_tvl_fmt":      _fmt_x(mcap_tvl),
        "commits_fmt":       str(int(commits)) if not np.isnan(commits) else "N/D",
    }


# ── Narrativa macro ───────────────────────────────────────────────────────────

def narrativa_macro(macro: dict, scores_macro: dict, sinais: dict,
                    categoria: str | None) -> dict:
    fg        = macro.get("fear_greed_atual", np.nan)
    fg_label  = macro.get("fear_greed_label", "")
    btc_dom   = macro.get("btc_dominance", np.nan)
    funding   = macro.get("funding_rate_atual", np.nan)
    fase      = macro.get("fase_ciclo", "desconhecida")
    pct_ciclo = macro.get("pct_ciclo_completo", np.nan)
    score_m   = scores_macro.get("score_macro", np.nan)
    label_m, _ = classificar_score(score_m) if not np.isnan(score_m) else ("N/D", "")

    # Fear & Greed
    if not np.isnan(fg):
        if fg <= 25:
            texto_fg = f"Medo Extremo ({int(fg)}/100) — historicamente zonas de acumulação para investidores de longo prazo."
        elif fg <= 45:
            texto_fg = f"Medo no mercado ({int(fg)}/100) — sentimento pessimista, mas sem extremos."
        elif fg <= 65:
            texto_fg = f"Sentimento neutro ({int(fg)}/100) — mercado em equilíbrio entre compradores e vendedores."
        elif fg <= 80:
            texto_fg = f"Ganância ({int(fg)}/100) — cuidado com sobrecompra, mas tendência ainda positiva."
        else:
            texto_fg = f"Ganância Extrema ({int(fg)}/100) — risco elevado de reversão, mercado eufórico."
    else:
        texto_fg = "Fear & Greed indisponível."

    # Halving
    texto_halving = ""
    if fase != "desconhecida" and not np.isnan(pct_ciclo):
        texto_halving = f"O Bitcoin está na fase '{fase.replace('_', ' ').title()}' do ciclo de halving ({pct_ciclo:.0f}% concluído)."

    return {
        "score_macro":    round(score_m, 1) if not np.isnan(score_m) else "N/D",
        "label_macro":    label_m,
        "texto_fg":       texto_fg,
        "texto_halving":  texto_halving,
        "fg_fmt":         f"{int(fg)}/100 — {fg_label}" if not np.isnan(fg) else "N/D",
        "btc_dom_fmt":    _fmt_pct(btc_dom, sinal=False) if not np.isnan(btc_dom) else "N/D",
        "funding_fmt":    f"{funding*100:+.4f}%" if not np.isnan(funding) else "N/D",
        "fase_ciclo":     fase.replace("_", " ").title(),
        "pct_ciclo_fmt":  f"{pct_ciclo:.0f}%" if not np.isnan(pct_ciclo) else "N/D",
    }


# ── Score integrado final ─────────────────────────────────────────────────────

def calcular_score_integrado(scores_quant: dict, scores_fund: dict,
                              scores_macro: dict, analise_ia: dict,
                              pesos: dict) -> dict:
    """
    Agrega os 4 componentes no Score Integrado Final.
    Pesos redistribuídos para componentes ausentes.
    """
    from config.mappings import PESOS_INTEGRADO

    mapa = {
        "quant":       scores_quant.get("score_quant", np.nan),
        "fundamental": scores_fund.get("score_fundamental", np.nan),
        "macro":       scores_macro.get("score_macro", np.nan),
        "ia":          analise_ia.get("score_ia", np.nan),
    }

    peso_total = 0.0
    score_total = 0.0
    componentes_usados = {}

    for chave, score in mapa.items():
        peso = PESOS_INTEGRADO.get(chave, 0.0)
        if not np.isnan(score):
            score_total += score * peso
            peso_total  += peso
            componentes_usados[chave] = score

    score_final = round(score_total / peso_total, 2) if peso_total > 0 else np.nan
    label, cor  = classificar_score(score_final) if not np.isnan(score_final) else ("N/D", "#666")

    return {
        "score_final":          score_final,
        "label_final":          label,
        "cor_final":            cor,
        "componentes":          componentes_usados,
        "componentes_ausentes": [k for k in mapa if np.isnan(mapa[k])],
    }


# ── Orquestrador ──────────────────────────────────────────────────────────────

def gerar_narrativa_completa(dados: dict, metricas_quant: dict, scores_quant: dict,
                              pilares: dict, scores_fund: dict, macro: dict,
                              scores_macro: dict, sinais_macro: dict,
                              analise_ia: dict) -> dict:
    """
    Consolida todas as narrativas em um único dict para o template Jinja2.
    """
    from config.mappings import PESOS_INTEGRADO
    from config.settings import BENCHMARK

    nome      = dados["dados_mercado"].get("nome", dados["coin_id"])
    simbolo   = dados["dados_mercado"].get("simbolo", dados["coin_id"].upper())
    categoria = dados.get("categoria")
    md        = dados["dados_mercado"]

    score_integrado = calcular_score_integrado(
        scores_quant, scores_fund, scores_macro, analise_ia, PESOS_INTEGRADO
    )

    return {
        "meta": {
            "coin_id":    dados["coin_id"],
            "nome":       nome,
            "simbolo":    simbolo,
            "categoria":  categoria or "Crypto",
            "peers":      dados.get("peers", []),
            "benchmark":  BENCHMARK,
        },
        "mercado": {
            "preco_fmt":    f"${md.get('preco_usd', 0):,.4f}",
            "mcap_fmt":     _fmt_usd(md.get("mcap_usd", np.nan)),
            "volume_fmt":   _fmt_usd(md.get("volume_24h", np.nan)),
            "fdv_fmt":      _fmt_usd(md.get("fdv_usd", np.nan)),
            "var_24h_fmt":  _fmt_pct(md.get("variacao_24h", np.nan)),
            "var_7d_fmt":   _fmt_pct(md.get("variacao_7d", np.nan)),
            "var_30d_fmt":  _fmt_pct(md.get("variacao_30d", np.nan)),
            "rank_fmt":     f"#{int(md.get('rank_mercado', 0))}" if md.get("rank_mercado") else "N/D",
            "ath_fmt":      _fmt_usd(md.get("ath_usd", np.nan)),
        },
        "score_integrado": score_integrado,
        "quant":       narrativa_quant(metricas_quant, scores_quant, nome, simbolo, BENCHMARK),
        "fundamental": narrativa_fundamental(pilares, scores_fund, md, nome),
        "macro":       narrativa_macro(macro, scores_macro, sinais_macro, categoria),
        "ia_texto":    analise_ia.get("analise_ia_texto", ""),
        "avisos":      dados.get("avisos_validacao", []),
        "noticias":    dados.get("noticias_filtradas", [])[:8],
    }