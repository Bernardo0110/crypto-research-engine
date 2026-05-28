import numpy as np
import pandas as pd


def validar_pilares(resultado_pilares: dict) -> list[str]:
    """
    Verifica consistência dos dados fundamentalistas.
    Retorna lista de avisos — vazia se tudo ok.
    """
    avisos = []
    pilares = resultado_pilares.get("pilares", {})

    # Tokenomics
    tok = pilares.get("tokenomics", {})
    fdv_mcap = tok.get("fdv_mcap_ratio", np.nan)
    if not np.isnan(fdv_mcap) and fdv_mcap < 1.0:
        avisos.append(
            f"FDV/MCap = {fdv_mcap:.2f} < 1.0 — incomum, verificar se FDV está correto."
        )
    if not np.isnan(fdv_mcap) and fdv_mcap > 10:
        avisos.append(
            f"FDV/MCap = {fdv_mcap:.1f}x — diluição futura muito elevada."
        )

    # Supply
    inflacao = tok.get("inflacao_supply", np.nan)
    if not np.isnan(inflacao) and inflacao > 1.0:
        avisos.append(
            f"Inflação de supply = {inflacao*100:.0f}% — supply circulante muito menor que total."
        )

    # Protocol Revenue
    pr = pilares.get("protocol_revenue", {})
    mcap_tvl = pr.get("mcap_tvl_ratio", np.nan)
    if not np.isnan(mcap_tvl) and mcap_tvl > 50:
        avisos.append(
            f"MCap/TVL = {mcap_tvl:.1f}x — protocolo pode estar fortemente sobrevalorizado."
        )

    fdv_rev = pr.get("fdv_revenue_ratio", np.nan)
    if not np.isnan(fdv_rev) and fdv_rev > 500:
        avisos.append(
            f"FDV/Revenue = {fdv_rev:.0f}x — múltiplo de receita extremamente elevado."
        )

    # Developer
    dev = pilares.get("developer", {})
    commits = dev.get("github_commits_4s", np.nan)
    if not np.isnan(commits) and commits == 0:
        avisos.append("Zero commits nas últimas 4 semanas — desenvolvimento pode estar estagnado.")

    # Pilares ausentes
    ausentes = resultado_pilares.get("pilares_ausentes", [])
    if ausentes:
        avisos.append(f"Pilares sem dados suficientes: {', '.join(ausentes)}.")

    return avisos


def resumo_cobertura(resultado_pilares: dict) -> dict:
    """
    Retorna dict com cobertura de dados por pilar (True/False).
    Útil para o PDF exibir quais seções têm dados completos.
    """
    pilares = resultado_pilares.get("pilares", {})
    return {
        pilar: bool(dados)
        for pilar, dados in pilares.items()
    }