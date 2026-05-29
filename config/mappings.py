"""
config/mappings.py
ÚNICA fonte de verdade para todos os mapeamentos estáticos do projeto.

Organização por domínio:
  I.   Categorias & peers      — categorias CoinGecko e peers por categoria
  II.  Fontes de dados         — URLs base e configurações de APIs
  III. On-chain                — métricas Blockchain.info e Etherscan
  IV.  Macro crypto            — drivers macro e sensibilidades
  V.   Notícias                — keywords por categoria
  VI.  Scoring                 — pesos, classificação e sinais
  VII. Halving                 — datas históricas e futuras

Ao editar este arquivo você altera o comportamento de toda a análise.
Não há outros arquivos de configuração estática no projeto.
"""

from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# I. CATEGORIAS & PEERS
# ─────────────────────────────────────────────────────────────────────────────

# Categorias CoinGecko → peers padrão
# Equivalente ao SECTOR_PEERS_B3 do projeto equity
CATEGORY_PEERS: dict[str, list[str]] = {
    "layer-1": [
        "bitcoin", "ethereum", "solana", "cardano",
        "avalanche-2", "polkadot", "near",
    ],
    "layer-2": [
        "matic-network", "arbitrum", "optimism",
        "base", "starknet", "zksync",
    ],
    "decentralized-finance-defi": [
        "uniswap", "aave", "curve-dao-token",
        "maker", "lido-dao", "compound-governance-token",
    ],
    "decentralized-exchange": [
        "uniswap", "curve-dao-token", "pancakeswap-token",
        "dydx", "jupiter-exchange-solana",
    ],
    "lending-borrowing": [
        "aave", "compound-governance-token", "maker",
        "morpho", "radiant-capital",
    ],
    "liquid-staking": [
        "lido-dao", "rocket-pool", "frax-ether",
        "staked-ether", "binance-staked-eth",
    ],
    "stablecoins": [
        "tether", "usd-coin", "dai", "frax", "true-usd",
    ],
    "gaming-nft": [
        "axie-infinity", "the-sandbox", "decentraland",
        "immutable-x", "gala",
    ],
    "real-world-assets-rwa": [
        "goldfinch", "centrifuge", "maple",
        "truefi", "credix-finance",
    ],
}

# Coins usados na rotação automática da sessão de melhorias — um por categoria
COINS_ROTACAO: list[str] = [
    "bitcoin",          # layer-1 (store of value)
    "ethereum",         # layer-1 (smart contract platform)
    "solana",           # layer-1 (high performance)
    "matic-network",    # layer-2
    "uniswap",          # DeFi / DEX
    "aave",             # lending
    "lido-dao",         # liquid staking
    "axie-infinity",    # gaming / NFT
]

# Mapeamento categoria CoinGecko → chave interna
CATEGORY_TO_KEY: dict[str, str] = {
    "layer-1":                      "layer1",
    "layer-2":                      "layer2",
    "smart-contract-platform":      "layer1",
    "decentralized-finance-defi":   "defi",
    "decentralized-exchange":       "dex",
    "lending-borrowing":            "lending",
    "liquid-staking":               "liquid_staking",
    "stablecoins":                  "stablecoins",
    "gaming-entertainment-and-nft": "gaming",
    "real-world-assets-rwa":        "rwa",
    "gaming-nft":                   "gaming",
}

# ─────────────────────────────────────────────────────────────────────────────
# II. FONTES DE DADOS
# ─────────────────────────────────────────────────────────────────────────────

# URLs base de cada provider
API_URLS: dict[str, str] = {
    "coingecko":      "https://api.coingecko.com/api/v3",
    "coingecko_pro":  "https://pro-api.coingecko.com/api/v3",
    "defillama":      "https://api.llama.fi",
    "defillama_fees": "https://api.llama.fi",
    "blockchain_info":"https://api.blockchain.info/charts",
    "etherscan":      "https://api.etherscan.io/v2/api",
    "github":         "https://api.github.com",
    "okx":            "https://www.okx.com/api/v5",
    "okx_public":     "https://www.okx.com/api/v5/public",
    "okx_rubik":      "https://www.okx.com/api/v5/rubik/stat",
    "fear_greed":     "https://api.alternative.me/fng/",
    "pytrends":       "https://trends.google.com",
    "tokenomist":     "https://api.tokenomist.ai",
    "google_news":    "https://news.google.com/rss/search",
}

