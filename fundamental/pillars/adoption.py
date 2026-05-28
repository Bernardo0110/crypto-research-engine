import numpy as np


def calcular_adoption(coin_id: str, df_peers, macro: dict) -> dict:
    """
    Pilar Adoção — volume relativo, liquidez e interesse de busca.
    macro: dict retornado por macro_provider (contém trends_*).
    """
    if coin_id not in df_peers.index:
        return {}

    row = df_peers.loc[coin_id]

    volume_mcap = row.get("volume_mcap", np.nan)
    rank        = row.get("rank_mercado", np.nan)

    # Google Trends — busca pelo coin_id e nome
    trends_keys = [k for k in macro if k.startswith("trends_") and k.endswith("_media")]
    trends_media = float(np.nanmean([macro[k] for k in trends_keys])) if trends_keys else np.nan
    trends_atual_keys = [k for k in macro if k.startswith("trends_") and k.endswith("_atual")]
    trends_atual = float(np.nanmean([macro[k] for k in trends_atual_keys])) if trends_atual_keys else np.nan

    return {
        "volume_mcap_ratio":  volume_mcap,
        "rank_mercado":       rank,
        "trends_media_3m":    trends_media,
        "trends_atual":       trends_atual,
    }