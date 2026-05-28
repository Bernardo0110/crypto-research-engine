import requests
import numpy as np
from config.mappings import API_URLS, API_TIMEOUTS

# Mapeamento coin_id (CoinGecko) → slug DeFiLlama
# Expandir conforme novos protocolos forem adicionados
COINGECKO_PARA_DEFILLAMA = {
    "uniswap":        "uniswap",
    "aave":           "aave-v3",
    "maker":          "makerdao",
    "compound":       "compound-v3",
    "curve-dao-token":"curve-dex",
    "lido-dao":       "lido",
    "rocket-pool":    "rocket-pool",
    "gmx":            "gmx",
    "jupiter-exchange-solana": "jupiter",
    "hyperliquid":    "hyperliquid-dex",
}


def _slug_defillama(coin_id: str) -> str | None:
    return COINGECKO_PARA_DEFILLAMA.get(coin_id)


def buscar_tvl(coin_id: str) -> dict:
    """Retorna TVL atual e histórico recente do protocolo."""
    slug = _slug_defillama(coin_id)
    if not slug:
        return {}
    url = f"{API_URLS['defillama_tvl']}/protocol/{slug}"
    try:
        r = requests.get(url, timeout=API_TIMEOUTS["defillama"])
        r.raise_for_status()
        d = r.json()
        tvl_atual = d.get("currentChainTvls", {})
        tvl_total = sum(tvl_atual.values()) if tvl_atual else np.nan
        historico = d.get("tvl", [])
        tvl_30d = np.nan
        tvl_90d = np.nan
        if len(historico) >= 90:
            tvl_30d = historico[-30]["totalLiquidityUSD"] if len(historico) >= 30 else np.nan
            tvl_90d = historico[-90]["totalLiquidityUSD"]
        return {
            "tvl_usd":       tvl_total,
            "tvl_30d_usd":   tvl_30d,
            "tvl_90d_usd":   tvl_90d,
            "chains":        list(tvl_atual.keys()),
        }
    except Exception as e:
        print(f"[defillama] buscar_tvl({coin_id}): {e}")
        return {}


def buscar_fees_revenue(coin_id: str) -> dict:
    """Retorna fees e revenue do protocolo (últimos 24h, 7d, 30d)."""
    slug = _slug_defillama(coin_id)
    if not slug:
        return {}
    resultado = {}
    for endpoint, prefixo in [("fees", "fees"), ("revenue", "revenue")]:
        url = f"{API_URLS['defillama_fees']}/{endpoint}/{slug}?dataType=dailyFees"
        try:
            r = requests.get(url, timeout=API_TIMEOUTS["defillama"])
            r.raise_for_status()
            d = r.json()
            total = d.get("total24h", np.nan)
            total_7d = d.get("total7d", np.nan)
            total_30d = d.get("total30d", np.nan)
            resultado[f"{prefixo}_24h"] = total
            resultado[f"{prefixo}_7d"]  = total_7d
            resultado[f"{prefixo}_30d"] = total_30d
        except Exception as e:
            print(f"[defillama] buscar_{endpoint}({coin_id}): {e}")
    return resultado


def buscar_tvl_categoria(coin_ids: list[str]) -> dict[str, dict]:
    """Busca TVL de múltiplos protocolos para comparação de peers."""
    resultado = {}
    for cid in coin_ids:
        dados = buscar_tvl(cid)
        fees  = buscar_fees_revenue(cid)
        resultado[cid] = {**dados, **fees}
    return resultado