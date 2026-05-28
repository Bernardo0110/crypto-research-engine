# Crypto Research Engine — Guia para IAs

Framework automatizado de análise de criptomoedas. Dado um coin ID do CoinGecko (ex: `ethereum`), executa análise quantitativa, fundamentalista, on-chain e macroeconômica, exportando um PDF profissional com scoring multifatorial, gráficos e narrativa gerada por IA.

---

## Como rodar

```bash
python main.py                        # usa config/settings.py (ATIVO = "ethereum")
python main.py bitcoin                # sobrescreve o ativo
python main.py solana bitcoin         # sobrescreve ativo e benchmark
```

**Variáveis de ambiente (`.env`):**

```
COINGECKO_DEMO_KEY=...   # opcional — sem ela rate limit menor
ETHERSCAN_API_KEY=...    # opcional — sem ela métricas ETH limitadas
GITHUB_TOKEN=...         # opcional — sem ela rate limit 60 req/h
GEMINI_API_KEY=...       # opcional — sem ela análise IA ignorada
TOKENOMIST_API_KEY=...   # opcional — sem ela unlocks marcados como N/D
```

---

## Estrutura de pastas

```
config/
  mappings.py       ← FONTE ÚNICA de todos os dicts/sets/pesos estáticos
  settings.py       ← config de runtime: ATIVO, BENCHMARK, PERIODOS, cores

data/
  field_mapper.py         normaliza e valida dados entre providers
  providers/
    coingecko_provider.py   preços, market data, tokenomics, peers
    defillama_provider.py   TVL, fees, revenue (DeFi)
    onchain_provider.py     Bitcoin on-chain (Blockchain.info) + ETH (Etherscan)
    macro_provider.py       Fear & Greed, OKX funding rates, BTC dominance
    news_provider.py        Google News RSS
    github_provider.py      developer activity (commits, contributors)
    crypto_provider.py      orquestra todos os providers

quant/
  metrics.py    calcula CAGR, Sharpe, Beta, Drawdown, Alpha etc.
  scoring.py    converte métricas em scores 0–10 (percentil)
  charts.py     gráficos quant

fundamental/
  metrics.py    orquestra os 5 pilares para todos os peers
  scoring.py    agrega scores dos pilares com pesos
  validation.py checagem de consistência
  charts.py     gráficos fundamentalistas
  pillars/
    tokenomics.py       supply, FDV/MCap, inflation rate, developer activity
    adoption.py         volume, google trends, active addresses
    onchain.py          hash rate, NVT, on-chain metrics
    protocol_revenue.py TVL, fees, revenue (DeFi — N/D para não-DeFi)
    valuation.py        MCap/TVL, FDV/Revenue, Volume/MCap
    developer.py        GitHub commits, contributors, code frequency

macro/
  analysis.py   aplica sensibilidades por categoria às variáveis macro
  ai_analyst.py Gemini analisa notícias + macro e emite veredicto
  charts.py     gráficos macro

narrative/
  generator.py  geração de texto interpretativo

pdf/
  renderer_html.py  Jinja2 → HTML → Playwright → PDF

main.py           orquestra todo o pipeline
outputs/pdfs/     PDFs gerados
notebooks/        features em desenvolvimento (Colab)
```

---

## Fluxo de dados

```
settings.py (ATIVO, BENCHMARK)
        │
        ├─ coingecko_provider  → preços, peers, tokenomics, market data
        ├─ defillama_provider  → TVL, fees, revenue (DeFi)
        ├─ onchain_provider    → hash rate, active addresses, NVT (BTC/ETH)
        ├─ macro_provider      → fear&greed, funding rates, BTC dominance
        ├─ github_provider     → commits, contributors, stars
        ├─ news_provider       → notícias Google RSS
        │
        ├─ crypto_provider     → orquestra e normaliza todas as fontes
        │
        ├─ quant/metrics       → CAGR, Sharpe, Beta, Drawdown etc.
        ├─ quant/scoring       → score quant 0–10
        │
        ├─ fundamental/metrics → calcula 5 pilares para todos os peers
        ├─ fundamental/scoring → score fundamentalista 0–10
        │
        ├─ macro/analysis      → avalia contexto macro por categoria
        ├─ macro/ai_analyst    → Gemini emite veredicto textual
        │
        ├─ quant/scoring       → Score Integrado Final
        ├─ narrative/generator → textos interpretativos
        └─ pdf/renderer_html   → PDF final
```

