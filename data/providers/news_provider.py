import re
import time
import random
import feedparser
import numpy as np
from datetime import datetime, timezone
from config.mappings import API_URLS, NEWS_KEYWORDS


def _strip_html(text: str) -> str:
    """Remove tags HTML e decodifica entidades básicas."""
    text = re.sub(r"<[^>]+>", "", text or "")
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    return text.strip()

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# Intervalo base entre requisições ao Google News (segundos)
_NEWS_SLEEP_MIN = 2.0
_NEWS_SLEEP_MAX = 4.5


def _sleep_news() -> None:
    """Pausa aleatória entre requisições ao Google News para evitar bloqueio de IP."""
    time.sleep(random.uniform(_NEWS_SLEEP_MIN, _NEWS_SLEEP_MAX))


def _buscar_feed(url: str, max_itens: int = 20) -> list[dict]:
    """Parseia um feed RSS/Atom e retorna lista de itens normalizados."""
    try:
        ua = random.choice(_USER_AGENTS)
        feed = feedparser.parse(url, request_headers={"User-Agent": ua})
        itens = []
        for entry in feed.entries[:max_itens]:
            publicado = entry.get("published_parsed") or entry.get("updated_parsed")
            dt = datetime(*publicado[:6], tzinfo=timezone.utc) if publicado else None
            itens.append({
                "titulo":   _strip_html(entry.get("title", "")),
                "resumo":   _strip_html(entry.get("summary", "")),
                "url":      entry.get("link", ""),
                "fonte":    _strip_html(feed.feed.get("title", "")),
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
    url = f"{API_URLS['google_news']}?q={termo}+cryptocurrency&hl=en-US&gl=US&ceid=US:en"
    return _buscar_feed(url)


def buscar_noticias_macro() -> list[dict]:
    """Notícias macro crypto: Bitcoin, regulação, Fed, mercado cripto."""
    termos = ["Bitcoin+crypto+market", "crypto+regulation", "Federal+Reserve+crypto"]
    noticias = []
    for i, termo in enumerate(termos):
        if i > 0:
            _sleep_news()
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