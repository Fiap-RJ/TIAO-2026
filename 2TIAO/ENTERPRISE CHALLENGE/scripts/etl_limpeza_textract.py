import json
import re

def processar_laudo_bruto(texto_sujo, id_paciente="uuid-anonimo"):
    # 1. Estrutura base do JSON que o backend espera
    laudo_limpo = {
        "paciente_id": id_paciente,
        "paineis": []
    }
    
    marcadores_encontrados = []

    # 2. A "Mágica" do RegEx: Ensinando o Python a ler os padrões no texto
    # Essa regra procura a palavra "Gene:", pega o código dele, pula espaços/hifens e pega a predisposição.
    padrao_busca = r"(?i)Gene:\s*([A-Z0-9]+)\s*[-:]\s*Predisposição:\s*([^.]+)"
    
    # 3. Executando a busca no texto sujo
    resultados = re.findall(padrao_busca, texto_sujo)

    # 4. Organizando o que foi encontrado
    for gene, predisposicao in resultados:
        marcadores_encontrados.append({
            "caracteristica": "Não informada no texto bruto",
            "gene": gene.strip(),
            "predisposicao": predisposicao.strip(),
            "recomendacao": "Consulte o especialista."
        })

    # 5. Adicionando ao painel se encontrou algo
    if marcadores_encontrados:
        laudo_limpo["paineis"].append({
            "categoria": "Dados Extraídos do PDF",
            "marcadores": marcadores_encontrados
        })

    return json.dumps(laudo_limpo, indent=2, ensure_ascii=False)


# --- ÁREA DE TESTE ---
if __name__ == "__main__":
    # Simulando um texto todo quebrado vindo do AWS Textract
    texto_do_pdf = """
    RESULTADO DO EXAME GENERA FIT... %$#@
    Gene: WNT16 - Predisposição: Menor densidade óssea.
    ... ruídos de leitura ...
    Gene: ACTN3 : Predisposição: Maior aptidão para esportes de força e explosão.
    Fim do laudo.
    """

    print("--- Texto Sujo Original ---")
    print(texto_do_pdf)
    
    print("\n--- JSON Limpo Pronto para a IA ---")
    resultado_json = processar_laudo_bruto(texto_do_pdf)
    print(resultado_json)