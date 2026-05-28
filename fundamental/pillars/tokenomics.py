import numpy as np
from data.field_mapper import fdv_mcap_ratio, taxa_inflacao_supply


def calcular_tokenomics(coin_id: str, df_peers) -> dict:
    """
    Pilar Tokenomics — avalia estrutura de supply e pressão de diluição.
    df_peers: DataFrame normalizado de peers (saída de field_mapper.normalizar_peers).
    """
    if coin_id not in df_peers.index:
        return {}

    row = df_peers.loc[coin_id]

    fdv_mcap       = row.get("fdv_mcap", np.nan)
    inflacao       = row.get("inflacao_supply", np.nan)
    supply_maximo  = row.get("supply_maximo", np.nan)
    supply_circ    = row.get("supply_circulante", np.nan)
    supply_total   = row.get("supply_total", np.nan)

    # Supply cap: se supply_maximo existir, calcula % já emitida
    pct_emitido = np.nan
    if not np.isnan(supply_maximo) and supply_maximo > 0:
        pct_emitido = supply_circ / supply_maximo

    return {
        "fdv_mcap_ratio":    fdv_mcap,
        "inflacao_supply":   inflacao,
        "supply_maximo":     supply_maximo,
        "pct_supply_emitido": pct_emitido,
        "supply_cap_existe": not np.isnan(supply_maximo),
    }