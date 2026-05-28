import numpy as np
import pandas as pd


def fdv_mcap_ratio(dados_mercado: dict) -> float:
    """FDV / MCap — pressão de diluição futura. Quanto maior, mais diluição."""
    fdv  = dados_mercado.get("fdv_usd", np.nan)
    mcap = dados_mercado.get("mcap_usd", np.nan)
    if np.isnan(fdv) or np.isnan(mcap) or mcap == 0:
        return np.nan
    return fdv / mcap


def taxa_inflacao_supply(dados_mercado: dict) -> float:
    """
    Estimativa de inflação anual do supply:
    (supply_total - supply_circulante) / supply_circulante.
    Retorna np.nan se supply_maximo for None (supply ilimitado não penalizado aqui).
    """
    circ  = dados_mercado.get("supply_circulante", np.nan)
    total = dados_mercado.get("supply_total", np.nan)
    if np.isnan(circ) or np.isnan(total) or circ == 0:
        return np.nan
    return (total - circ) / circ


def volume_mcap_ratio(dados_mercado: dict) -> float:
    """Volume 24h / MCap — proxy de liquidez relativa."""
    vol  = dados_mercado.get("volume_24h", np.nan)
    mcap = dados_mercado.get("mcap_usd", np.nan)
    if np.isnan(vol) or np.isnan(mcap) or mcap == 0:
        return np.nan
    return vol / mcap


def pct_supply_em_staking(onchain: dict, dados_mercado: dict) -> float:
    """% do supply circulante que está em staking (só ETH por ora)."""
    staked = onchain.get("eth_staked", np.nan)
    circ   = dados_mercado.get("supply_circulante", np.nan)
    if np.isnan(staked) or np.isnan(circ) or circ == 0:
        return np.nan
    return staked / circ


def nvt_ratio(onchain: dict, dados_mercado: dict) -> float:
    """
    NVT = MCap / Volume On-Chain diário estimado.
    Só disponível para BTC (tx_volume_usd vem do Blockchain.info).
    """
    mcap       = dados_mercado.get("mcap_usd", np.nan)
    vol_onchain = onchain.get("tx_volume_usd", np.nan)
    if np.isnan(mcap) or np.isnan(vol_onchain) or vol_onchain == 0:
        return np.nan
    return mcap / vol_onchain


def mcap_tvl_ratio(dados_mercado: dict, defillama: dict) -> float:
    """MCap / TVL — valuation relativo para protocolos DeFi."""
    mcap = dados_mercado.get("mcap_usd", np.nan)
    tvl  = defillama.get("tvl_usd", np.nan)
    if np.isnan(mcap) or np.isnan(tvl) or tvl == 0:
        return np.nan
    return mcap / tvl


def fdv_revenue_ratio(dados_mercado: dict, defillama: dict) -> float:
    """FDV / Revenue anualizado — equivalente ao P/S para DeFi."""
    fdv        = dados_mercado.get("fdv_usd", np.nan)
    revenue_30d = defillama.get("revenue_30d", np.nan)
    if np.isnan(fdv) or np.isnan(revenue_30d) or revenue_30d == 0:
        return np.nan
    revenue_anual = revenue_30d * 12
    return fdv / revenue_anual


def normalizar_peers(market_peers: dict, defillama_peers: dict,
                     github_peers: dict) -> pd.DataFrame:
    """
    Consolida dados de todos os peers em um DataFrame.
    Cada linha é um coin; colunas são métricas normalizadas.
    Campos ausentes ficam como np.nan.
    """
    registros = []
    todos_coins = set(market_peers) | set(defillama_peers) | set(github_peers)

    for cid in todos_coins:
        md  = market_peers.get(cid, {})
        dl  = defillama_peers.get(cid, {})
        gh  = github_peers.get(cid, {})

        registros.append({
            "coin_id":          cid,
            "nome":             md.get("nome", cid),
            "simbolo":          md.get("simbolo", ""),
            "mcap_usd":         md.get("mcap_usd", np.nan),
            "volume_24h":       md.get("volume_24h", np.nan),
            "fdv_usd":          md.get("fdv_usd", np.nan),
            "supply_circulante":md.get("supply_circulante", np.nan),
            "supply_total":     md.get("supply_total", np.nan),
            "supply_maximo":    md.get("supply_maximo", np.nan),
            "variacao_30d":     md.get("variacao_30d", np.nan),
            "rank_mercado":     md.get("rank_mercado", np.nan),
            "fdv_mcap":         fdv_mcap_ratio(md),
            "volume_mcap":      volume_mcap_ratio(md),
            "inflacao_supply":  taxa_inflacao_supply(md),
            "tvl_usd":          dl.get("tvl_usd", np.nan),
            "fees_30d":         dl.get("fees_30d", np.nan),
            "revenue_30d":      dl.get("revenue_30d", np.nan),
            "mcap_tvl":         mcap_tvl_ratio(md, dl),
            "fdv_revenue":      fdv_revenue_ratio(md, dl),
            "github_stars":     gh.get("github_stars", np.nan),
            "github_commits_4s":gh.get("github_commits_4s", np.nan),
            "github_contributors": gh.get("github_contributors", np.nan),
        })

    df = pd.DataFrame(registros).set_index("coin_id")
    return df


def validar_dados_minimos(dados: dict) -> tuple[bool, list[str]]:
    """
    Verifica se o dict de dados tem o mínimo necessário para gerar o relatório.
    Retorna (ok, lista_de_avisos).
    """
    avisos = []

    if dados.get("historico_ativo", pd.Series(dtype=float)).empty:
        avisos.append("Histórico de preços indisponível — análise quantitativa impossível.")

    if not dados.get("dados_mercado"):
        avisos.append("Dados de mercado indisponíveis — relatório muito limitado.")

    if not dados.get("peers") or len(dados["peers"]) < 2:
        avisos.append("Peer set com menos de 2 coins — scoring por percentil inválido.")

    ok = len(avisos) == 0 or (
        not dados.get("historico_ativo", pd.Series(dtype=float)).empty
        and bool(dados.get("dados_mercado"))
    )
    return ok, avisos