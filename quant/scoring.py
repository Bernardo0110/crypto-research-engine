import numpy as np
from config.mappings import PESOS_QUANT, LIMIARES_QUANT


def _score_percentil(valor: float, valores_peers: list[float],
                     quanto_maior_melhor: bool = True) -> float:
    """
    Converte um valor em score 0–10 baseado em percentil dentro do peer set.
    Remove NaNs antes de calcular.
    """
    peers_validos = [v for v in valores_peers if not np.isnan(v)]
    if not peers_validos or np.isnan(valor):
        return np.nan
    percentil = sum(v < valor for v in peers_validos) / len(peers_validos)
    score = percentil * 10
    return score if quanto_maior_melhor else 10 - score


def _score_absoluto(valor: float, limiares: dict) -> float:
    """
    Converte valor em score 0–10 usando limiares fixos definidos em mappings.
    limiares: dict com chaves 'ruim', 'fraco', 'neutro', 'bom', 'otimo'
    correspondendo aos breakpoints crescentes.
    """
    if np.isnan(valor):
        return np.nan
    breakpoints = [
        (limiares["otimo"],  10.0),
        (limiares["bom"],     7.5),
        (limiares["neutro"],  5.0),
        (limiares["fraco"],   2.5),
    ]
    for threshold, score in breakpoints:
        if valor >= threshold:
            return score
    return 0.0


def score_sharpe(sharpe: float) -> float:
    return _score_absoluto(sharpe, LIMIARES_QUANT["sharpe"])


def score_sortino(sortino: float) -> float:
    return _score_absoluto(sortino, LIMIARES_QUANT["sortino"])


def score_max_drawdown(drawdown: float) -> float:
    """Drawdown é negativo — quanto menos negativo, melhor."""
    if np.isnan(drawdown):
        return np.nan
    # Inverte: -0.20 → melhor que -0.80
    return _score_absoluto(-drawdown, LIMIARES_QUANT["max_drawdown_invertido"])


def score_cagr(cagr: float) -> float:
    return _score_absoluto(cagr, LIMIARES_QUANT["cagr"])


def score_volatilidade(vol: float) -> float:
    """Volatilidade: menos é melhor — limiar invertido."""
    if np.isnan(vol):
        return np.nan
    return _score_absoluto(-vol, LIMIARES_QUANT["volatilidade_invertida"])


def score_calmar(calmar: float) -> float:
    return _score_absoluto(calmar, LIMIARES_QUANT["calmar"])


def score_var(var_95: float) -> float:
    """VaR é negativo — menos negativo é melhor."""
    if np.isnan(var_95):
        return np.nan
    return _score_absoluto(-var_95, LIMIARES_QUANT["var_invertido"])


def calcular_score_quant(metricas: dict) -> dict:
    """
    Recebe dict de métricas quantitativas e retorna scores individuais
    e score quant final ponderado (0–10).
    """
    scores_individuais = {
        "score_sharpe":     score_sharpe(metricas.get("sharpe_1a", np.nan)),
        "score_sortino":    score_sortino(metricas.get("sortino_1a", np.nan)),
        "score_drawdown":   score_max_drawdown(metricas.get("max_drawdown", np.nan)),
        "score_cagr":       score_cagr(metricas.get("cagr_2a", np.nan)),
        "score_volatilidade": score_volatilidade(metricas.get("volatilidade_1a", np.nan)),
        "score_calmar":     score_calmar(metricas.get("calmar", np.nan)),
        "score_var":        score_var(metricas.get("var_95", np.nan)),
    }

    # Pesos definidos em mappings.PESOS_QUANT
    # Redistribui proporcionalmente se algum score for NaN
    peso_total = 0.0
    score_ponderado = 0.0

    for chave_score, peso in PESOS_QUANT.items():
        s = scores_individuais.get(chave_score, np.nan)
        if not np.isnan(s):
            score_ponderado += s * peso
            peso_total += peso

    score_final = (score_ponderado / peso_total) if peso_total > 0 else np.nan

    return {
        **scores_individuais,
        "score_quant": round(score_final, 2),
    }