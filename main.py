import sys
import numpy as np
from datetime import datetime

from config.settings import ATIVO, BENCHMARK, TAXA_LIVRE_RISCO
from data.providers.crypto_provider import coletar_dados
from data.field_mapper import validar_dados_minimos
from quant.metrics import calcular_todas as calcular_metricas_quant
from quant.scoring import calcular_score_quant
from quant import charts as quant_charts
from fundamental.metrics import calcular_todos_pilares
from fundamental.scoring import calcular_score_fundamental
from fundamental.validation import validar_pilares, resumo_cobertura
from fundamental import charts as fund_charts
from macro.analysis import calcular_scores_macro, interpretar_macro
from macro.ai_analyst import gerar_analise_ia
from macro import charts as macro_charts
from narrative.generator import gerar_narrativa_completa
from pdf.renderer_html import gerar_pdf


def _titulo(texto: str) -> None:
    largura = 60
    print(f"\n{'─' * largura}")
    print(f"  {texto}")
    print(f"{'─' * largura}")


def _ok(texto: str) -> None:
    print(f"  ✓ {texto}")


def _aviso(texto: str) -> None:
    print(f"  ⚠ {texto}")


def _erro(texto: str) -> None:
    print(f"  ✗ {texto}")


def main(coin_id: str = ATIVO, benchmark_id: str = BENCHMARK) -> None:
    inicio = datetime.now()

    print(f"\n{'═' * 60}")
    print(f"  CRYPTO RESEARCH ENGINE")
    print(f"  Ativo: {coin_id.upper()}  |  Benchmark: {benchmark_id.upper()}")
    print(f"  {inicio.strftime('%d/%m/%Y %H:%M')}")
    print(f"{'═' * 60}")

    # ── 1. Coleta de dados ────────────────────────────────────────────────
    _titulo("1. Coleta de Dados")
    dados = coletar_dados(coin_id, benchmark_id)

    ok, avisos_validacao = validar_dados_minimos(dados)
    dados["avisos_validacao"] = avisos_validacao

    if not ok:
        for aviso in avisos_validacao:
            _erro(aviso)
        print("\n  Dados insuficientes para gerar o relatório. Abortando.")
        sys.exit(1)

    if avisos_validacao:
        for aviso in avisos_validacao:
            _aviso(aviso)

    nome    = dados["dados_mercado"].get("nome", coin_id)
    simbolo = dados["dados_mercado"].get("simbolo", coin_id.upper())
    _ok(f"{nome} ({simbolo}) · categoria: {dados.get('categoria', 'N/D')}")
    _ok(f"Peers: {dados['peers']}")
    _ok(f"Histórico: {len(dados['historico_ativo'])} dias")

    # ── 2. Análise Quantitativa ───────────────────────────────────────────
    _titulo("2. Análise Quantitativa")
    metricas_quant = calcular_metricas_quant(
        dados["historico_ativo"],
        dados["historico_benchmark"],
        TAXA_LIVRE_RISCO,
    )
    scores_quant = calcular_score_quant(metricas_quant)
    _ok(f"Score Quant: {scores_quant.get('score_quant', 'N/D'):.2f} / 10")

    graficos_quant = quant_charts.gerar_todos(
        historico_ativo   = dados["historico_ativo"],
        historico_bench   = dados["historico_benchmark"],
        scores            = scores_quant,
        nome              = nome,
        simbolo           = simbolo,
        nome_bench        = benchmark_id.upper(),
        coin_id           = coin_id,
    )
    _ok(f"Gráficos quant gerados: {sum(1 for v in graficos_quant.values() if v)}")

    # ── 3. Análise Fundamentalista ────────────────────────────────────────
    _titulo("3. Análise Fundamentalista")
    resultado_pilares = calcular_todos_pilares(dados)
    df_peers          = resultado_pilares["df_peers"]

    avisos_fund = validar_pilares(resultado_pilares)
    cobertura   = resumo_cobertura(resultado_pilares)
    for aviso in avisos_fund:
        _aviso(aviso)

    scores_fund = calcular_score_fundamental(resultado_pilares, df_peers, coin_id)
    _ok(f"Score Fundamental: {scores_fund.get('score_fundamental', 'N/D')}")
    _ok(f"Pilares ativos: {resultado_pilares['pilares_ativos']}")

    graficos_fund = fund_charts.gerar_todos(
        df_peers          = df_peers,
        scores_fundamental = scores_fund,
        nome              = nome,
        coin_id           = coin_id,
    )
    _ok(f"Gráficos fundamentalistas gerados: {sum(1 for v in graficos_fund.values() if v)}")

    # ── 4. Análise Macro ──────────────────────────────────────────────────
    _titulo("4. Análise Macro")
    categoria     = dados.get("categoria")
    macro         = dados["macro"]
    scores_macro  = calcular_scores_macro(macro, categoria)
    sinais_macro  = interpretar_macro(macro, scores_macro)
    _ok(f"Score Macro: {scores_macro.get('score_macro', 'N/D')}")
    _ok(f"Fear & Greed: {sinais_macro.get('fear_greed', 'N/D')}")
    _ok(f"Fase Halving: {macro.get('fase_ciclo', 'N/D')}")

    graficos_macro = macro_charts.gerar_todos(
        macro        = macro,
        scores_macro = scores_macro,
        nome         = nome,
        coin_id      = coin_id,
    )
    _ok(f"Gráficos macro gerados: {sum(1 for v in graficos_macro.values() if v)}")

    # ── 5. Análise IA (Gemini) ────────────────────────────────────────────
    _titulo("5. Análise IA (Gemini)")
    analise_ia = gerar_analise_ia(
        nome           = nome,
        simbolo        = simbolo,
        categoria      = categoria,
        sinais_macro   = sinais_macro,
        noticias_texto = dados.get("noticias_texto", ""),
        scores_macro   = scores_macro,
        dados_mercado  = dados["dados_mercado"],
    )
    if analise_ia:
        _ok(f"Análise IA gerada ({analise_ia.get('modelo_ia', '?')})")
        _ok(f"Score IA: {analise_ia.get('score_ia', 'N/D')}")
    else:
        _aviso("Análise IA não disponível (GEMINI_API_KEY ausente ou erro)")

    # ── 6. Narrativa ──────────────────────────────────────────────────────
    _titulo("6. Geração de Narrativa")
    narrativa = gerar_narrativa_completa(
        dados          = dados,
        metricas_quant = metricas_quant,
        scores_quant   = scores_quant,
        pilares        = resultado_pilares["pilares"],
        scores_fund    = scores_fund,
        macro          = macro,
        scores_macro   = scores_macro,
        sinais_macro   = sinais_macro,
        analise_ia     = analise_ia,
    )
    sc = narrativa["score_integrado"]
    _ok(f"Score Integrado Final: {sc['score_final']} / 10 → {sc['label_final']}")

    # ── 7. PDF ────────────────────────────────────────────────────────────
    _titulo("7. Geração do PDF")
    caminho_pdf = gerar_pdf(
        narrativa      = narrativa,
        graficos_quant = graficos_quant,
        graficos_fund  = graficos_fund,
        graficos_macro = graficos_macro,
        df_peers       = df_peers,
        coin_id        = coin_id,
    )

    # ── Sumário final ─────────────────────────────────────────────────────
    duracao = (datetime.now() - inicio).total_seconds()
    print(f"\n{'═' * 60}")
    print(f"  ANÁLISE CONCLUÍDA em {duracao:.0f}s")
    print(f"{'═' * 60}")
    print(f"  Ativo:          {nome} ({simbolo})")
    print(f"  Score Final:    {sc['score_final']} / 10  →  {sc['label_final']}")
    print(f"  PDF:            {caminho_pdf}")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    # Permite sobrescrever ativo e benchmark pela linha de comando:
    # python main.py bitcoin
    # python main.py solana ethereum
    args = sys.argv[1:]
    coin      = args[0] if len(args) >= 1 else ATIVO
    benchmark = args[1] if len(args) >= 2 else BENCHMARK
    main(coin, benchmark)