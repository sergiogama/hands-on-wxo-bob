---
name: generate-unit-tests
description: Gera testes unitários Python com pytest e unittest.mock seguindo padrão AAA
---

Ao gerar testes unitários Python:

## Obrigatório
- Framework: pytest (fixtures, parametrize, raises)
- Mocks: unittest.mock (patch, MagicMock, AsyncMock)
- Estrutura: Arrange / Act / Assert com comentários
- Nomenclatura: test_deve_[comportamento]_quando_[condicao]

## Cobertura mínima
- Caminho feliz (happy path)
- Valores None, "", [], {}
- Exceções esperadas (pytest.raises)
- Valores de borda (0, -1, string vazia, lista muito grande)
