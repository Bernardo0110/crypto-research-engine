import numpy as np
import pandas as pd
from config.mappings import PESOS_FUNDAMENTAL, LIMIARES_FUNDAMENTAL


def _percentil_peers(valor: float, serie: pd.Series,
                     quanto_maior_melhor: bool = True) -> float:
    """Score 0–10 por percentil dentro do peer set."""
    validos = serie.dropna()
    if validos.empty or np.isnan(valor):
        return np.nan
    percentil = (validos < valor).sum() / len(validos)
    return (percentil * 10) if quanto_maior_melhor else (10 - percentil * 10)


def _absoluto(valor: float, limiares: dict,
               quanto_maior_melhor: bool = True) -> float:
    """Score 0–10 por limiares fixos."""
    if np.isnan(valor):
        return np.nan
    breakpoints = sorted(limiares.items(), key=lambda x: x[1], reverse=True)
    for nome, threshold in breakpoints:
        if quanto_maior_melhor and valor >= threshold:
            return {"otimo": 10.0, "bom": 7.5, "neutro": 5.0, "fraco": 2.5}.get(nome, 0.0)
        if not quanto_maior_melhor and valor <= threshold:
            return {"otimo": 10.0, "bom": 7.5, "neutro": 5.0, "fraco": 2.5}.get(nome, 0.0)
    return 0.0


# ── Tokenomics ────────────────────────────────────────────────────────────────

def score_tokenomics(pilar: dict, df_peers: pd.DataFrame) -> dict:
    scores = {}

    # FDV/MCap: menor é melhor (menos pressão de diluição)
    fdv_mcap = pilar.get("fdv_mcap_ratio", np.nan)
    scores["score_fdv_mcap"] = _percentil_peers(
        fdv_mcap, df_peers["fdv_mcap"].dropna(), quanto_maior_melhor=False
    )

    # Inflação de supply: menor é melhor
    inflacao = pilar.get("inflacao_supply", np.nan)
    scores["score_inflacao"] = _percentil_peers(
        inflacao, df_peers["inflacao_supply"].dropna(), quanto_maior_melhor=False
    )

    # Supply cap: bônus fixo se existir cap
    scores["score_supply_cap"] = 7.5 if pilar.get("supply_cap_existe") else 4.0

    validos = [v for v in scores.values() if not np.isnan(v)]
    scores["score_tokenomics"] = round(np.mean(validos), 2) if validos else np.nan
    return scores


# ── Adoption ──────────────────────────────────────────────────────────────────

def score_adoption(pilar: dict, df_peers: pd.DataFrame) -> dict:
    scores = {}

    # Volume/MCap: maior é melhor (mais liquidez)
    vol_mcap = pilar.get("volume_mcap_ratio", np.nan)
    scores["score_volume_mcap"] = _percentil_peers(
        vol_mcap, df_peers["volume_mcap"].dropna(), quanto_maior_melhor=True
    )

    # Rank de mercado: menor rank (número menor) é melhor
    rank = pilar.get("rank_mercado", np.nan)
    scores["score_rank"] = _percentil_peers(
        rank, df_peers["rank_mercado"].dropna(), quanto_maior_melhor=False
    )

    # Google Trends: maior é melhor
    trends = pilar.get("trends_media_3m", np.nan)
    scores["score_trends"] = _absoluto(
        trends, LIMIARES_FUNDAMENTAL.get("trends", {"otimo": 70, "bom": 40, "neutro": 20, "fraco": 10})
    )

    validos = [v for v in scores.values() if not np.isnan(v)]
    scores["score_adoption"] = round(np.mean(validos), 2) if validos else np.nan
    return scores


# ── On-Chain ──────────────────────────────────────────────────────────────────

def score_onchain(pilar: dict, coin_id: str) -> dict:
    if not pilar:
        return {"score_onchain": np.nan}

    scores = {}

    if coin_id == "bitcoin":
        hash_rate = pilar.get("hash_rate", np.nan)
        scores["score_hash_rate"] = _absoluto(
            hash_rate,
            LIMIARES_FUNDAMENTAL.get("btc_hash_rate",
                {"otimo": 600e18, "bom": 400e18, "neutro": 200e18, "fraco": 100e18})
        )
        nvt = pilar.get("nvt_ratio", np.nan)
        # NVT: menor pode ser subvalorizado (melhor), maior pode ser sobrevalorizado
        scores["score_nvt"] = _absoluto(
            nvt,
            LIMIARES_FUNDAMENTAL.get("nvt", {"otimo": 0, "bom": 30, "neutro": 60, "fraco": 100}),
            quanto_maior_melhor=False
        )

    elif coin_id == "ethereum":
        pct_staked = pilar.get("pct_staked", np.nan)
        scores["score_staking"] = _absoluto(
            pct_staked if not np.isnan(pct_staked) else np.nan,
            LIMIARES_FUNDAMENTAL.get("eth_staking_pct",
                {"otimo": 0.28, "bom": 0.22, "neutro": 0.16, "fraco": 0.10})
        )

    validos = [v for v in scores.values() if not np.isnan(v)]
    scores["score_onchain"] = round(np.mean(validos), 2) if validos else np.nan
    return scores


# ── Protocol Revenue ──────────────────────────────────────────────────────────

