import requests
import numpy as np
import pandas as pd
from pytrends.request import TrendReq
from config.mappings import API_URLS, API_TIMEOUTS, HALVINGS, FASES_HALVING
from config.settings import ATIVO


# ─── Fear & Greed (Alternative.me) ───────────────────────────────────────────

def buscar_fear_greed(dias: int = 30) -> dict:
    """Retorna Fear & Greed Index atual e histórico dos últimos `dias` dias."""
    url = f"{API_URLS['fear_greed']}?limit={dias}"
    try:
        r = requests.get(url, timeout=API_TIMEOUTS["fear_greed"])
        r.raise_for_status()
        dados = r.json().get("data", [])
        if not dados:
            return {}
        atual = dados[0]
        valores = [int(d["value"]) for d in dados]
        return {
            "fear_greed_atual":       int(atual["value"]),
            "fear_greed_label":       atual["value_classification"],
            "fear_greed_media_30d":   float(np.mean(valores)),
            "fear_greed_min_30d":     float(np.min(valores)),
            "fear_greed_max_30d":     float(np.max(valores)),
        }
    except Exception as e:
        print(f"[fear_greed] buscar_fear_greed: {e}")
        return {}


# ─── BTC Dominance (CoinGecko global) ────────────────────────────────────────

def buscar_btc_dominance() -> dict:
    """Retorna dominância do BTC e ETH no mercado global."""
    url = f"{API_URLS['coingecko']}/global"
    try:
        r = requests.get(url, timeout=API_TIMEOUTS["coingecko"])
        r.raise_for_status()
        d = r.json().get("data", {})
        domins = d.get("market_cap_percentage", {})
        return {
            "btc_dominance":        domins.get("btc", np.nan),
            "eth_dominance":        domins.get("eth", np.nan),
            "mcap_total_usd":       d.get("total_market_cap", {}).get("usd", np.nan),
            "volume_total_24h":     d.get("total_volume", {}).get("usd", np.nan),
            "num_moedas_ativas":    d.get("active_cryptocurrencies", np.nan),
        }
    except Exception as e:
        print(f"[macro] buscar_btc_dominance: {e}")
        return {}


# ─── Funding Rates & Open Interest (OKX public) ───────────────────────────────

# Mapeamento coin_id CoinGecko → símbolo OKX (perpetual swap)
COINGECKO_PARA_OKX = {
    "bitcoin":           "BTC-USD-SWAP",
    "ethereum":          "ETH-USD-SWAP",
    "solana":            "SOL-USD-SWAP",
    "binancecoin":       "BNB-USD-SWAP",
    "ripple":            "XRP-USD-SWAP",
    "cardano":           "ADA-USD-SWAP",
    "avalanche-2":       "AVAX-USD-SWAP",
    "chainlink":         "LINK-USD-SWAP",
    "polkadot":          "DOT-USD-SWAP",
    "uniswap":           "UNI-USD-SWAP",
    "near":              "NEAR-USD-SWAP",
    "aptos":             "APT-USD-SWAP",
    "sui":               "SUI-USD-SWAP",
    "hyperliquid":       "HYPE-USD-SWAP",
}


def buscar_funding_rate(coin_id: str) -> dict:
    """Retorna funding rate atual e open interest via OKX (sem autenticação)."""
    instId = COINGECKO_PARA_OKX.get(coin_id)
    if not instId:
        return {}

    resultado = {}

    # Funding rate atual
    url_fr = f"{API_URLS['okx']}/public/funding-rate"
    try:
        r = requests.get(url_fr, params={"instId": instId}, timeout=API_TIMEOUTS["okx"])
        r.raise_for_status()
        dados = r.json().get("data", [{}])[0]
        resultado["funding_rate_atual"] = float(dados.get("fundingRate", np.nan))
        resultado["funding_rate_previsto"] = float(dados.get("nextFundingRate", np.nan))
    except Exception as e:
        print(f"[okx] funding_rate({coin_id}): {e}")
        resultado["funding_rate_atual"]    = np.nan
        resultado["funding_rate_previsto"] = np.nan

    # Open interest
    url_oi = f"{API_URLS['okx']}/public/open-interest"
    try:
        r = requests.get(url_oi, params={"instId": instId}, timeout=API_TIMEOUTS["okx"])
        r.raise_for_status()
        dados = r.json().get("data", [{}])[0]
        resultado["open_interest_usd"] = float(dados.get("oiUsd", np.nan))
    except Exception as e:
        print(f"[okx] open_interest({coin_id}): {e}")
        resultado["open_interest_usd"] = np.nan

    # Long/Short ratio
    url_ls = f"{API_URLS['okx']}/rubik/stat/contracts/long-short-account-ratio"
    try:
        r = requests.get(url_ls, params={"ccy": instId.split("-")[0], "period": "1D"},
                         timeout=API_TIMEOUTS["okx"])
        r.raise_for_status()
        dados = r.json().get("data", [])
        if dados:
            resultado["long_short_ratio"] = float(dados[0][1])
        else:
            resultado["long_short_ratio"] = np.nan
    except Exception as e:
        print(f"[okx] long_short_ratio({coin_id}): {e}")
        resultado["long_short_ratio"] = np.nan

    return resultado


