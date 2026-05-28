"""
config/settings.py
Configurações globais do projeto.
Edite apenas este arquivo para trocar o ativo analisado.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Ativo e benchmark ────────────────────────────────────────
ATIVO     = "ethereum"   # ID no CoinGecko (ex: "bitcoin", "solana")
SIMBOLO   = "ETH"        # Símbolo do ativo
BENCHMARK = "bitcoin"    # Benchmark (sempre BTC para crypto)

# ── Períodos analisados pelo módulo quant ────────────────────
# Crypto opera 24/7/365 — usar 365 dias, não 252
PERIODOS = {
    "1 Ano":  "1y",
    "2 Anos": "2y",
}

# ── Taxa livre de risco ──────────────────────────────────────
# Crypto é precificado em USD → usar Fed Funds Rate
# Fallback caso API do Fed esteja indisponível
RF_FALLBACK = 0.045   # 4.5% a.a.

# ── Paleta de cores ──────────────────────────────────────────
COR_DESTAQUE = "#1A5276"
COR_PEERS    = "#AAB7B8"
COR_BM       = "#E74C3C"
COR_FUNDO    = "#F8F9FA"
COR_GRID     = "#DEE2E6"

# ── Tiers de market cap (USD) ────────────────────────────────
TIER_LARGE = 10_000_000_000   # > USD 10B → Large Cap
TIER_MID   =  1_000_000_000   # USD 1B–10B → Mid Cap
                               # abaixo     → Small Cap

# ── API Keys ─────────────────────────────────────────────────
COINGECKO_DEMO_KEY = os.getenv("COINGECKO_DEMO_KEY", "")
ETHERSCAN_API_KEY  = os.getenv("ETHERSCAN_API_KEY", "")
GITHUB_TOKEN       = os.getenv("GITHUB_TOKEN", "")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY", "")
TOKENOMIST_API_KEY = os.getenv("TOKENOMIST_API_KEY", "")

# ── Dias de análise crypto ───────────────────────────────────
DIAS_ANO = 365   # crypto opera 24/7 — não usar 252