# Timeout padrão por provider (segundos)
API_TIMEOUTS: dict[str, int] = {
    "coingecko":      15,
    "defillama":      45,   # lento para /protocol/{slug}
    "blockchain_info":15,
    "etherscan":      15,
    "github":         15,
    "okx_public":     10,
    "fear_greed":     10,
    "tokenomist":     15,
}

# ─────────────────────────────────────────────────────────────────────────────
# III. ON-CHAIN
# ─────────────────────────────────────────────────────────────────────────────

# Métricas Blockchain.info disponíveis para Bitcoin
BLOCKCHAIN_INFO_METRICS: dict[str, str] = {
    "hash-rate":                        "Hash Rate (EH/s)",
    "n-unique-addresses":               "Active Addresses",
    "n-transactions":                   "Transaction Count",
    "miners-revenue":                   "Miner Revenue (USD)",
    "transaction-fees":                 "Transaction Fees (BTC)",
    "market-cap":                       "Market Cap (USD)",
    "estimated-transaction-volume-usd": "Tx Volume (USD)",
    "mempool-size":                     "Mempool Size",
}

# Etherscan — módulos e actions necessários
ETHERSCAN_ENDPOINTS: dict[str, tuple[str, str]] = {
    "eth_supply":   ("stats",      "ethsupply"),
    "eth_supply2":  ("stats",      "ethsupply2"),
    "eth_price":    ("stats",      "ethprice"),
    "gas_oracle":   ("gastracker", "gasoracle"),
    "block_number": ("proxy",      "eth_blockNumber"),
    "token_supply": ("stats",      "tokensupply"),
}

# ─────────────────────────────────────────────────────────────────────────────
# IV. MACRO CRYPTO
# ─────────────────────────────────────────────────────────────────────────────

# Drivers macro por categoria — equivalente ao SENSIBILIDADE_SETORIAL do equity
# Escala: +1 = positivo quando sobe, -1 = negativo quando sobe, 0 = neutro
SENSIBILIDADE_MACRO: dict[str, dict] = {
    "layer1": {
        "btc_dominance":  -1,   # alta dominância BTC = altcoins sofrem
        "fear_greed":     +1,   # greed = mercado em alta
        "funding_rate":   +1,   # funding positivo = mercado bullish
        "google_trends":  +1,   # interesse crescente = adoção
        "descricao": "L1s são sensíveis ao ciclo macro do Bitcoin e ao sentimento geral do mercado.",
    },
    "layer2": {
        "btc_dominance":  -1,
        "fear_greed":     +1,
        "funding_rate":   +1,
        "google_trends":  +1,
        "eth_gas":        +1,   # gas alto = mais uso de L2
        "descricao": "L2s dependem do ecossistema Ethereum e se beneficiam de alta atividade on-chain.",
    },
    "defi": {
        "btc_dominance":  -1,
        "fear_greed":     +1,
        "funding_rate":    0,
        "tvl_total":      +1,   # TVL crescendo = setor saudável
        "eth_gas":        -1,   # gas alto = fricção para usuários DeFi
        "descricao": "DeFi é sensível ao TVL total do ecossistema e ao custo de gas do Ethereum.",
    },
    "dex": {
        "btc_dominance":  -1,
        "fear_greed":     +1,
        "volume_defi":    +1,   # volume alto = mais fees geradas
        "eth_gas":        -1,
        "descricao": "DEXs dependem do volume de trading — crescem em mercados voláteis e ativos.",
    },
    "lending": {
        "btc_dominance":  -1,
        "fear_greed":      0,
        "funding_rate":   +1,
        "tvl_total":      +1,
        "descricao": "Lending protocols crescem com TVL alto e mercados bullish que aumentam colateral.",
    },
    "liquid_staking": {
        "btc_dominance":   0,
        "fear_greed":     +1,
        "eth_staking_rate":+1,  # mais staking = mais demanda por liquid staking
        "descricao": "Liquid staking cresce com adoção de proof-of-stake e busca por yield.",
    },
    "stablecoins": {
        "btc_dominance":  +1,   # dominância alta = fuga para stablecoins
        "fear_greed":     -1,   # fear = entrada em stablecoins
        "funding_rate":    0,
        "descricao": "Stablecoins crescem em momentos de medo e incerteza do mercado.",
    },
    "gaming": {
        "btc_dominance":  -1,
        "fear_greed":     +1,
        "google_trends":  +1,
        "descricao": "Gaming/NFT é altamente especulativo e correlacionado com sentimento de mercado.",
    },
    "rwa": {
        "btc_dominance":   0,
        "fear_greed":      0,
        "tvl_total":      +1,
        "descricao": "RWA crescem com adoção institucional e regulação favorável.",
    },
    "generic": {
        "btc_dominance":  -1,
        "fear_greed":     +1,
        "funding_rate":   +1,
        "descricao": "Análise macro geral aplicada ao ativo.",
    },
}

