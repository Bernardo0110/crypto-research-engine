import requests
import numpy as np
from config.settings import ETHERSCAN_API_KEY
from config.mappings import API_URLS, API_TIMEOUTS, BLOCKCHAIN_INFO_METRICS, ETHERSCAN_ENDPOINTS


# ─── Bitcoin (Blockchain.info) ────────────────────────────────────────────────

def buscar_onchain_btc() -> dict:
    """Busca métricas on-chain do Bitcoin via Blockchain.info."""
    resultado = {}
    for metrica, path in BLOCKCHAIN_INFO_METRICS.items():
        url = f"{API_URLS['blockchain_info']}/{path}"
        try:
            r = requests.get(url, timeout=API_TIMEOUTS["blockchain_info"])
            r.raise_for_status()
            valor = float(r.text.strip())
            resultado[metrica] = valor
        except Exception as e:
            print(f"[blockchain.info] {metrica}: {e}")
            resultado[metrica] = np.nan
    return resultado


def calcular_nvt_btc(dados_btc: dict, preco_btc: float) -> float:
    """
    NVT Ratio = MCap / Volume On-Chain (USD).
    Requer 'tx_volume_usd' no dict de dados BTC.
    """
    mcap = dados_btc.get("hash_rate")   # placeholder — mcap vem do CoinGecko
    vol_onchain = dados_btc.get("tx_volume_usd", np.nan)
    if np.isnan(vol_onchain) or vol_onchain == 0:
        return np.nan
    # mcap calculado: supply_circulante * preco (fornecido externamente)
    return np.nan  # calculado em metrics.py com dados completos


# ─── Ethereum (Etherscan V2) ──────────────────────────────────────────────────

def _etherscan_get(action: str, params_extra: dict = {}) -> dict:
    """Helper para chamadas Etherscan V2."""
    if not ETHERSCAN_API_KEY:
        return {}
    url = API_URLS["etherscan"]
    params = {
        "chainid": 1,
        "module":  ETHERSCAN_ENDPOINTS[action]["module"],
        "action":  ETHERSCAN_ENDPOINTS[action]["action"],
        "apikey":  ETHERSCAN_API_KEY,
        **params_extra,
    }
    try:
        r = requests.get(url, params=params, timeout=API_TIMEOUTS["etherscan"])
        r.raise_for_status()
        d = r.json()
        if d.get("status") == "1":
            return d.get("result", {})
        return {}
    except Exception as e:
        print(f"[etherscan] {action}: {e}")
        return {}


def buscar_onchain_eth() -> dict:
    """Busca métricas on-chain do Ethereum via Etherscan V2."""
    resultado = {}

    # Supply total ETH
    supply_raw = _etherscan_get("eth_supply")
    if supply_raw:
        try:
            resultado["eth_supply_total"] = int(supply_raw) / 1e18
        except Exception:
            resultado["eth_supply_total"] = np.nan
    else:
        resultado["eth_supply_total"] = np.nan

    # ETH em staking (Beacon Chain)
    staking_raw = _etherscan_get("eth2_validators")
    if staking_raw:
        try:
            eth_staked = sum(
                int(v.get("effectivebalance", 0)) for v in staking_raw
            ) / 1e9 if isinstance(staking_raw, list) else np.nan
            resultado["eth_staked"] = eth_staked
        except Exception:
            resultado["eth_staked"] = np.nan
    else:
        resultado["eth_staked"] = np.nan

    # Gas price médio
    gas_raw = _etherscan_get("gas_oracle")
    if isinstance(gas_raw, dict):
        try:
            resultado["gas_price_gwei"] = float(gas_raw.get("ProposeGasPrice", np.nan))
        except Exception:
            resultado["gas_price_gwei"] = np.nan
    else:
        resultado["gas_price_gwei"] = np.nan

    return resultado


# ─── Roteador por coin ────────────────────────────────────────────────────────

def buscar_onchain(coin_id: str) -> dict:
    """
    Retorna métricas on-chain disponíveis para o coin.
    BTC e ETH têm dados completos; outros coins retornam dict vazio.
    """
    if coin_id == "bitcoin":
        return buscar_onchain_btc()
    elif coin_id == "ethereum":
        return buscar_onchain_eth()
    else:
        return {}