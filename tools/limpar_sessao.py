"""
tools/limpar_sessao.py
Remove apenas os artefatos intermediários gerados durante uma sessão de melhorias.

Filosofia: cirúrgico, nunca destrutivo em massa.

Critério de remoção de PDFs: coin ID E data devem coincidir com uma avaliação
existente. Um PDF de ethereum de 2 semanas atrás nunca será tocado mesmo que
ethereum tenha sido analisado nesta sessão.

Arquivos removidos:
  - outputs/pdfs/<COIN>_<DATA>_<HHMM>.pdf   onde (COIN, DATA) existe em avaliação
  - outputs/avaliacoes/<COIN>_avaliacao_v*_<DATA>.md

Nunca toca em:
  - outputs/backlog_melhorias.md
  - outputs/avaliacoes/.rotacao.txt
  - outputs/avaliacoes/.gitkeep
  - PDFs sem avaliação correspondente (mesmo coin, mesma data)
  - Qualquer arquivo de código
"""

import re
from pathlib import Path

ROOT           = Path(__file__).resolve().parent.parent
PDFS_DIR       = ROOT / "outputs" / "pdfs"
AVALIACOES_DIR = ROOT / "outputs" / "avaliacoes"

# Padrão exclusivo de avaliar.py: COIN_avaliacao_vN_YYYYMMDD.md
_PAD_AVALIACAO = re.compile(r"^(.+?)_avaliacao_v\d+.*?_(\d{8})\.md$", re.IGNORECASE)

# Padrão de PDF gerado pelo pipeline: COIN_YYYYMMDD_HHMM.pdf
_PAD_PDF = re.compile(r"^(.+?)_(\d{8})_\d{4}\.pdf$", re.IGNORECASE)


def _chaves_sessao() -> set[tuple[str, str]]:
    """Retorna set de (coin_upper, data_yyyymmdd) das avaliações existentes."""
    if not AVALIACOES_DIR.exists():
        return set()
    chaves = set()
    for f in AVALIACOES_DIR.iterdir():
        m = _PAD_AVALIACAO.match(f.name)
        if m:
            chaves.add((m.group(1).upper(), m.group(2)))
    return chaves


def _avaliacoes_da_sessao() -> list[Path]:
    if not AVALIACOES_DIR.exists():
        return []
    return sorted(
        f for f in AVALIACOES_DIR.iterdir()
        if _PAD_AVALIACAO.match(f.name)
    )


def _pdfs_da_sessao(chaves: set[tuple[str, str]]) -> list[Path]:
    """Retorna apenas os PDFs cujo (coin, data) coincide com uma avaliação."""
    if not PDFS_DIR.exists() or not chaves:
        return []
    resultado = []
    for pdf in PDFS_DIR.glob("*.pdf"):
        m = _PAD_PDF.match(pdf.name)
        if m and (m.group(1).upper(), m.group(2)) in chaves:
            resultado.append(pdf)
    return sorted(resultado)


def main():
    chaves     = _chaves_sessao()
    avaliacoes = _avaliacoes_da_sessao()

    if not avaliacoes:
        print("Nenhuma avaliação de sessão encontrada — nada a remover.")
        return

    pdfs = _pdfs_da_sessao(chaves)

    coins_datas = sorted(f"{c} ({d[:4]}-{d[4:6]}-{d[6:]})" for c, d in chaves)
    print(f"Pares (coin, data) da sessão: {', '.join(coins_datas)}\n")

    print("Arquivos que serão removidos:")
    for f in pdfs:
        print(f"  [PDF]       {f.name}")
    for f in avaliacoes:
        print(f"  [avaliação] {f.name}")

    if not pdfs and not avaliacoes:
        print("  (nenhum)")
        return

    preservados_pdf = sorted(
        f for f in PDFS_DIR.glob("*.pdf") if f not in pdfs
    )
    if preservados_pdf:
        print("\nPDFs preservados (não fazem parte desta sessão):")
        for f in preservados_pdf:
            print(f"  {f.name}")

    print("\nRemovendo...")
    for f in pdfs:
        f.unlink()
        print(f"  removido: {f.name}")
    for f in avaliacoes:
        f.unlink()
        print(f"  removido: {f.name}")

    print(f"\nConcluído: {len(pdfs)} PDF(s) e {len(avaliacoes)} avaliação(ões) removidos.")


if __name__ == "__main__":
    main()
