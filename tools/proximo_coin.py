"""
tools/proximo_coin.py
Retorna o próximo coin da rotação de melhorias e avança o estado.

Uso: python tools/proximo_coin.py
Saída: linha única com o coin ID (ex: ethereum) — pronto para ser capturado.

Estado persistido em outputs/avaliacoes/.rotacao.txt
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from config.mappings import COINS_ROTACAO

ARQUIVO_ESTADO = pathlib.Path("outputs/avaliacoes/.rotacao.txt")


def _ler_indice_atual() -> int:
    if ARQUIVO_ESTADO.exists():
        try:
            return int(ARQUIVO_ESTADO.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    return -1


def _salvar_indice(indice: int) -> None:
    ARQUIVO_ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_ESTADO.write_text(str(indice), encoding="utf-8")


def proximo_coin() -> str:
    indice_atual = _ler_indice_atual()
    proximo = (indice_atual + 1) % len(COINS_ROTACAO)
    _salvar_indice(proximo)
    coin = COINS_ROTACAO[proximo]
    print(coin)
    return coin


if __name__ == "__main__":
    proximo_coin()
