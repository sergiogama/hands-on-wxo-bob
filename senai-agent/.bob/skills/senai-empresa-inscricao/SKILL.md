---
name: senai-empresa-inscricao
description: Conduz o fluxo de inscrição de uma empresa em soluções SENAI Para Sua Empresa via MCP Server
---

Ao receber solicitação de inscrição em programa SENAI:

1. Confirme com o usuário a solução de interesse (use `listar_solucoes` se necessário)
2. Colete os dados obrigatórios um por vez, de forma conversacional:
   - Razão social da empresa
   - CNPJ (apenas números, 14 dígitos)
   - Nome completo do responsável
   - E-mail corporativo do responsável
   - Telefone com DDD
   - Mensagem adicional (opcional)
3. Exiba um resumo completo e peça confirmação explícita do usuário
4. Somente após confirmação, chame a tool `realizar_inscricao` do MCP Server senai-empresa
5. Informe o protocolo gerado e os próximos passos

## Regras
- NUNCA submeta a inscrição sem confirmação explícita
- Valide o CNPJ: 14 dígitos numéricos
- Valide o e-mail: deve conter @ e domínio corporativo
