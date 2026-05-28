import numpy as np
from data.field_mapper import nvt_ratio, pct_supply_em_staking


def calcular_onchain(coin_id: str, onchain: dict, dados_mercado: dict) -> dict:
    """
    Pilar On-Chain — métricas específicas por blockchain.
    Dados disponíveis: BTC completo, ETH parcial, outros vazio.
    """
    if not onchain:
        return {}

    resultado = {}

    if coin_id == "bitcoin":
        resultado = {
            "hash_rate":          onchain.get("hash_rate", np.nan),
            "active_addresses":   onchain.get("active_addresses", np.nan),
            "tx_count":           onchain.get("tx_count", np.nan),
            "tx_volume_usd":      onchain.get("tx_volume_usd", np.nan),
            "nvt_ratio":          nvt_ratio(onchain, dados_mercado),
            "mempool_size":       onchain.get("mempool_size", np.nan),
            "avg_block_size":     onchain.get("avg_block_size", np.nan),
            "miners_revenue":     onchain.get("miners_revenue", np.nan),
        }

    elif coin_id == "ethereum":
        resultado = {
            "eth_supply_total":   onchain.get("eth_supply_total", np.nan),
            "eth_staked":         onchain.get("eth_staked", np.nan),
            "pct_staked":         pct_supply_em_staking(onchain, dados_mercado),
            "gas_price_gwei":     onchain.get("gas_price_gwei", np.nan),
        }

    return resultado