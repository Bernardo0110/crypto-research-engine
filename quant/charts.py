import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from config.settings import CORES, ATIVO


PASTA_SAIDA = Path("outputs/charts")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)


def _salvar(fig: plt.Figure, nome: str) -> Path:
    caminho = PASTA_SAIDA / nome
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return caminho


def _estilo_base(fig: plt.Figure, ax: plt.Axes) -> None:
    """Aplica estilo escuro consistente em todos os gráficos."""
    fundo = CORES.get("fundo", "#0D1117")
    texto = CORES.get("texto", "#E6EDF3")
    grade = CORES.get("grade", "#21262D")
    fig.patch.set_facecolor(fundo)
    ax.set_facecolor(fundo)
    ax.tick_params(colors=texto, labelsize=9)
    ax.xaxis.label.set_color(texto)
    ax.yaxis.label.set_color(texto)
    ax.title.set_color(texto)
    ax.spines[:].set_color(grade)
    ax.grid(True, color=grade, linewidth=0.5, alpha=0.7)


def grafico_preco_historico(historico: pd.Series, nome: str,
                             simbolo: str, coin_id: str) -> Path:
    """Linha de preço USD com área sombreada abaixo da curva."""
    fig, ax = plt.subplots(figsize=(11, 4))
    _estilo_base(fig, ax)

    cor = CORES.get("primaria", "#F7931A")
    ax.plot(historico.index, historico.values, color=cor, linewidth=1.5)
    ax.fill_between(historico.index, historico.values, alpha=0.15, color=cor)

    ax.set_title(f"{nome} ({simbolo}) — Preço Histórico (USD)", fontsize=12, pad=10)
    ax.set_ylabel("USD")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30)

    return _salvar(fig, f"{coin_id}_preco_historico.png")


