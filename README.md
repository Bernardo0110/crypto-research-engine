# Crypto Research Engine

Framework automatizado de análise de criptomoedas. Dado um coin ID do CoinGecko, executa análise quantitativa, fundamentalista, on-chain e macroeconômica, exportando um PDF profissional com scoring multifatorial, gráficos e narrativa gerada por IA.

---

## Como usar

```bash
python main.py                  # analisa o ativo configurado em config/settings.py
python main.py bitcoin          # sobrescreve o ativo
python main.py solana ethereum  # sobrescreve ativo e benchmark
```

O relatório é salvo automaticamente em `outputs/pdfs/`.

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/crypto-research-engine.git
cd crypto-research-engine

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Instale o Playwright (necessário para gerar o PDF)
playwright install chromium

# 5. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves de API
```

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha as chaves:

| Variável | Obrigatória | Onde obter |
|---|---|---|
| `COINGECKO_DEMO_KEY` | Não (recomendada) | [coingecko.com](https://www.coingecko.com/en/api) → Get Demo API Key |
| `ETHERSCAN_API_KEY` | Não (recomendada) | [etherscan.io](https://etherscan.io/register) → API Keys |
| `GITHUB_TOKEN` | Não (recomendada) | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `GEMINI_API_KEY` | Não | [aistudio.google.com](https://aistudio.google.com) |
| `TOKENOMIST_API_KEY` | Não | [tokenomist.ai](https://tokenomist.ai/pricing) (trial gratuito) |

Sem as chaves opcionais o projeto funciona normalmente, mas com dados mais limitados e rate limits menores.

---

## Estrutura do projeto

```
crypto-research-engine/
├── config/
│   ├── mappings.py          ← FONTE ÚNICA de todos os mapeamentos estáticos
│   └── settings.py          ← runtime: ATIVO, BENCHMARK, API keys
│
├── data/
│   ├── field_mapper.py      ← normaliza e calcula métricas derivadas
│   └── providers/
│       ├── coingecko_provider.py   preços, market data, tokenomics, peers
│       ├── defillama_provider.py   TVL, fees, revenue (DeFi)
│       ├── onchain_provider.py     BTC on-chain (Blockchain.info) + ETH (Etherscan)
│       ├── macro_provider.py       Fear & Greed, OKX funding rates, BTC dominance
│       ├── news_provider.py        Google News RSS
│       ├── github_provider.py      commits, contributors, stars
│       └── crypto_provider.py      orquestra todos os providers
│
├── quant/
│   ├── metrics.py           CAGR, Sharpe, Sortino, Beta, Drawdown, Alpha, VaR
│   ├── scoring.py           converte métricas em scores 0–10
│   └── charts.py            gráficos quantitativos
│
├── fundamental/
│   ├── metrics.py           orquestra os 6 pilares para todos os peers
│   ├── scoring.py           agrega scores com pesos
│   ├── validation.py        checagem de consistência
│   ├── charts.py            gráficos fundamentalistas
│   └── pillars/
│       ├── tokenomics.py    supply, FDV/MCap, inflation rate
│       ├── adoption.py      volume, google trends, active addresses
│       ├── onchain.py       hash rate, NVT, on-chain metrics
│       ├── protocol_revenue.py  TVL, fees, revenue (DeFi)
│       ├── valuation.py     MCap/TVL, FDV/Revenue, Volume/MCap
│       └── developer.py     GitHub commits, contributors
│
├── macro/
│   ├── analysis.py          scores das variáveis macro por categoria
│   ├── ai_analyst.py        Gemini analisa notícias + macro
│   └── charts.py            gráficos macro (Fear & Greed, Halving, etc.)
│
├── narrative/
│   └── generator.py         textos interpretativos para o PDF
│
├── pdf/
│   ├── renderer_html.py     Jinja2 → HTML → Playwright → PDF
│   └── templates/
│       └── relatorio.html   template completo do relatório
│
├── outputs/pdfs/            PDFs gerados (gitignored)
├── notebooks/               protótipos e testes em Colab
├── main.py                  pipeline principal
├── requirements.txt
├── .env.example
└── CLAUDE.md                guia para IAs que trabalhem neste projeto
```

---

## Sistema de scoring

O projeto usa **scoring por percentil**: cada métrica é comparada com os peers da mesma categoria CoinGecko (ex: Layer-1s, DeFi, DEXs). O score vai de 0 (pior do peer set) a 10 (melhor).

### Score Integrado Final

| Componente | Peso | Requer |
|---|---|---|
| Quantitativo | 30% | Sempre disponível |
| Fundamentalista | 25% | CoinGecko + DeFiLlama |
| On-Chain | 20% | Blockchain.info / Etherscan |
| Macro Crypto | 15% | OKX + Alternative.me |
| Análise IA | 10% | `GEMINI_API_KEY` |

Quando algum componente não tem dados, os pesos são redistribuídos proporcionalmente entre os disponíveis.

### Classificação final

| Score | Classificação |
|---|---|
| 7.0 – 10.0 | **FORTE** |
| 5.0 – 6.9 | **NEUTRO** |
| 3.0 – 4.9 | **FRACO** |
| 0.0 – 2.9 | **VENDA** |

---

## Fontes de dados

| Fonte | Provider | API key | O que fornece |
|---|---|---|---|
| CoinGecko | `coingecko_provider` | Demo (opcional) | Preços, peers, tokenomics |
| DeFiLlama | `defillama_provider` | Não | TVL, fees, revenue (DeFi) |
| Blockchain.info | `onchain_provider` | Não | BTC: hash rate, active addresses |
| Etherscan V2 | `onchain_provider` | Gratuita | ETH: supply, gas, staking |
| OKX Public | `macro_provider` | Não | Funding rates, open interest |
| Alternative.me | `macro_provider` | Não | Fear & Greed Index |
| GitHub API | `github_provider` | Opcional | Commits, contributors, stars |
| Google News RSS | `news_provider` | Não | Notícias recentes |
| pytrends | `macro_provider` | Não | Google Trends |
| Gemini (Google) | `macro/ai_analyst` | **Sim** | Veredicto textual |
| Tokenomist | `coingecko_provider` | Trial | Token unlock schedule |

---

## Estrutura do PDF

O relatório gerado tem no mínimo **5 páginas de análise** + apêndices de dados brutos:

| Página | Conteúdo |
|---|---|
| 1 | **Capa** — nome, preço, score integrado, composição dos scores, variações |
| 2 | **Sumário Executivo** — veredicto IA, scores por dimensão, pontos positivos/negativos |
| 3 | **Análise Quantitativa** — gráficos de preço, retornos vs benchmark, tabela de métricas |
| 4 | **Análise Fundamentalista** — pilares, tokenomics, TVL, developer activity, peers |
| 5 | **Contexto Macro & Veredicto** — Fear & Greed, Halving cycle, score final |
| A | **Apêndice A** — métricas quantitativas completas, radar de scores |
| B | **Apêndice B** — comparativo de peers por categoria |
| C | **Apêndice C** — notícias recentes filtradas |

---

## Diferenças críticas em relação ao projeto equity

| Aspecto | Equity | Crypto |
|---|---|---|
| Dias úteis/ano | 252 | **365** (crypto opera 24/7) |
| Taxa livre de risco | CDI (BCB) | **Fed Funds Rate** |
| Benchmark | ^BVSP | **BTC-USD** |
| Peers | Setor GICS B3 | **Categoria CoinGecko** |
| Fundamentalista | DRE/BPA/BPP (CVM) | **Tokenomics + TVL + On-Chain** |
| Macro | SELIC, IPCA, câmbio | **Fear & Greed, BTC Dom, Funding Rate** |
| Ciclo de mercado | N/A | **Halving Cycle Bitcoin** |

---

## Tratamento de dados ausentes

O projeto foi desenhado para analisar **qualquer crypto**, mesmo com cobertura parcial:

- Campo sem dado → `np.nan` (nunca `None` em DataFrames)
- Pilar sem dados suficientes → excluído do score com aviso no relatório
- Pesos redistribuídos automaticamente entre componentes disponíveis
- PDF gerado mesmo com análise parcial — seções sem dados exibem aviso explicativo

---

## Adicionando novas criptomoedas

Para analisar qualquer coin listado no CoinGecko, basta usar o ID do CoinGecko:

```bash
python main.py hyperliquid
python main.py aptos
python main.py sui
python main.py arbitrum
```

Para encontrar o ID correto: acesse `https://www.coingecko.com/en/coins/NOME_DA_MOEDA` — o ID aparece na URL.

Para adicionar suporte a um novo coin com dados on-chain ou GitHub, edite os mapeamentos em:
- `data/providers/onchain_provider.py` → `buscar_onchain()`
- `data/providers/github_provider.py` → `COINGECKO_PARA_GITHUB`
- `data/providers/macro_provider.py` → `COINGECKO_PARA_OKX`
- `config/mappings.py` → `CATEGORY_PEERS`

---

## Licença

MIT