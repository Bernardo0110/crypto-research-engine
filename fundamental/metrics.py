import numpy as np
import pandas as pd
from data.field_mapper import normalizar_peers
from fundamental.pillars.tokenomics      import calcular_tokenomics
from fundamental.pillars.adoption        import calcular_adoption
from fundamental.pillars.onchain         import calcular_onchain
from fundamental.pillars.protocol_revenue import calcular_protocol_revenue
from fundamental.pillars.valuation       import calcular_valuation
from fundamental.pillars.developer       import calcular_developer


def calcular_todos_pilares(dados: dict) -> dict:
    """
    Orquestra os 6 pilares fundamentalistas para o ativo principal.
    Retorna dict com resultados de cada pilar + DataFrame de peers normalizado.
    """
    coin_id        = dados["coin_id"]
    dados_mercado  = dados["dados_mercado"]
    market_peers   = dados["market_peers"]
    defillama_peers = dados["defillama_peers"]
    github_peers   = dados["github_peers"]
    onchain        = dados["onchain"]
    macro          = dados["macro"]

    # DataFrame consolidado de peers
    df_peers = normalizar_peers(market_peers, defillama_peers, github_peers)

    # Garante que o próprio ativo está no df_peers
    if coin_id not in df_peers.index and dados_mercado:
        from data.field_mapper import (fdv_mcap_ratio, volume_mcap_ratio,
                                        taxa_inflacao_supply, mcap_tvl_ratio,
                                        fdv_revenue_ratio)
        dl = defillama_peers.get(coin_id, {})
        gh = github_peers.get(coin_id, {})
        df_peers.loc[coin_id] = {
            "nome":              dados_mercado.get("nome", coin_id),
            "simbolo":           dados_mercado.get("simbolo", ""),
            "mcap_usd":          dados_mercado.get("mcap_usd", np.nan),
            "volume_24h":        dados_mercado.get("volume_24h", np.nan),
            "fdv_usd":           dados_mercado.get("fdv_usd", np.nan),
            "supply_circulante": dados_mercado.get("supply_circulante", np.nan),
            "supply_total":      dados_mercado.get("supply_total", np.nan),
            "supply_maximo":     dados_mercado.get("supply_maximo", np.nan),
            "variacao_30d":      dados_mercado.get("variacao_30d", np.nan),
            "rank_mercado":      dados_mercado.get("rank_mercado", np.nan),
            "fdv_mcap":          fdv_mcap_ratio(dados_mercado),
            "volume_mcap":       volume_mcap_ratio(dados_mercado),
            "inflacao_supply":   taxa_inflacao_supply(dados_mercado),
            "tvl_usd":           dl.get("tvl_usd", np.nan),
            "fees_30d":          dl.get("fees_30d", np.nan),
            "revenue_30d":       dl.get("revenue_30d", np.nan),
            "mcap_tvl":          mcap_tvl_ratio(dados_mercado, dl),
            "fdv_revenue":       fdv_revenue_ratio(dados_mercado, dl),
            "github_stars":      gh.get("github_stars", np.nan),
            "github_commits_4s": gh.get("github_commits_4s", np.nan),
            "github_contributors": gh.get("github_contributors", np.nan),
        }

    pilares = {
        "tokenomics":       calcular_tokenomics(coin_id, df_peers),
        "adoption":         calcular_adoption(coin_id, df_peers, macro),
        "onchain":          calcular_onchain(coin_id, onchain, dados_mercado),
        "protocol_revenue": calcular_protocol_revenue(coin_id, df_peers, dados_mercado),
        "valuation":        calcular_valuation(coin_id, df_peers),
        "developer":        calcular_developer(coin_id, github_peers),
    }

    # Registra quais pilares têm dados suficientes
    pilares_ativos = {k: v for k, v in pilares.items() if v}
    pilares_ausentes = [k for k, v in pilares.items() if not v]

    if pilares_ausentes:
        print(f"[fundamental] Pilares sem dados: {pilares_ausentes}")

    return {
        "pilares":         pilares,
        "pilares_ativos":  list(pilares_ativos.keys()),
        "pilares_ausentes": pilares_ausentes,
        "df_peers":        df_peers,
    }