import numpy as np
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY

_MODELOS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemma-4-26b-a4b-it",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

MAX_PROMPT_CHARS = 24_000


def _montar_prompt(nome: str, simbolo: str, categoria: str | None,
                   sinais_macro: dict, noticias_texto: str,
                   scores_macro: dict, dados_mercado: dict) -> str:

    preco    = dados_mercado.get("preco_usd", np.nan)
    var_30d  = dados_mercado.get("variacao_30d", np.nan)
    mcap     = dados_mercado.get("mcap_usd", np.nan)
    rank     = dados_mercado.get("rank_mercado", np.nan)

    linhas_macro = "\n".join(
        f"- {k.replace('_', ' ').title()}: {v}"
        for k, v in sinais_macro.items()
    )

    linhas_scores = "\n".join(
        f"- {k.replace('score_', '').replace('_', ' ').title()}: {v:.1f}/10"
        for k, v in scores_macro.items()
        if k.startswith("score_") and not np.isnan(v)
    )

    preco_str   = f"${preco:,.4f}" if not np.isnan(preco) else "N/D"
    var_30d_str = f"{var_30d:+.1f}%" if not np.isnan(var_30d) else "N/D"
    mcap_str    = f"${mcap/1e9:.2f}B" if not np.isnan(mcap) else "N/D"
    rank_str    = str(int(rank)) if not np.isnan(rank) else "N/D"

    prompt = f"""Você é um analista sênior de criptomoedas. Sua tarefa é produzir uma análise macro concisa e fundamentada sobre {nome} ({simbolo}).

## Dados de Mercado
- Preço atual: {preco_str}
- Variação 30d: {var_30d_str}
- Market Cap: {mcap_str} (rank #{rank_str})
- Categoria: {categoria or 'N/D'}

## Contexto Macro Crypto
{linhas_macro}

## Scores Macro (0–10)
{linhas_scores}

## Notícias Recentes
{noticias_texto if noticias_texto else 'Nenhuma notícia relevante encontrada.'}

## Tarefa
Escreva uma análise macro em português com exatamente 3 seções:

**1. Contexto de Mercado (2–3 parágrafos)**
Interprete as variáveis macro acima (Fear & Greed, BTC Dominance, Funding Rate, ciclo de halving) e como elas afetam {nome} especificamente. Seja objetivo e evite jargões desnecessários.

**2. Principais Riscos e Oportunidades (bullet points)**
Liste 3 riscos e 3 oportunidades concretas com base nos dados apresentados. Não invente riscos genéricos — ancore cada um nos dados acima.

**3. Veredicto Macro**
Uma frase direta com sua avaliação do contexto macro atual para {nome}: Favorável / Neutro / Desfavorável — e por quê em 2–3 linhas.

Seja direto. Não repita os dados brutos — interprete-os. Máximo 500 palavras."""

    return prompt


def gerar_analise_ia(nome: str, simbolo: str, categoria: str | None,
                     sinais_macro: dict, noticias_texto: str,
                     scores_macro: dict, dados_mercado: dict) -> dict:
    """
    Envia prompt ao Gemini e retorna análise textual + score IA.
    Retorna dict vazio se GEMINI_API_KEY não estiver configurada.
    """
    if not GEMINI_API_KEY:
        print("[gemini] GEMINI_API_KEY não configurada — análise IA ignorada.")
        return {}

    prompt = _montar_prompt(
        nome, simbolo, categoria, sinais_macro,
        noticias_texto, scores_macro, dados_mercado
    )

    prompt = prompt[:MAX_PROMPT_CHARS]
    client = genai.Client(api_key=GEMINI_API_KEY)
    score_macro_base = scores_macro.get("score_macro", np.nan)

    for modelo in _MODELOS:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=900,
                ),
            )
            texto = response.text.strip()
            return {
                "analise_ia_texto": texto,
                "score_ia":         round(score_macro_base, 2) if not np.isnan(score_macro_base) else np.nan,
                "modelo_ia":        modelo,
            }
        except Exception as e:
            print(f"[gemini] {modelo}: {e}")

    print("[gemini] Todos os modelos falharam — análise IA ignorada.")
    return {}