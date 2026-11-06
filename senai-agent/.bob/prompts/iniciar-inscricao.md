---
name: iniciar-inscricao
description: Inicia o processo de inscrição de uma empresa em um programa SENAI Para Sua Empresa
---

Conduza o processo de inscrição em etapas:

1. Use `listar_solucoes` para confirmar que a solução {{SOLUCAO}} está disponível
2. Colete os dados obrigatórios de forma conversacional (um por vez):
   - Razão social da empresa
   - CNPJ (14 dígitos numéricos)
   - Nome completo do responsável
   - E-mail corporativo
   - Telefone com DDD
3. Exiba resumo completo e aguarde confirmação explícita ("confirmar" / "sim")
4. Chame `realizar_inscricao` do MCP senai-empresa apenas após confirmação
5. Apresente o protocolo e próximos passos ao usuário
