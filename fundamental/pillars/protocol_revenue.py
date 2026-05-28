import numpy as np
from data.field_mapper import mcap_tvl_ratio, fdv_revenue_ratio


def calcular_protocol_revenue(coin_id: str, df_peers, dados_mercado: dict) -> dict:
    """
    Pilar Protocol Revenue — TVL, fees e revenue para protocolos DeFi.
    Retorna dict vazio para coins sem dados DeFiLlama (não-DeFi).
    """
    if coin_id not in df_peers.index:
        return {}

    row = df_peers.loc[coin_id]

    tvl        = row.get("tvl_usd", np.nan)
    fees_30d   = row.get("fees_30d", np.nan)
    revenue_30d = row.get("revenue_30d", np.nan)

    # Sem TVL → protocolo não indexado no DeFiLlama
    if np.isnan(tvl):
        return {}

    mcap_tvl   = row.get("mcap_tvl", np.nan)
    fdv_rev    = row.get("fdv_revenue", np.nan)

    # Fee margin: % do fees que fica como revenue do protocolo
    fee_margin = np.nan
    if not np.isnan(fees_30d) and fees_30d > 0 and not np.isnan(revenue_30d):
        fee_margin = revenue_30d / fees_30d

    return {
        "tvl_usd":          tvl,
        "fees_30d":         fees_30d,
        "revenue_30d":      revenue_30d,
        "fees_anualizados": fees_30d * 12 if not np.isnan(fees_30d) else np.nan,
        "revenue_anualizado": revenue_30d * 12 if not np.isnan(revenue_30d) else np.nan,
        "mcap_tvl_ratio":   mcap_tvl,
        "fdv_revenue_ratio": fdv_rev,
        "fee_margin":       fee_margin,
    }