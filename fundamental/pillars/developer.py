import numpy as np


def calcular_developer(coin_id: str, github_peers: dict) -> dict:
    """
    Pilar Developer — atividade de desenvolvimento via GitHub.
    Retorna dict vazio se não houver dados para o coin.
    """
    dados = github_peers.get(coin_id, {})
    if not dados:
        return {}

    commits_4s   = dados.get("github_commits_4s", np.nan)
    commits_52s  = dados.get("github_commits_52s", np.nan)
    contributors = dados.get("github_contributors", np.nan)
    stars        = dados.get("github_stars", np.nan)
    issues       = dados.get("github_issues", np.nan)

    # Ritmo de commits: média semanal no último ano
    ritmo_semanal = np.nan
    if not np.isnan(commits_52s):
        ritmo_semanal = commits_52s / 52

    # Aceleração: commits últimas 4 semanas vs média semanal anual
    aceleracao = np.nan
    if not np.isnan(commits_4s) and not np.isnan(ritmo_semanal) and ritmo_semanal > 0:
        aceleracao = (commits_4s / 4) / ritmo_semanal

    return {
        "github_commits_4s":    commits_4s,
        "github_commits_52s":   commits_52s,
        "github_ritmo_semanal": ritmo_semanal,
        "github_aceleracao":    aceleracao,
        "github_contributors":  contributors,
        "github_stars":         stars,
        "github_issues_abertos": issues,
    }