---

## Sistema de scoring

**Metodologia:** percentil dentro do peer set por categoria (0 = pior, 10 = melhor).

**Componentes do Score Integrado Final:**

| Componente      | Peso | Requer                      |
|-----------------|------|-----------------------------|
| Quantitativo    | 30%  | sempre disponível           |
| Fundamentalista | 25%  | CoinGecko + DeFiLlama       |
| On-Chain        | 20%  | Blockchain.info + Etherscan |
| Macro Crypto    | 15%  | OKX + Alternative.me        |
| Análise IA      | 10%  | GEMINI_API_KEY              |

Pesos redistribuídos proporcionalmente quando algum componente está ausente.

---

## Fontes de dados externas

| Fonte           | Provider               | API key?        | O que fornece                               |
|-----------------|------------------------|-----------------|---------------------------------------------|
| CoinGecko       | coingecko_provider.py  | Demo (opcional) | preços, peers, tokenomics, market data      |
| DeFiLlama       | defillama_provider.py  | não             | TVL, fees, revenue por protocolo            |
| Blockchain.info | onchain_provider.py    | não             | on-chain BTC: hash rate, active addresses   |
| Etherscan V2    | onchain_provider.py    | gratuita        | on-chain ETH: supply, gas, staking          |
| OKX Public      | macro_provider.py      | não             | funding rates, open interest, L/S ratio     |
| Alternative.me  | macro_provider.py      | não             | Fear & Greed Index histórico                |
| GitHub API      | github_provider.py     | opcional        | commits, contributors, stars, languages     |
| Google News RSS | news_provider.py       | não             | notícias por projeto/categoria              |
| pytrends        | macro_provider.py      | não             | Google Trends — interesse de busca          |
| Gemini (Google) | macro/ai_analyst.py    | **sim**         | veredicto macro textual                     |
| Tokenomist      | coingecko_provider.py  | trial           | token unlock schedule (N/D sem key)         |

---

## Diferenças críticas em relação ao projeto equity

| Aspecto             | Equity                  | Crypto                               |
|---------------------|-------------------------|--------------------------------------|
| Dias úteis por ano  | 252                     | **365** (crypto opera 24/7)          |
| Taxa livre de risco | CDI (BCB série 4389)    | **Fed Funds Rate**                   |
| Benchmark           | ^BVSP                   | **BTC-USD**                          |
| Peers               | Setor GICS B3           | **Categoria CoinGecko**              |
| Fundamentalista     | DRE/BPA/BPP via CVM     | **Tokenomics + TVL + On-Chain**      |
| Insiders            | CVM VLMO                | **N/D (Whale Alert é pago)**         |
| Macro específico    | SELIC, IPCA, câmbio     | **Fear&Greed, BTC Dom, Funding Rate**|
| Ciclo de mercado    | não aplicável           | **Halving Cycle Bitcoin**            |

---

## Tratamento de dados ausentes

O projeto foi desenhado para analisar **qualquer crypto**, assumindo graciosamente a falta de dados:

- Campo sem dado → `np.nan` (nunca `None` em DataFrames)
- Pilar sem dados suficientes → excluído do score com aviso
- Pesos redistribuídos automaticamente entre componentes disponíveis
- PDF gerado mesmo com análise parcial — seções sem dados exibem aviso explicativo

---

## Nomenclatura e convenções

- **Idioma:** variáveis, funções e comentários em português
- **Funções privadas:** prefixo `_`
- **Tolerância a falhas:** todo provider usa `try/except` com fallback
- **NaN explícito:** campos sem dado retornam `np.nan`
- **Sem comentários óbvios:** só quando o `porquê` não é evidente