# Limiares para classificação dos drivers macro
LIMIARES_MACRO: dict[str, float] = {
    "fear_greed_extremo_medo":   25.0,   # ≤ 25 = Extreme Fear
    "fear_greed_medo":           45.0,   # ≤ 45 = Fear
    "fear_greed_ganancia":       65.0,   # ≥ 65 = Greed
    "fear_greed_extremo_ganancia":80.0,  # ≥ 80 = Extreme Greed
    "btc_dominance_alta":        60.0,   # ≥ 60% = dominância alta (altcoins sofrem)
    "btc_dominance_baixa":       40.0,   # ≤ 40% = dominância baixa (altseason)
    "funding_rate_bullish":       0.01,  # ≥ 0.01% por 8h = bullish
    "funding_rate_bearish":      -0.01,  # ≤ -0.01% por 8h = bearish
    "fdv_mcap_risco_alto":        3.0,   # FDV/MCap > 3x = risco de diluição alto
    "fdv_mcap_risco_medio":       1.5,   # FDV/MCap > 1.5x = risco médio
}

# Contexto macro — rótulo e cor hex
CONTEXTO: dict[str, tuple[str, str]] = {
    "favoravel":    ("Favorável",    "#1A5276"),
    "neutro":       ("Neutro",       "#B7950B"),
    "desfavoravel": ("Desfavorável", "#BA4A00"),
}

# ─────────────────────────────────────────────────────────────────────────────
# V. NOTÍCIAS POR CATEGORIA
# ─────────────────────────────────────────────────────────────────────────────

