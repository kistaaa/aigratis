## Inputs
- prompt.yaml : o seu prompt, com mensagem de sistema incluido
- models.yaml: lista de provedores e modelos

## Scripts
- enviar_prompt.py : envia o prompt do yaml para os modelos da lista até receber uma resposta, se não receber envia pro próximo
- testar_models.py : testa a conexão com cada modelo na lista e mostra status e erros
