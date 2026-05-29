import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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


def grafico_fear_greed_gauge(valor: float, label: str, coin_id: str) -> str | None:
    """Gauge semicircular do Fear & Greed Index."""
    if np.isnan(valor):
        return None

    fig, ax = plt.subplots(figsize=(6, 3.5), subplot_kw={"aspect": "equal"})
    fundo = CORES.get("fundo", "#0D1117")
    texto = CORES.get("texto", "#E6EDF3")
    fig.patch.set_facecolor(fundo)
    ax.set_facecolor(fundo)
    ax.axis("off")

    # Arcos coloridos (180° = semicírculo)
    zonas = [
        (0,  20,  CORES.get("negativo", "#F85149"),  "Ext. Medo"),
        (20, 40,  "#D29922",                          "Medo"),
        (40, 60,  CORES.get("grade", "#3D444D"),      "Neutro"),
        (60, 80,  "#3FB950",                          "Ganância"),
        (80, 100, CORES.get("positivo", "#238636"),   "Ext. Ganância"),
    ]

    for inicio, fim, cor, _ in zonas:
        theta1 = 180 - (fim / 100 * 180)
        theta2 = 180 - (inicio / 100 * 180)
        arco = mpatches.Wedge(
            center=(0, 0), r=1.0, theta1=theta1, theta2=theta2,
            width=0.3, color=cor, alpha=0.85
        )
        ax.add_patch(arco)

    # Ponteiro
    angulo_rad = np.radians(180 - (valor / 100 * 180))
    ax.annotate(
        "", xy=(0.6 * np.cos(angulo_rad), 0.6 * np.sin(angulo_rad)),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=texto, lw=2.0)
    )
    ax.plot(0, 0, "o", color=texto, markersize=6)

    ax.text(0, -0.25, f"{int(valor)}", ha="center", va="center",
            fontsize=22, fontweight="bold", color=texto)
    ax.text(0, -0.45, label, ha="center", va="center",
            fontsize=10, color=texto, alpha=0.8)
    ax.set_title("Fear & Greed Index", color=texto, fontsize=11, pad=8)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.6, 1.1)

    return _salvar(fig)


def grafico_halving_ciclo(macro: dict, coin_id: str) -> str | None:
    """Barra de progresso do ciclo de halving."""
    pct = macro.get("pct_ciclo_completo", np.nan)
    fase = macro.get("fase_ciclo", "desconhecida")
    dias = macro.get("dias_desde_halving", np.nan)
    proximo = macro.get("proximo_halving", "N/D")

    if np.isnan(pct):
        return None

    fig, ax = plt.subplots(figsize=(9, 2))
    fundo = CORES.get("fundo", "#0D1117")
    texto = CORES.get("texto", "#E6EDF3")
    grade = CORES.get("grade", "#21262D")
    fig.patch.set_facecolor(fundo)
    ax.set_facecolor(fundo)
    ax.axis("off")

    # Barra de fundo
    ax.barh(0, 100, color=grade, height=0.4, left=0)
    # Barra de progresso
    cor_progresso = CORES.get("primaria", "#F7931A")
    ax.barh(0, pct, color=cor_progresso, height=0.4, left=0, alpha=0.85)

    ax.text(pct / 2, 0, f"{pct:.0f}%", ha="center", va="center",
            fontsize=10, fontweight="bold", color=fundo)

    ax.text(0, 0.35, f"Fase: {fase.replace('_', ' ').title()}",
            ha="left", va="bottom", fontsize=9, color=texto)
    ax.text(100, 0.35,
            f"Próximo halving: {proximo}",
            ha="right", va="bottom", fontsize=9, color=texto, alpha=0.8)

    ax.set_title("Ciclo de Halving Bitcoin", color=texto, fontsize=11, pad=6)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.7)

    return _salvar(fig)


def grafico_scores_macro(scores_macro: dict, nome: str, coin_id: str) -> str | None:
    """Barras horizontais dos scores das variáveis macro."""
    mapa = {
        "score_fear_greed":    "Fear & Greed",
        "score_btc_dominance": "BTC Dominance",
        "score_funding_rate":  "Funding Rate",
        "score_halving":       "Halving Cycle",
        "score_trends":        "Google Trends",
    }

    labels, valores = [], []
    for chave, label in mapa.items():
        v = scores_macro.get(chave, np.nan)
        if not np.isnan(v):
            labels.append(label)
            valores.append(v)

    if not labels:
        return None

    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 0.6)))
    _estilo_base(fig, ax)

    cores = [
        CORES.get("positivo", "#3FB950") if v >= 6.5
        else CORES.get("alerta", "#D29922") if v >= 4.0
        else CORES.get("negativo", "#F85149")
        for v in valores
    ]

    ax.barh(labels, valores, color=cores, edgecolor="none", height=0.5)
    ax.axvline(5.0, color=CORES.get("grade", "#21262D"),
               linewidth=1.0, linestyle="--", alpha=0.8)
    ax.set_xlim(0, 10)
    ax.set_xlabel("Score (0–10)")
    ax.set_title(f"{nome} — Contexto Macro", fontsize=11, pad=10)

    for i, v in enumerate(valores):
        ax.text(v + 0.15, i, f"{v:.1f}", va="center",
                color=CORES.get("texto", "#E6EDF3"), fontsize=9)

    return _salvar(fig)


def gerar_todos(macro: dict, scores_macro: dict,
                nome: str, coin_id: str) -> dict[str, str | None]:
    """Gera todos os gráficos macro."""
    return {
        "fear_greed":   grafico_fear_greed_gauge(
                            macro.get("fear_greed_atual", np.nan),
                            macro.get("fear_greed_label", ""),
                            coin_id
                        ),
        "halving":      grafico_halving_ciclo(macro, coin_id),
        "scores_macro": grafico_scores_macro(scores_macro, nome, coin_id),
    }