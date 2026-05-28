import numpy as np
import pandas as pd
from scipy import stats
from config.settings import DIAS_ANO
from config.mappings import LIMIARES_MACRO


def retornos_diarios(precos: pd.Series) -> pd.Series:
    """Retornos percentuais diários a partir de série de preços."""
    return precos.pct_change().dropna()


def cagr(precos: pd.Series) -> float:
    """Compound Annual Growth Rate."""
    if precos.empty or len(precos) < 2:
        return np.nan
    anos = len(precos) / DIAS_ANO
    if anos == 0:
        return np.nan
    return (precos.iloc[-1] / precos.iloc[0]) ** (1 / anos) - 1


def volatilidade_anual(retornos: pd.Series) -> float:
    """Volatilidade anualizada (desvio padrão dos retornos diários × √DIAS_ANO)."""
    if retornos.empty:
        return np.nan
    return float(retornos.std() * np.sqrt(DIAS_ANO))


def sharpe(retornos: pd.Series, taxa_livre_risco_anual: float) -> float:
    """
    Sharpe Ratio anualizado.
    taxa_livre_risco_anual: Fed Funds Rate como decimal (ex: 0.053).
    """
    if retornos.empty:
        return np.nan
    rfr_diaria = (1 + taxa_livre_risco_anual) ** (1 / DIAS_ANO) - 1
    excesso = retornos - rfr_diaria
    if excesso.std() == 0:
        return np.nan
    return float((excesso.mean() / excesso.std()) * np.sqrt(DIAS_ANO))


def sortino(retornos: pd.Series, taxa_livre_risco_anual: float) -> float:
    """Sortino Ratio — penaliza apenas volatilidade negativa."""
    if retornos.empty:
        return np.nan
    rfr_diaria = (1 + taxa_livre_risco_anual) ** (1 / DIAS_ANO) - 1
    excesso = retornos - rfr_diaria
    downside = excesso[excesso < 0]
    if downside.empty or downside.std() == 0:
        return np.nan
    return float((excesso.mean() / downside.std()) * np.sqrt(DIAS_ANO))


def max_drawdown(precos: pd.Series) -> float:
    """Maximum Drawdown: maior queda pico a vale no período."""
    if precos.empty:
        return np.nan
    pico_acumulado = precos.cummax()
    drawdowns = (precos - pico_acumulado) / pico_acumulado
    return float(drawdowns.min())


def beta(retornos_ativo: pd.Series, retornos_bench: pd.Series) -> float:
    """Beta em relação ao benchmark (BTC por padrão)."""
    alinhado = pd.concat([retornos_ativo, retornos_bench], axis=1).dropna()
    if len(alinhado) < 30:
        return np.nan
    cov = alinhado.cov().iloc[0, 1]
    var_bench = alinhado.iloc[:, 1].var()
    if var_bench == 0:
        return np.nan
    return float(cov / var_bench)


def alpha_anual(retornos_ativo: pd.Series, retornos_bench: pd.Series,
                taxa_livre_risco_anual: float) -> float:
    """Alpha de Jensen anualizado."""
    b = beta(retornos_ativo, retornos_bench)
    if np.isnan(b):
        return np.nan
    rfr_diaria   = (1 + taxa_livre_risco_anual) ** (1 / DIAS_ANO) - 1
    ret_ativo    = retornos_ativo.mean() * DIAS_ANO
    ret_bench    = retornos_bench.mean() * DIAS_ANO
    rfr_anual    = taxa_livre_risco_anual
    return float(ret_ativo - (rfr_anual + b * (ret_bench - rfr_anual)))


def var_historico(retornos: pd.Series, confianca: float = 0.95) -> float:
    """Value at Risk histórico (perda máxima esperada com `confianca` de probabilidade)."""
    if retornos.empty:
        return np.nan
    return float(np.percentile(retornos, (1 - confianca) * 100))


def correlacao(retornos_ativo: pd.Series, retornos_bench: pd.Series) -> float:
    """Correlação de Pearson entre ativo e benchmark."""
    alinhado = pd.concat([retornos_ativo, retornos_bench], axis=1).dropna()
    if len(alinhado) < 10:
        return np.nan
    return float(alinhado.corr().iloc[0, 1])


def calmar_ratio(precos: pd.Series) -> float:
    """CAGR / |Max Drawdown| — retorno ajustado pela pior queda."""
    c = cagr(precos)
    md = max_drawdown(precos)
    if np.isnan(c) or np.isnan(md) or md == 0:
        return np.nan
    return float(c / abs(md))


def retorno_periodo(precos: pd.Series, dias: int) -> float:
    """Retorno simples para um período específico em dias."""
    if precos.empty or len(precos) < dias:
        return np.nan
    return float((precos.iloc[-1] / precos.iloc[-dias]) - 1)


def calcular_todas(historico_ativo: pd.Series, historico_benchmark: pd.Series,
                   taxa_livre_risco: float) -> dict:
    """
    Calcula todas as métricas quantitativas e retorna dict completo.
    Aceita séries de preços — retornos calculados internamente.
    """
    ret_ativo = retornos_diarios(historico_ativo)
    ret_bench = retornos_diarios(historico_benchmark)

    # Subperíodos alinhados ao histórico disponível
    dias_1a  = min(365, len(historico_ativo))
    dias_2a  = min(730, len(historico_ativo))

    return {
        # Retornos por período
        "retorno_7d":       retorno_periodo(historico_ativo, 7),
        "retorno_30d":      retorno_periodo(historico_ativo, 30),
        "retorno_90d":      retorno_periodo(historico_ativo, 90),
        "retorno_1a":       retorno_periodo(historico_ativo, dias_1a),
        "retorno_2a":       retorno_periodo(historico_ativo, dias_2a),
        "cagr_2a":          cagr(historico_ativo.iloc[-dias_2a:]),

        # Risco
        "volatilidade_1a":  volatilidade_anual(ret_ativo.iloc[-dias_1a:]),
        "max_drawdown":     max_drawdown(historico_ativo),
        "var_95":           var_historico(ret_ativo),

        # Ajustados ao risco
        "sharpe_1a":        sharpe(ret_ativo.iloc[-dias_1a:], taxa_livre_risco),
        "sortino_1a":       sortino(ret_ativo.iloc[-dias_1a:], taxa_livre_risco),
        "calmar":           calmar_ratio(historico_ativo.iloc[-dias_1a:]),

        # Relação com benchmark (BTC)
        "beta_1a":          beta(ret_ativo.iloc[-dias_1a:], ret_bench.iloc[-dias_1a:]),
        "alpha_1a":         alpha_anual(ret_ativo.iloc[-dias_1a:], ret_bench.iloc[-dias_1a:],
                                        taxa_livre_risco),
        "correlacao_btc":   correlacao(ret_ativo.iloc[-dias_1a:], ret_bench.iloc[-dias_1a:]),
    }