import asyncio
import markdown as _md
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUTS_DIR   = Path("outputs/pdfs")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _carregar_imagem_base64(caminho: Path | None) -> str:
    """Converte imagem em base64 para embed no HTML."""
    if not caminho or not Path(caminho).exists():
        return ""
    import base64
    with open(caminho, "rb") as f:
        dados = base64.b64encode(f.read()).decode()
    ext = Path(caminho).suffix.lstrip(".")
    return f"data:image/{ext};base64,{dados}"


def _preparar_graficos(graficos_quant: dict, graficos_fund: dict,
                        graficos_macro: dict) -> dict:
    """Converte todos os caminhos de gráficos para base64."""
    resultado = {}
    todos = {**graficos_quant, **graficos_fund, **graficos_macro}
    for nome, caminho in todos.items():
        resultado[nome] = _carregar_imagem_base64(caminho)
    return resultado


def renderizar_html(narrativa: dict, graficos_quant: dict, graficos_fund: dict,
                     graficos_macro: dict, df_peers) -> str:
    """Renderiza o template Jinja2 e retorna HTML completo."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    env.filters["markdown"] = lambda text: _md.markdown(
        text or "", extensions=["nl2br"]
    )

    graficos_b64 = _preparar_graficos(graficos_quant, graficos_fund, graficos_macro)

    # Tabela de peers para apêndice
    peers_tabela = []
    if df_peers is not None and not df_peers.empty:
        import numpy as np
        for idx, row in df_peers.iterrows():
            peers_tabela.append({
                "coin_id":   idx,
                "simbolo":   row.get("simbolo", idx.upper()),
                "mcap":      f"${row.get('mcap_usd', 0)/1e9:.2f}B" if not isinstance(row.get('mcap_usd'), float) or not __import__('numpy').isnan(row.get('mcap_usd', float('nan'))) else "N/D",
                "volume":    f"${row.get('volume_24h', 0)/1e6:.0f}M" if not isinstance(row.get('volume_24h'), float) or not __import__('numpy').isnan(row.get('volume_24h', float('nan'))) else "N/D",
                "fdv_mcap":  f"{row.get('fdv_mcap', float('nan')):.2f}x" if not __import__('numpy').isnan(row.get('fdv_mcap', float('nan'))) else "N/D",
                "rank":      f"#{int(row.get('rank_mercado', 0))}" if not __import__('numpy').isnan(row.get('rank_mercado', float('nan'))) else "N/D",
            })

    template = env.get_template("relatorio.html")
    return template.render(
        narrativa     = narrativa,
        graficos      = graficos_b64,
        peers_tabela  = peers_tabela,
        data_geracao  = datetime.now().strftime("%d/%m/%Y às %H:%M"),
    )


async def _html_para_pdf(html: str, caminho_pdf: Path) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path          = str(caminho_pdf),
            format        = "A4",
            print_background = True,
            margin        = {"top": "0mm", "bottom": "0mm",
                             "left": "0mm", "right": "0mm"},
        )
        await browser.close()


def gerar_pdf(narrativa: dict, graficos_quant: dict, graficos_fund: dict,
               graficos_macro: dict, df_peers, coin_id: str) -> Path:
    """Pipeline completo: narrativa → HTML → PDF."""
    html = renderizar_html(narrativa, graficos_quant, graficos_fund,
                            graficos_macro, df_peers)

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M")
    nome_pdf   = f"{coin_id}_{timestamp}.pdf"
    caminho    = OUTPUTS_DIR / nome_pdf

    asyncio.run(_html_para_pdf(html, caminho))
    print(f"[pdf] Gerado: {caminho}")
    return caminho