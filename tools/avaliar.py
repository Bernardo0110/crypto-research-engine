"""
tools/avaliar.py
Avalia o PDF mais recente do projeto usando Gemini 2.5 Flash.
Salva o resultado em outputs/avaliacoes/ com nome versionado.

Uso: python tools/avaliar.py
"""

import os
import pathlib
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELO         = "gemini-2.5-flash"
DIR_PDFS       = pathlib.Path("outputs/pdfs")
DIR_AVALIACOES = pathlib.Path("outputs/avaliacoes")
CAMINHO_PROMPT = pathlib.Path("prompts/avaliar_relatorio.md")


def _pdf_mais_recente() -> pathlib.Path:
    pdfs = sorted(DIR_PDFS.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {DIR_PDFS}")
    return pdfs[0]


def _proximo_numero_versao() -> int:
    DIR_AVALIACOES.mkdir(parents=True, exist_ok=True)
    existentes = list(DIR_AVALIACOES.glob("*_avaliacao_v*.md"))
    if not existentes:
        return 1
    numeros = []
    for f in existentes:
        try:
            n = int(f.stem.split("_v")[-1])
            numeros.append(n)
        except ValueError:
            pass
    return max(numeros, default=0) + 1


def avaliar():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY não encontrada no .env")

    pdf = _pdf_mais_recente()
    prompt = CAMINHO_PROMPT.read_text(encoding="utf-8")
    versao = _proximo_numero_versao()
    coin_id = pdf.stem.split("_")[0]
    data_hoje = datetime.now().strftime("%Y%m%d")
    caminho_saida = DIR_AVALIACOES / f"{coin_id}_avaliacao_v{versao}_{data_hoje}.md"

    print(f"📄 PDF: {pdf.name}")
    print(f"🤖 Modelo: {MODELO}")
    print(f"💾 Saída: {caminho_saida}")
    print("⏳ Enviando para Gemini...")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODELO,
        contents=[
            types.Part.from_bytes(data=pdf.read_bytes(), mime_type="application/pdf"),
            prompt,
        ],
    )

    resultado = response.text
    caminho_saida.write_text(resultado, encoding="utf-8")
    print(f"✅ Avaliação salva em {caminho_saida}")
    return caminho_saida


if __name__ == "__main__":
    avaliar()
