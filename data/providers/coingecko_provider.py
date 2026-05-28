import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from config.settings import COINGECKO_DEMO_KEY, TOKENOMIST_API_KEY
from config.mappings import API_URLS, API_TIMEOUTS, CATEGORY_PEERS, CATEGORY_TO_KEY

HEADERS_CG = {"x-cg-demo-api-key": COINGECKO_DEMO_KEY} if COINGECKO_DEMO_KEY else {}


def buscar_dados_mercado(coin_id: str) -> dict:
    """Retorna preço, mcap, volume, fdv, supply e metadados do coin."""
    url = f"{API_URLS['coingecko']}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "false",
        "developer_data": "false",
    }
    try:
        r = requests.get(url, headers=HEADERS_CG, params=params, timeout=API_TIMEOUTS["coingecko"])
        r.raise_for_status()
        d = r.json()
        md = d.get("market_data", {})
        return {
            "nome":                  d.get("name", coin_id),
            "simbolo":               d.get("symbol", "").upper(),
            "categorias":            d.get("categories", []),
            "descricao":             d.get("description", {}).get("en", ""),
            "homepage":              (d.get("links", {}).get("homepage") or [""])[0],
            "genesis_date":          d.get("genesis_date"),
            "preco_usd":             md.get("current_price", {}).get("usd", np.nan),
            "mcap_usd":              md.get("market_cap", {}).get("usd", np.nan),
            "volume_24h":            md.get("total_volume", {}).get("usd", np.nan),
            "fdv_usd":               md.get("fully_diluted_valuation", {}).get("usd", np.nan),
            "supply_circulante":     md.get("circulating_supply", np.nan),
            "supply_total":          md.get("total_supply", np.nan),
            "supply_maximo":         md.get("max_supply", np.nan),
            "variacao_24h":          md.get("price_change_percentage_24h", np.nan),
            "variacao_7d":           md.get("price_change_percentage_7d", np.nan),
            "variacao_30d":          md.get("price_change_percentage_30d", np.nan),
            "ath_usd":               md.get("ath", {}).get("usd", np.nan),
            "ath_data":              md.get("ath_date", {}).get("usd"),
            "atl_usd":               md.get("atl", {}).get("usd", np.nan),
            "rank_mercado":          md.get("market_cap_rank", np.nan),
            "coingecko_score":       d.get("coingecko_score", np.nan),
        }
    except Exception as e:
        print(f"[coingecko] buscar_dados_mercado({coin_id}): {e}")
        return {}


def buscar_historico_precos(coin_id: str, dias: int = 365) -> pd.Series:
    """Retorna série diária de preços de fechamento (USD) dos últimos `dias` dias."""
    url = f"{API_URLS['coingecko']}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": dias, "interval": "daily"}
    try:
        r = requests.get(url, headers=HEADERS_CG, params=params, timeout=API_TIMEOUTS["coingecko"])
        r.raise_for_status()
        precos = r.json().get("prices", [])
        if not precos:
            return pd.Series(dtype=float)
        df = pd.DataFrame(precos, columns=["timestamp_ms", "preco"])
        df["data"] = pd.to_datetime(df["timestamp_ms"], unit="ms").dt.normalize()
        df = df.drop_duplicates("data").set_index("data")["preco"]
        return df.sort_index()
    except Exception as e:
        print(f"[coingecko] buscar_historico_precos({coin_id}, {dias}d): {e}")
        return pd.Series(dtype=float)


def buscar_categoria(coin_id: str) -> str | None:
    """Retorna a categoria principal do coin (primeira que existir em CATEGORY_PEERS)."""
    dados = buscar_dados_mercado(coin_id)
    categorias = dados.get("categorias", [])
    for cat in categorias:
        chave = CATEGORY_TO_KEY.get(cat)
        if chave and chave in CATEGORY_PEERS:
            return chave
    return None


def buscar_peers(coin_id: str, categoria: str | None = None) -> list[str]:
    """Retorna lista de coin IDs do peer set (inclui o próprio coin)."""
    if categoria is None:
        categoria = buscar_categoria(coin_id)
    if categoria is None:
        return [coin_id]
    peers = CATEGORY_PEERS.get(categoria, [coin_id])
    if coin_id not in peers:
        peers = [coin_id] + list(peers)
    return peers


def buscar_dados_mercado_batch(coin_ids: list[str]) -> dict[str, dict]:
    """Busca market data de múltiplos coins em uma única chamada (endpoint /coins/markets)."""
    url = f"{API_URLS['coingecko']}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coin_ids),
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d",
    }
    try:
        r = requests.get(url, headers=HEADERS_CG, params=params, timeout=API_TIMEOUTS["coingecko"])
        r.raise_for_status()
        resultado = {}
        for item in r.json():
            cid = item.get("id", "")
            resultado[cid] = {
                "nome":              item.get("name", cid),
                "simbolo":           (item.get("symbol") or "").upper(),
                "preco_usd":         item.get("current_price", np.nan),
                "mcap_usd":          item.get("market_cap", np.nan),
                "volume_24h":        item.get("total_volume", np.nan),
                "fdv_usd":           item.get("fully_diluted_valuation", np.nan),
                "supply_circulante": item.get("circulating_supply", np.nan),
                "supply_total":      item.get("total_supply", np.nan),
                "supply_maximo":     item.get("max_supply", np.nan),
                "variacao_24h":      item.get("price_change_percentage_24h", np.nan),
                "variacao_7d":       item.get("price_change_percentage_7d_in_currency", np.nan),
                "variacao_30d":      item.get("price_change_percentage_30d_in_currency", np.nan),
                "ath_usd":           item.get("ath", np.nan),
                "rank_mercado":      item.get("market_cap_rank", np.nan),
            }
        return resultado
    except Exception as e:
        print(f"[coingecko] buscar_dados_mercado_batch: {e}")
        return {}


def buscar_tokenomics_tokenomist(coin_id: str) -> dict:
    """
    Busca schedule de unlocks via Tokenomist.
    Requer TOKENOMIST_API_KEY — retorna dict vazio se ausente.
    """
    if not TOKENOMIST_API_KEY:
        return {}
    url = f"{API_URLS['tokenomist']}/tokens/{coin_id}/unlocks"
    headers = {"x-api-key": TOKENOMIST_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=API_TIMEOUTS.get("tokenomist", 10))
        r.raise_for_status()
        dados = r.json()
        proximo_unlock = dados.get("next_unlock", {})
        return {
            "unlock_proximo_data":     proximo_unlock.get("date"),
            "unlock_proximo_pct":      proximo_unlock.get("percentage_of_supply", np.nan),
            "unlock_12m_pct":          dados.get("unlock_next_12m_percentage", np.nan),
            "cliff_ativo":             dados.get("cliff_active", False),
        }
    except Exception as e:
        print(f"[tokenomist] buscar_tokenomics_tokenomist({coin_id}): {e}")
        return {}