def score_protocol_revenue(pilar: dict, df_peers: pd.DataFrame) -> dict:
    if not pilar:
        return {"score_protocol_revenue": np.nan}

    scores = {}

    # MCap/TVL: menor é melhor (mais barato em relação ao TVL)
    mcap_tvl = pilar.get("mcap_tvl_ratio", np.nan)
    scores["score_mcap_tvl"] = _percentil_peers(
        mcap_tvl, df_peers["mcap_tvl"].dropna(), quanto_maior_melhor=False
    )

    # FDV/Revenue: menor é melhor (mais barato vs receita)
    fdv_rev = pilar.get("fdv_revenue_ratio", np.nan)
    scores["score_fdv_revenue"] = _percentil_peers(
        fdv_rev, df_peers["fdv_revenue"].dropna(), quanto_maior_melhor=False
    )

    # Fee margin: maior é melhor (protocolo retém mais das fees)
    fee_margin = pilar.get("fee_margin", np.nan)
    scores["score_fee_margin"] = _absoluto(
        fee_margin,
        LIMIARES_FUNDAMENTAL.get("fee_margin",
            {"otimo": 0.5, "bom": 0.3, "neutro": 0.15, "fraco": 0.05})
    )

    validos = [v for v in scores.values() if not np.isnan(v)]
    scores["score_protocol_revenue"] = round(np.mean(validos), 2) if validos else np.nan
    return scores


# ── Valuation ─────────────────────────────────────────────────────────────────

def score_valuation(pilar: dict, df_peers: pd.DataFrame) -> dict:
    scores = {}

    fdv_mcap = pilar.get("fdv_mcap_ratio", np.nan)
    scores["score_fdv_mcap_val"] = _percentil_peers(
        fdv_mcap, df_peers["fdv_mcap"].dropna(), quanto_maior_melhor=False
    )

    # MCap/Volume: menor é melhor (mais liquidez relativa)
    mcap_vol = pilar.get("mcap_volume_ratio", np.nan)
    if not np.isnan(mcap_vol):
        scores["score_mcap_volume"] = _absoluto(
            mcap_vol,
            LIMIARES_FUNDAMENTAL.get("mcap_volume",
                {"otimo": 5, "bom": 15, "neutro": 30, "fraco": 60}),
            quanto_maior_melhor=False
        )

    validos = [v for v in scores.values() if not np.isnan(v)]
    scores["score_valuation"] = round(np.mean(validos), 2) if validos else np.nan
    return scores


# ── Developer ─────────────────────────────────────────────────────────────────

def score_developer(pilar: dict, df_peers: pd.DataFrame) -> dict:
    if not pilar:
        return {"score_developer": np.nan}

    scores = {}

    commits_4s = pilar.get("github_commits_4s", np.nan)
    scores["score_commits"] = _percentil_peers(
        commits_4s, df_peers["github_commits_4s"].dropna(), quanto_maior_melhor=True
    )

    contributors = pilar.get("github_contributors", np.nan)
    scores["score_contributors"] = _percentil_peers(
        contributors, df_peers["github_contributors"].dropna(), quanto_maior_melhor=True
    )

    aceleracao = pilar.get("github_aceleracao", np.nan)
    scores["score_aceleracao"] = _absoluto(
        aceleracao,
        LIMIARES_FUNDAMENTAL.get("dev_aceleracao",
            {"otimo": 1.5, "bom": 1.1, "neutro": 0.9, "fraco": 0.6})
    )

    validos = [v for v in scores.values() if not np.isnan(v)]
    scores["score_developer"] = round(np.mean(validos), 2) if validos else np.nan
    return scores


# ── Agregador final ───────────────────────────────────────────────────────────

def calcular_score_fundamental(resultado_pilares: dict,
                                df_peers: pd.DataFrame,
                                coin_id: str) -> dict:
    """
    Calcula scores de todos os pilares e agrega no score fundamentalista final.
    Pesos redistribuídos proporcionalmente para pilares ausentes.
    """
    pilares = resultado_pilares["pilares"]

    scores_pilares = {
        **score_tokenomics(pilares["tokenomics"], df_peers),
        **score_adoption(pilares["adoption"], df_peers),
        **score_onchain(pilares["onchain"], coin_id),
        **score_protocol_revenue(pilares["protocol_revenue"], df_peers),
        **score_valuation(pilares["valuation"], df_peers),
        **score_developer(pilares["developer"], df_peers),
    }

    mapa_pilar_score = {
        "tokenomics":       "score_tokenomics",
        "adoption":         "score_adoption",
        "onchain":          "score_onchain",
        "protocol_revenue": "score_protocol_revenue",
        "valuation":        "score_valuation",
        "developer":        "score_developer",
    }

    peso_total = 0.0
    score_ponderado = 0.0

    for pilar, chave_score in mapa_pilar_score.items():
        peso = PESOS_FUNDAMENTAL.get(pilar, 0.0)
        s = scores_pilares.get(chave_score, np.nan)
        if not np.isnan(s):
            score_ponderado += s * peso
            peso_total += peso

    score_final = round(score_ponderado / peso_total, 2) if peso_total > 0 else np.nan

    return {
        **scores_pilares,
        "score_fundamental": score_final,
    }