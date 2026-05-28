import feedparser
import numpy as np
from datetime import datetime, timezone
from config.mappings import API_URLS, NEWS_KEYWORDS


def _buscar_feed(url: str, max_itens: int = 20) -> list[dict]:
    """Parseia um feed RSS/Atom e retorna lista de itens normalizados."""
    try:
        feed = feedparser.parse(url)
        itens = []
        for entry in feed.entries[:max_itens]:
            publicado = entry.get("published_parsed") or entry.get("updated_parsed")
            dt = datetime(*publicado[:6], tzinfo=timezone.utc) if publicado else None
            itens.append({
                "titulo":   entry.get("title", ""),
                "resumo":   entry.get("summary", ""),
                "url":      entry.get("link", ""),
                "fonte":    feed.feed.get("title", ""),
                "data":     dt,
            })
        return itens
    except Exception as e:
        print(f"[news] _buscar_feed({url}): {e}")
        return []


def buscar_noticias_coin(coin_id: str, nome: str | None = None) -> list[dict]:
    """
    Busca notícias recentes sobre o coin via Google News RSS.
    Usa o nome do projeto se disponível, senão o coin_id.
    """
    termo = nome or coin_id
    # Google News RSS — sem autenticação
    url = f"{API_URLS['google_news']}?q={termo}+cryptocurrency&hl=en-US&gl=US&ceid=US:en"
    return _buscar_feed(url)


def buscar_noticias_macro() -> list[dict]:
    """Notícias macro crypto: Bitcoin, regulação, Fed, mercado cripto."""
    termos = ["Bitcoin+crypto+market", "crypto+regulation", "Federal+Reserve+crypto"]
    noticias = []
    for termo in termos:
        url = f"{API_URLS['google_news']}?q={termo}&hl=en-US&gl=US&ceid=US:en"
        noticias.extend(_buscar_feed(url, max_itens=10))
    return noticias


def filtrar_relevantes(noticias: list[dict], coin_id: str, nome: str | None = None) -> list[dict]:
    """
    Filtra notícias mantendo apenas as mais relevantes para o coin.
    Usa palavras-chave definidas em mappings.NEWS_KEYWORDS.
    """
    keywords = NEWS_KEYWORDS.get(coin_id, set())
    if nome:
        keywords = keywords | {nome.lower(), coin_id.lower()}

    relevantes = []
    for n in noticias:
        texto = (n["titulo"] + " " + n["resumo"]).lower()
        if any(kw in texto for kw in keywords):
            relevantes.append(n)

    # Ordena por data (mais recente primeiro), tratando None
    return sorted(relevantes, key=lambda x: x["data"] or datetime.min.replace(tzinfo=timezone.utc),
                  reverse=True)


def preparar_noticias_para_ia(noticias: list[dict], max_noticias: int = 15) -> str:
    """
    Formata lista de notícias como texto estruturado para input do Gemini.
    Retorna string vazia se não houver notícias.
    """
    if not noticias:
        return ""
    linhas = []
    for i, n in enumerate(noticias[:max_noticias], 1):
        data_str = n["data"].strftime("%Y-%m-%d") if n["data"] else "data desconhecida"
        linhas.append(f"{i}. [{data_str}] {n['titulo']} ({n['fonte']})")
        if n["resumo"]:
            resumo = n["resumo"][:200].strip()
            linhas.append(f"   {resumo}")
    return "\n".join(linhas)