NEWS_KEYWORDS: dict[str, dict] = {
    "layer1": {
        "keywords_globais": [
            '"layer 1 blockchain"', '"proof of stake"', '"blockchain adoption"',
            '"crypto market"', '"bitcoin dominance"', '"ethereum upgrade"',
        ],
        "keywords_relevancia": [
            "upgrade", "mainnet", "testnet", "staking", "validator",
            "throughput", "tps", "partnership", "adoption", "ecosystem",
        ],
        "keywords_exclusao": [
            "scam", "rug pull", "hack", "exploit", "celebrity",
        ],
    },
    "layer2": {
        "keywords_globais": [
            '"layer 2"', '"rollup"', '"ethereum scaling"', '"zk proof"',
            '"optimistic rollup"', '"TVL"',
        ],
        "keywords_relevancia": [
            "tvl", "bridge", "sequencer", "rollup", "scaling",
            "transaction", "fees", "upgrade", "mainnet",
        ],
        "keywords_exclusao": [
            "scam", "rug pull", "hack", "celebrity",
        ],
    },
    "defi": {
        "keywords_globais": [
            '"DeFi"', '"decentralized finance"', '"total value locked"',
            '"yield farming"', '"liquidity"', '"protocol revenue"',
        ],
        "keywords_relevancia": [
            "tvl", "yield", "liquidity", "protocol", "revenue",
            "fees", "apy", "vault", "pool", "governance",
        ],
        "keywords_exclusao": [
            "scam", "rug pull", "hack", "exploit", "celebrity",
        ],
    },
    "dex": {
        "keywords_globais": [
            '"decentralized exchange"', '"DEX volume"', '"AMM"',
            '"liquidity pool"', '"swap"', '"trading fees"',
        ],
        "keywords_relevancia": [
            "volume", "liquidity", "pool", "swap", "fees",
            "trading", "pair", "slippage", "governance",
        ],
        "keywords_exclusao": [
            "scam", "rug pull", "hack", "celebrity",
        ],
    },
    "lending": {
        "keywords_globais": [
            '"DeFi lending"', '"collateral"', '"borrowing"',
            '"liquidation"', '"interest rate"', '"bad debt"',
        ],
        "keywords_relevancia": [
            "collateral", "borrow", "lend", "liquidation", "tvl",
            "interest", "utilization", "governance", "risk",
        ],
        "keywords_exclusao": [
            "scam", "rug pull", "hack", "celebrity",
        ],
    },
    "generic": {
        "keywords_globais": [
            '"crypto market"', '"blockchain"', '"digital assets"',
            '"web3"', '"token"',
        ],
        "keywords_relevancia": [
            "partnership", "adoption", "upgrade", "mainnet",
            "launch", "token", "governance", "community",
        ],
        "keywords_exclusao": [
            "scam", "rug pull", "hack", "celebrity",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# VI. SCORING
# ─────────────────────────────────────────────────────────────────────────────

# Limiares para scoring quantitativo absoluto
LIMIARES_QUANT: dict[str, dict[str, float]] = {
    "sharpe": {
        "fraco": 0.0,
        "neutro": 0.5,
        "bom": 1.0,
        "otimo": 1.5,
    },
    "sortino": {
        "fraco": 0.0,
        "neutro": 0.75,
        "bom": 1.25,
        "otimo": 1.75,
    },
    "max_drawdown_invertido": {
        "fraco": 0.0,
        "neutro": 0.1,
        "bom": 0.25,
        "otimo": 0.50,
    },
    "cagr": {
        "fraco": 0.0,
        "neutro": 0.05,
        "bom": 0.15,
        "otimo": 0.30,
    },
    "volatilidade_invertida": {
        "fraco": -1.0,
        "neutro": -0.7,
        "bom": -0.5,
        "otimo": -0.3,
    },
    "calmar": {
        "fraco": 0.0,
        "neutro": 0.1,
        "bom": 0.25,
        "otimo": 0.50,
    },
    "var_invertido": {
        "fraco": 0.0,
        "neutro": 0.05,
        "bom": 0.15,
        "otimo": 0.30,
    },
}

LIMIARES_FUNDAMENTAL: dict[str, dict[str, float]] = {
    "trends": {
        "fraco": 10.0,
        "neutro": 20.0,
        "bom": 40.0,
        "otimo": 70.0,
    },
    "btc_hash_rate": {
        "fraco": 100e18,
        "neutro": 200e18,
        "bom": 400e18,
        "otimo": 600e18,
    },
    "nvt": {
        "fraco": 100.0,
        "neutro": 60.0,
        "bom": 30.0,
        "otimo": 0.0,
    },
    "eth_staking_pct": {
        "fraco": 0.10,
        "neutro": 0.16,
        "bom": 0.22,
        "otimo": 0.28,
    },
    "fee_margin": {
        "fraco": 0.05,
        "neutro": 0.15,
        "bom": 0.30,
        "otimo": 0.50,
    },
    "mcap_volume": {
        "fraco": 60.0,
        "neutro": 30.0,
        "bom": 15.0,
        "otimo": 5.0,
    },
    "dev_aceleracao": {
        "fraco": 0.6,
        "neutro": 0.9,
        "bom": 1.1,
        "otimo": 1.5,
    },
}

# Score Quantitativo
PESOS_QUANT: dict[str, float] = {
    "score_sharpe":      0.15,
    "score_sortino":     0.15,
    "score_drawdown":    0.15,
    "score_cagr":        0.20,
    "score_volatilidade":0.15,
    "score_calmar":      0.10,
    "score_var":         0.10,
}

# Score Fundamentalista (pilares)
PESOS_FUNDAMENTAL: dict[str, float] = {
    "Tokenomics":        0.25,
    "Adoção":            0.20,
    "OnChain":           0.20,
    "ProtocolRevenue":   0.20,
    "Valuation":         0.15,
}

# Sub-pesos do pilar Tokenomics
PESOS_TOKENOMICS: dict[str, float] = {
    "supply_pct_circulating": 0.20,
    "fdv_to_mcap":            0.30,
    "inflation_rate":         0.25,
    "commit_count_4_weeks":   0.25,
}

# Sub-pesos do pilar Adoção
PESOS_ADOCAO: dict[str, float] = {
    "volume_mcap_ratio":    0.30,
    "price_change_30d":     0.20,
    "google_trends":        0.25,
    "active_addresses":     0.25,
}

# Sub-pesos do pilar OnChain
PESOS_ONCHAIN: dict[str, float] = {
    "hash_rate_yoy":        0.35,
    "active_addresses_yoy": 0.35,
    "nvt_ratio":            0.30,
}

# Sub-pesos do pilar Protocol Revenue (DeFi)
PESOS_PROTOCOL_REVENUE: dict[str, float] = {
    "tvl":            0.30,
    "tvl_yoy":        0.25,
    "revenue_30d":    0.25,
    "fees_30d":       0.20,
}

# Sub-pesos do pilar Valuation
PESOS_VALUATION: dict[str, float] = {
    "mcap_tvl":       0.35,   # Market Cap / TVL (equivalente ao P/VP)
    "fdv_revenue":    0.35,   # FDV / Revenue anualizado (equivalente ao EV/Revenue)
    "volume_mcap":    0.30,   # Volume / Market Cap (liquidez relativa)
}

# Score Macro
PESOS_MACRO: dict[str, float] = {
    "fear_greed":     0.25,
    "btc_dominance":  0.25,
    "funding_rate":   0.20,
    "google_trends":  0.15,
    "halving_cycle":  0.15,
}

# Score Integrado Final
PESOS_INTEGRADO: dict[str, float] = {
    "quant":       0.30,
    "fundamental": 0.25,
    "onchain":     0.20,
    "macro":       0.15,
    "ia":          0.10,
}

# Nomes de exibição dos componentes do score integrado
NOMES_SCORE_INTEGRADO: dict[str, str] = {
    "quant":       "Quantitativo",
    "fundamental": "Fundamentalista",
    "onchain":     "On-Chain",
    "macro":       "Macro Crypto",
    "ia":          "Análise IA",
}

# Thresholds de classificação (0–10)
SCORE_CLASSIFICACAO: list[tuple[float, str, str]] = [
    (7.0, "FORTE",  "#1A5276"),
    (5.0, "NEUTRO", "#B7950B"),
    (3.0, "FRACO",  "#BA4A00"),
    (0.0, "VENDA",  "#922B21"),
]


def classificar_score(score: float) -> tuple[str, str]:
    """Retorna (label, cor_hex) para um score 0–10."""
    for threshold, label, cor in SCORE_CLASSIFICACAO:
        if score >= threshold:
            return label, cor
    return "VENDA", "#922B21"


# Métricas onde MENOR valor = melhor (usadas no ranking percentil)
MENOR_MELHOR: set[str] = {
    "fdv_to_mcap",
    "inflation_rate",
    "nvt_ratio",
    "fdv_revenue",
}

# ─────────────────────────────────────────────────────────────────────────────
# VII. HALVING CYCLE
# ─────────────────────────────────────────────────────────────────────────────

# Datas históricas e estimadas dos halvings do Bitcoin
HALVINGS: list[datetime] = [
    datetime(2009,  1,  3),   # Genesis block
    datetime(2012, 11, 28),   # Halving 1
    datetime(2016,  7,  9),   # Halving 2
    datetime(2020,  5, 11),   # Halving 3
    datetime(2024,  4, 19),   # Halving 4 (atual)
    datetime(2028,  4,  1),   # Halving 5 (estimado)
]

# Fases do ciclo e seus thresholds (% do ciclo completo)
FASES_HALVING: list[tuple[float, str, str, str]] = [
    # (pct_min, label, cor, descricao)
    (0.0,  "POST-HALVING ACUMULAÇÃO", "#27AE60",
     "Primeiros meses após halving — historicamente período de acumulação antes da bull run."),
    (0.20, "BULL RUN",               "#1A5276",
     "Fase de alta — historicamente o período de maior valorização do ciclo."),
    (0.50, "DISTRIBUIÇÃO / TOPO",    "#E67E22",
     "Fase próxima ao topo histórico — risco elevado de reversão."),
    (0.75, "BEAR MARKET",            "#C0392B",
     "Fase final do ciclo — historicamente período de capitulação e acumulação."),
]