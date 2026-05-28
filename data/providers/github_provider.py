import requests
import numpy as np
from datetime import datetime, timedelta
from config.settings import GITHUB_TOKEN
from config.mappings import API_URLS, API_TIMEOUTS

HEADERS_GH = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Mapeamento coin_id → repositório principal (owner/repo)
COINGECKO_PARA_GITHUB = {
    "bitcoin":           "bitcoin/bitcoin",
    "ethereum":          "ethereum/go-ethereum",
    "solana":            "anza-xyz/agave",
    "cardano":           "IntersectMBO/cardano-node",
    "polkadot":          "paritytech/polkadot-sdk",
    "avalanche-2":       "ava-labs/avalanchego",
    "near":              "near/nearcore",
    "aptos":             "aptos-labs/aptos-core",
    "sui":               "MystenLabs/sui",
    "chainlink":         "smartcontractkit/chainlink",
    "uniswap":           "Uniswap/v4-core",
    "aave":              "bgd-labs/aave-v3-origin",
    "maker":             "makerdao/dss",
    "compound":          "compound-finance/compound-protocol",
    "lido-dao":          "lidofinance/lido-dao",
    "gmx":               "gmx-io/gmx-contracts",
    "hyperliquid":       None,  # repo privado — sem dados GitHub
}


def _get(url: str, params: dict = {}) -> dict | list | None:
    try:
        r = requests.get(url, headers=HEADERS_GH, params=params,
                         timeout=API_TIMEOUTS["github"])
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[github] GET {url}: {e}")
        return None


def buscar_dados_repo(coin_id: str) -> dict:
    """Retorna métricas do repositório principal do projeto."""
    repo = COINGECKO_PARA_GITHUB.get(coin_id)
    if not repo:
        return {}

    base = f"{API_URLS['github']}/repos/{repo}"
    info = _get(base)
    if not info:
        return {}

    resultado = {
        "github_repo":        repo,
        "github_stars":       info.get("stargazers_count", np.nan),
        "github_forks":       info.get("forks_count", np.nan),
        "github_watchers":    info.get("subscribers_count", np.nan),
        "github_issues":      info.get("open_issues_count", np.nan),
        "github_linguagem":   info.get("language"),
        "github_criado_em":   info.get("created_at"),
        "github_atualizado":  info.get("pushed_at"),
    }

    # Commits nas últimas 4 semanas
    commits_raw = _get(f"{base}/stats/participation")
    if isinstance(commits_raw, dict):
        all_commits = commits_raw.get("all", [])
        resultado["github_commits_4s"] = int(sum(all_commits[-4:])) if len(all_commits) >= 4 else np.nan
        resultado["github_commits_52s"] = int(sum(all_commits)) if all_commits else np.nan
    else:
        resultado["github_commits_4s"]  = np.nan
        resultado["github_commits_52s"] = np.nan

    # Contribuidores ativos (top 30 — único endpoint disponível sem auth avançado)
    contribs = _get(f"{base}/contributors", params={"per_page": 30})
    if isinstance(contribs, list):
        resultado["github_contributors"] = len(contribs)
        resultado["github_commits_top30"] = sum(c.get("contributions", 0) for c in contribs)
    else:
        resultado["github_contributors"]  = np.nan
        resultado["github_commits_top30"] = np.nan

    return resultado


def buscar_dados_github_batch(coin_ids: list[str]) -> dict[str, dict]:
    """Busca métricas GitHub de múltiplos projetos."""
    return {cid: buscar_dados_repo(cid) for cid in coin_ids}