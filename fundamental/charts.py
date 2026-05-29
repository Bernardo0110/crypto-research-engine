import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from config.settings import CORES


def _salvar(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


def _estilo_base(fig: plt.Figure, ax: plt.Axes) -> None:
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


def grafico_mcap_peers(df_peers: pd.DataFrame, coin_id: str, nome: str) -> str | None:
    """Barras horizontais de MCap dos peers (USD)."""
    df = df_peers["mcap_usd"].dropna().sort_values(ascending=True)
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(9, max(3, len(df) * 0.45)))
    _estilo_base(fig, ax)

    cores = [
        CORES.get("primaria", "#F7931A") if idx == coin_id
        else CORES.get("secundaria", "#58A6FF")
        for idx in df.index
    ]
    labels = [
        df_peers.loc[idx, "simbolo"] if idx in df_peers.index else idx
        for idx in df.index
    ]

    ax.barh(labels, df.values / 1e9, color=cores, edgecolor="none", height=0.6)
    ax.set_xlabel("Market Cap (USD Bilhões)")
    ax.set_title(f"{nome} — Market Cap vs Peers", fontsize=11, pad=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}B"))

    return _salvar(fig)


def grafico_scores_pilares(scores_fundamental: dict, nome: str, coin_id: str) -> str | None:
    """Barras dos scores por pilar fundamentalista."""
    mapa = {
        "score_tokenomics":       "Tokenomics",
        "score_adoption":         "Adoção",
        "score_onchain":          "On-Chain",
        "score_protocol_revenue": "Protocol Revenue",
        "score_valuation":        "Valuation",
        "score_developer":        "Developer",
    }

    labels, valores = [], []
    for chave, label in mapa.items():
        v = scores_fundamental.get(chave, np.nan)
        if not np.isnan(v):
            labels.append(label)
            valores.append(v)

    if not labels:
        return None

    fig, ax = plt.subplots(figsize=(8, 4))
    _estilo_base(fig, ax)

    cor_barras = [
        CORES.get("positivo", "#3FB950") if v >= 6.5
        else CORES.get("alerta", "#D29922") if v >= 4.0
        else CORES.get("negativo", "#F85149")
        for v in valores
    ]

    ax.barh(labels, valores, color=cor_barras, edgecolor="none", height=0.55)
    ax.axvline(5.0, color=CORES.get("grade", "#21262D"),
               linewidth=1.0, linestyle="--", alpha=0.8)
    ax.set_xlim(0, 10)
    ax.set_xlabel("Score (0–10)")
    ax.set_title(f"{nome} — Scores por Pilar Fundamentalista", fontsize=11, pad=10)

    for i, (v, label) in enumerate(zip(valores, labels)):
        ax.text(v + 0.2, i, f"{v:.1f}", va="center",
                color=CORES.get("texto", "#E6EDF3"), fontsize=9)

    return _salvar(fig)


def grafico_tvl_peers(df_peers: pd.DataFrame, coin_id: str, nome: str) -> str | None:
    """Barras de TVL dos peers DeFi. Retorna None se sem dados."""
    df = df_peers["tvl_usd"].dropna().sort_values(ascending=True)
    if df.empty or len(df) < 2:
        return None

    fig, ax = plt.subplots(figsize=(9, max(3, len(df) * 0.45)))
    _estilo_base(fig, ax)

    cores = [
        CORES.get("primaria", "#F7931A") if idx == coin_id
        else CORES.get("secundaria", "#58A6FF")
        for idx in df.index
    ]
    labels = [
        df_peers.loc[idx, "simbolo"] if idx in df_peers.index else idx
        for idx in df.index
    ]

    ax.barh(labels, df.values / 1e9, color=cores, edgecolor="none", height=0.6)
    ax.set_xlabel("TVL (USD Bilhões)")
    ax.set_title(f"{nome} — TVL vs Peers DeFi", fontsize=11, pad=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}B"))

    return _salvar(fig)


def gerar_todos(df_peers: pd.DataFrame, scores_fundamental: dict,
                nome: str, coin_id: str) -> dict[str, str | None]:
    """Gera todos os gráficos fundamentalistas."""
    return {
        "mcap_peers":     grafico_mcap_peers(df_peers, coin_id, nome),
        "scores_pilares": grafico_scores_pilares(scores_fundamental, nome, coin_id),
        "tvl_peers":      grafico_tvl_peers(df_peers, coin_id, nome),
    }