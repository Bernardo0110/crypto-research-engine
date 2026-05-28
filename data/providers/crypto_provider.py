import numpy as np
from config.settings import ATIVO, BENCHMARK
from data.providers.coingecko_provider import (
    buscar_dados_mercado,
    buscar_historico_precos,
    buscar_categoria,
    buscar_peers,
    buscar_dados_mercado_batch,
    buscar_tokenomics_tokenomist,
)
from data.providers.defillama_provider import buscar_tvl_categoria
from data.providers.onchain_provider import buscar_onchain
from data.providers.macro_provider import buscar_macro_completo
from data.providers.github_provider import buscar_dados_github_batch
from data.providers.news_provider import (
    buscar_noticias_coin,
    buscar_noticias_macro,
    filtrar_relevantes,
    preparar_noticias_para_ia,
)


def coletar_dados(coin_id: str = ATIVO, benchmark_id: str = BENCHMARK) -> dict:
    """
    Orquestra todos os providers e retorna dict completo com dados do coin.
    Nunca lança exceção — falhas parciais retornam np.nan nos campos afetados.
    """
    print(f"\n[crypto_provider] Coletando dados: {coin_id} (benchmark: {benchmark_id})")

    # ── Dados básicos ──────────────────────────────────────────────────────────
    print("  → CoinGecko: dados de mercado...")
    dados_mercado = buscar_dados_mercado(coin_id)
    nome = dados_mercado.get("nome", coin_id)
    simbolo = dados_mercado.get("simbolo", coin_id.upper())

    # ── Categoria e peers ──────────────────────────────────────────────────────
    print("  → CoinGecko: peers...")
    categoria = buscar_categoria(coin_id)
    peers = buscar_peers(coin_id, categoria)
    print(f"     categoria={categoria}, peers={peers}")

    # ── Histórico de preços ────────────────────────────────────────────────────
    print("  → CoinGecko: histórico de preços (ativo + benchmark)...")
    historico_ativo     = buscar_historico_precos(coin_id, dias=730)
    historico_benchmark = buscar_historico_precos(benchmark_id, dias=730)

    # ── Market data dos peers (batch) ──────────────────────────────────────────
    print("  → CoinGecko: market data dos peers...")
    market_peers = buscar_dados_mercado_batch(peers)

    # ── Tokenomics Tokenomist ──────────────────────────────────────────────────
    print("  → Tokenomist: unlocks...")
    tokenomics = buscar_tokenomics_tokenomist(coin_id)

    # ── DeFiLlama ─────────────────────────────────────────────────────────────
    print("  → DeFiLlama: TVL e revenue dos peers...")
    defillama_peers = buscar_tvl_categoria(peers)

    # ── On-Chain ──────────────────────────────────────────────────────────────
    print(f"  → On-Chain: {coin_id}...")
    onchain = buscar_onchain(coin_id)

    # ── GitHub ────────────────────────────────────────────────────────────────
    print("  → GitHub: developer activity dos peers...")
    github_peers = buscar_dados_github_batch(peers)

    # ── Macro ─────────────────────────────────────────────────────────────────
    print("  → Macro: fear&greed, dominance, funding rates, trends, halving...")
    macro = buscar_macro_completo(coin_id, termos_trends=[nome, coin_id])

    # ── Notícias ──────────────────────────────────────────────────────────────
    print("  → News: Google News RSS...")
    noticias_raw = buscar_noticias_coin(coin_id, nome)
    noticias_macro = buscar_noticias_macro()
    noticias_filtradas = filtrar_relevantes(noticias_raw, coin_id, nome)
    noticias_texto = preparar_noticias_para_ia(noticias_filtradas)

    print("  ✓ Coleta concluída.\n")

    return {
        # Identificação
        "coin_id":             coin_id,
        "benchmark_id":        benchmark_id,
        "nome":                nome,
        "simbolo":             simbolo,
        "categoria":           categoria,
        "peers":               peers,

        # Market data
        "dados_mercado":       dados_mercado,
        "market_peers":        market_peers,

        # Preços
        "historico_ativo":     historico_ativo,
        "historico_benchmark": historico_benchmark,

        # Tokenomics
        "tokenomics":          tokenomics,

        # DeFi
        "defillama_peers":     defillama_peers,

        # On-Chain
        "onchain":             onchain,

        # Developer
        "github_peers":        github_peers,

        # Macro
        "macro":               macro,

        # Notícias
        "noticias_filtradas":  noticias_filtradas,
        "noticias_macro":      noticias_macro,
        "noticias_texto":      noticias_texto,
    }