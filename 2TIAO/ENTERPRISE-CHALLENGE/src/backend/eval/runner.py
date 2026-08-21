"""Runner do eval — executa os casos e gera o relatório."""

from datetime import datetime

from agents import app
from eval.cases import EVAL_CASES
from eval.criteria import (
    EvalResult,
    avaliar_disclaimer,
    avaliar_grounding,
    avaliar_guardrails,
    avaliar_recusa,
)


def avaliar_caso(caso: dict) -> EvalResult:
    """Executa o agente para um caso e avalia a resposta."""
    result = EvalResult(case_id=caso["id"], pergunta=caso["pergunta"])

    try:
        output = app.invoke({"question": caso["pergunta"]})
        resposta = output.get("answer", "")
        result.resposta_resumo = resposta[:200] + "..." if len(resposta) > 200 else resposta

        # 1. Disclaimer
        ok, nota = avaliar_disclaimer(resposta)
        result.tem_disclaimer = ok
        if nota:
            result.notas.append(nota)
            result.passou = False

        # 2. Grounding
        if caso.get("deve_mencionar"):
            notas_grounding = avaliar_grounding(resposta, caso["deve_mencionar"])
            result.notas.extend(notas_grounding)
            result.tem_grounding = len(notas_grounding) == 0

        # 3. Guardrails
        violacoes = avaliar_guardrails(resposta)
        result.violacoes_guardrail = violacoes
        if violacoes:
            result.notas.append(f"🚨 Violações: {violacoes}")
            result.passou = False

        # 4. Recusa (se esperada)
        if caso.get("espera_recusa") and not avaliar_recusa(resposta):
            result.notas.append(
                "⚠️ Esperava recusa/redirecionamento mas agente respondeu normalmente"
            )

        if not result.notas:
            result.notas.append("✅ Todos os critérios atendidos")

    except Exception as e:
        result.passou = False
        result.notas.append(f"💥 Erro na execução: {e}")

    return result


def executar_eval() -> list[EvalResult]:
    """Executa o eval completo e imprime o relatório."""
    print("=" * 60)
    print("  EVAL — Genera Intelligence Agent")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    resultados: list[EvalResult] = []
    total = len(EVAL_CASES)
    aprovados = 0

    for i, caso in enumerate(EVAL_CASES, 1):
        print(f"\n[{i}/{total}] Caso {caso['id']}: {caso['pergunta']}")
        print("-" * 40)

        resultado = avaliar_caso(caso)
        resultados.append(resultado)

        if resultado.passou:
            aprovados += 1
            print("  ✅ APROVADO")
        else:
            print("  ❌ REPROVADO")

        for nota in resultado.notas:
            print(f"     {nota}")

        if resultado.resposta_resumo:
            print(f"  📝 {resultado.resposta_resumo[:100]}...")

    # Relatório final
    print("\n" + "=" * 60)
    print("  RESULTADO FINAL")
    print("=" * 60)
    taxa = 100 * aprovados / total if total else 0
    print(f"  Aprovados: {aprovados}/{total} ({taxa:.0f}%)")
    print(f"  Reprovados: {total - aprovados}/{total}")

    categorias = sorted(set(c["categoria"] for c in EVAL_CASES))
    for cat in categorias:
        casos_cat = [r for r, c in zip(resultados, EVAL_CASES) if c["categoria"] == cat]
        aprovados_cat = sum(1 for r in casos_cat if r.passou)
        print(f"    [{cat.upper()}] {aprovados_cat}/{len(casos_cat)}")

    print("=" * 60)
    return resultados
