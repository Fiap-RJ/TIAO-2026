# Dados

- `novo_caso.json`: o `novo_caso` literal do enunciado, usado como entrada padrão da CLI (`python main.py`). A chave `"disponibilidade recursos"` (com espaço) foi mantida como no enunciado; o schema `DadosPaciente` a normaliza para `disponibilidade_recursos`.
- Base sintética: não é versionada. Ela é regerada por código, de forma determinística (seed 42, n = 5000), pelo notebook `src/CardioIA_Fase6_Modelo_Preditivo.ipynb` e por `ml.dataset.gerar_base_sintetica()`. Nenhum CSV é salvo nesta pasta.
- `*.db`: histórico de sessões (`SQLiteSession`) criado em tempo de execução e ignorado pelo Git.