def grafico_drawdown(historico: pd.Series, nome: str, coin_id: str) -> Path:
    """Drawdown ao longo do tempo (área vermelha)."""
    pico = historico.cummax()
    drawdown = (historico - pico) / pico

    fig, ax = plt.subplots(figsize=(11, 3))
    _estilo_base(fig, ax)

    cor = CORES.get("negativo", "#F85149")
    ax.fill_between(drawdown.index, drawdown.values * 100, 0, color=cor, alpha=0.6)
    ax.plot(drawdown.index, drawdown.values * 100, color=cor, linewidth=0.8)

    ax.set_title(f"{nome} — Drawdown (%)", fontsize=12, pad=10)
    ax.set_ylabel("Drawdown (%)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30)

    return _salvar(fig, f"{coin_id}_drawdown.png")


def grafico_retornos_acumulados(historico_ativo: pd.Series,
                                 historico_bench: pd.Series,
                                 nome: str, simbolo: str,
                                 nome_bench: str, coin_id: str) -> Path:
    """Retornos acumulados do ativo vs benchmark (base 100)."""
    # Alinha os dois históricos ao período em comum
    df = pd.concat([historico_ativo, historico_bench], axis=1).dropna()
    df.columns = [simbolo, nome_bench]
    base = df.iloc[0]
    df_norm = (df / base) * 100

    fig, ax = plt.subplots(figsize=(11, 4))
    _estilo_base(fig, ax)

    ax.plot(df_norm.index, df_norm[simbolo],
            color=CORES.get("primaria", "#F7931A"), linewidth=1.5, label=simbolo)
    ax.plot(df_norm.index, df_norm[nome_bench],
            color=CORES.get("secundaria", "#58A6FF"), linewidth=1.2,
            linestyle="--", label=nome_bench, alpha=0.8)

    ax.axhline(100, color=CORES.get("grade", "#21262D"), linewidth=0.8, linestyle=":")
    ax.set_title(f"{nome} vs {nome_bench} — Retorno Acumulado (base 100)", fontsize=12, pad=10)
    ax.set_ylabel("Índice (base 100)")
    ax.legend(facecolor=CORES.get("fundo", "#0D1117"),
              labelcolor=CORES.get("texto", "#E6EDF3"), fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30)

    return _salvar(fig, f"{coin_id}_retornos_acumulados.png")


def grafico_distribuicao_retornos(historico: pd.Series, nome: str,
                                   coin_id: str) -> Path:
    """Histograma + KDE dos retornos diários."""
    retornos = historico.pct_change().dropna() * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    _estilo_base(fig, ax)

    cor = CORES.get("primaria", "#F7931A")
    sns.histplot(retornos, bins=60, ax=ax, color=cor, alpha=0.5,
                 stat="density", edgecolor="none")
    sns.kdeplot(retornos, ax=ax, color=cor, linewidth=1.5)

    ax.axvline(0, color=CORES.get("texto", "#E6EDF3"), linewidth=0.8, linestyle="--")
    ax.axvline(float(np.percentile(retornos, 5)), color=CORES.get("negativo", "#F85149"),
               linewidth=1.0, linestyle="--", alpha=0.7, label="VaR 95%")

    ax.set_title(f"{nome} — Distribuição de Retornos Diários (%)", fontsize=12, pad=10)
    ax.set_xlabel("Retorno Diário (%)")
    ax.set_ylabel("Densidade")
    ax.legend(facecolor=CORES.get("fundo", "#0D1117"),
              labelcolor=CORES.get("texto", "#E6EDF3"), fontsize=9)

    return _salvar(fig, f"{coin_id}_distribuicao_retornos.png")


def grafico_radar_scores(scores: dict, nome: str, coin_id: str) -> Path:
    """Radar chart dos scores quant individuais (0–10)."""
    labels_map = {
        "score_sharpe":       "Sharpe",
        "score_sortino":      "Sortino",
        "score_drawdown":     "Drawdown",
        "score_cagr":         "CAGR",
        "score_volatilidade": "Volatilidade",
        "score_calmar":       "Calmar",
        "score_var":          "VaR",
    }
    chaves  = [k for k in labels_map if k in scores and not np.isnan(scores[k])]
    labels  = [labels_map[k] for k in chaves]
    valores = [scores[k] for k in chaves]

    if len(chaves) < 3:
        return None  # radar sem dados suficientes

    N = len(labels)
    angulos = [n / N * 2 * np.pi for n in range(N)]
    angulos += angulos[:1]
    valores_plot = valores + valores[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    fundo = CORES.get("fundo", "#0D1117")
    texto = CORES.get("texto", "#E6EDF3")
    cor   = CORES.get("primaria", "#F7931A")

    fig.patch.set_facecolor(fundo)
    ax.set_facecolor(fundo)
    ax.tick_params(colors=texto, labelsize=8)
    ax.spines["polar"].set_color(CORES.get("grade", "#21262D"))

    ax.plot(angulos, valores_plot, color=cor, linewidth=1.5)
    ax.fill(angulos, valores_plot, color=cor, alpha=0.2)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(labels, color=texto, fontsize=9)
    ax.set_ylim(0, 10)
    ax.set_yticks([2.5, 5.0, 7.5, 10.0])
    ax.set_yticklabels(["2.5", "5", "7.5", "10"], color=texto, fontsize=7)
    ax.set_title(f"{nome} — Scores Quant", color=texto, fontsize=12, pad=15)

    return _salvar(fig, f"{coin_id}_radar_quant.png")


def gerar_todos(historico_ativo: pd.Series, historico_bench: pd.Series,
                scores: dict, nome: str, simbolo: str,
                nome_bench: str, coin_id: str) -> dict[str, Path]:
    """Gera todos os gráficos quant e retorna dict {nome: caminho}."""
    return {
        "preco_historico":      grafico_preco_historico(historico_ativo, nome, simbolo, coin_id),
        "drawdown":             grafico_drawdown(historico_ativo, nome, coin_id),
        "retornos_acumulados":  grafico_retornos_acumulados(historico_ativo, historico_bench,
                                                            nome, simbolo, nome_bench, coin_id),
        "distribuicao":         grafico_distribuicao_retornos(historico_ativo, nome, coin_id),
        "radar_quant":          grafico_radar_scores(scores, nome, coin_id),
    }