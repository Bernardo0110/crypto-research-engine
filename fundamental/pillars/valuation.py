import numpy as np


def calcular_valuation(coin_id: str, df_peers) -> dict:
    """
    Pilar Valuation — múltiplos de mercado relativos ao peer set.
    Scores calculados em fundamental/scoring.py por percentil.
    """
    if coin_id not in df_peers.index:
        return {}

    row = df_peers.loc[coin_id]

    mcap       = row.get("mcap_usd", np.nan)
    fdv        = row.get("fdv_usd", np.nan)
    volume     = row.get("volume_24h", np.nan)
    tvl        = row.get("tvl_usd", np.nan)
    revenue_30d = row.get("revenue_30d", np.nan)

    # MCap / Volume 24h — dias de volume para "comprar" o mcap
    mcap_volume = np.nan
    if not np.isnan(mcap) and not np.isnan(volume) and volume > 0:
        mcap_volume = mcap / volume

    # FDV / MCap — múltiplo de diluição futura
    fdv_mcap = row.get("fdv_mcap", np.nan)

    # MCap / TVL (DeFi)
    mcap_tvl = row.get("mcap_tvl", np.nan)

    # FDV / Revenue anualizado (DeFi)
    fdv_revenue = row.get("fdv_revenue", np.nan)

    return {
        "mcap_usd":         mcap,
        "fdv_usd":          fdv,
        "mcap_volume_ratio": mcap_volume,
        "fdv_mcap_ratio":   fdv_mcap,
        "mcap_tvl_ratio":   mcap_tvl,
        "fdv_revenue_ratio": fdv_revenue,
    }