# ─── Google Trends (pytrends) ─────────────────────────────────────────────────

def buscar_google_trends(termos: list[str], periodo: str = "today 3-m") -> dict:
    """
    Retorna interesse médio e tendência recente para os termos fornecidos.
    `periodo`: padrão pytrends — ex: 'today 3-m', 'today 12-m'.
    """
    try:
        pt = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        pt.build_payload(termos[:5], timeframe=periodo, geo="")
        df = pt.interest_over_time()
        if df.empty:
            return {}
        resultado = {}
        for termo in termos[:5]:
            if termo in df.columns:
                serie = df[termo]
                resultado[f"trends_{termo}_media"]   = float(serie.mean())
                resultado[f"trends_{termo}_atual"]   = float(serie.iloc[-1])
                resultado[f"trends_{termo}_pico"]    = float(serie.max())
                # tendência: comparação última semana vs 4 semanas anteriores
                if len(serie) >= 5:
                    resultado[f"trends_{termo}_tendencia"] = float(
                        serie.iloc[-1] - serie.iloc[-5:].mean()
                    )
        return resultado
    except Exception as e:
        print(f"[pytrends] buscar_google_trends: {e}")
        return {}


# ─── Halving Cycle (calculado internamente) ───────────────────────────────────

def calcular_posicao_halving() -> dict:
    """
    Calcula a posição atual no ciclo de halving do Bitcoin.
    Zero custo — sem chamadas externas.
    """
    from datetime import datetime
    hoje = datetime.today()
    halvings_passados = [h for h in HALVINGS if h <= hoje]
    if not halvings_passados:
        return {}

    ultimo_halving = max(halvings_passados)
    idx = HALVINGS.index(ultimo_halving)

    # Próximo halving (se existir na lista)
    proximo_halving = HALVINGS[idx + 1] if idx + 1 < len(HALVINGS) else None

    dias_desde_halving = (hoje - ultimo_halving).days
    dias_ciclo = (proximo_halving - ultimo_halving).days if proximo_halving else 1458  # ~4 anos
    pct_ciclo = dias_desde_halving / dias_ciclo

    # Fase baseada em percentual do ciclo (FASES_HALVING é lista ordenada por pct_min crescente)
    fase = FASES_HALVING[0][1]
    for pct_min, label, _cor, _desc in FASES_HALVING:
        if pct_ciclo >= pct_min:
            fase = label

    return {
        "halving_numero":         idx + 1,
        "ultimo_halving":         ultimo_halving.strftime("%Y-%m-%d"),
        "proximo_halving":        proximo_halving.strftime("%Y-%m-%d") if proximo_halving else "N/D",
        "dias_desde_halving":     dias_desde_halving,
        "pct_ciclo_completo":     round(pct_ciclo * 100, 1),
        "fase_ciclo":             fase,
    }


# ─── Orquestrador macro ───────────────────────────────────────────────────────

def buscar_macro_completo(coin_id: str, termos_trends: list[str] | None = None) -> dict:
    """Agrega todas as métricas macro em um único dict."""
    termos = termos_trends or [coin_id]
    return {
        **buscar_fear_greed(),
        **buscar_btc_dominance(),
        **buscar_funding_rate(coin_id),
        **buscar_google_trends(termos),
        **calcular_posicao_halving(),
    }