# senai-agent — Contexto do Projeto

## Objetivo do agente
Agente SenaiEmpresaAssistant especializado no portal SENAI Para Sua Empresa
(https://www.senai.portaldaindustria.com.br/para-sua-empresa).
Responde sobre soluções corporativas e realiza inscrições via MCP Server.

## Stack tecnológico
- Python 3.10+, watsonx Orchestrate ADK
- MCP Server STDIO (senai_empresa_mcp)
- IBM Cloud Code Engine (deploy serverless)
- IBM Cloud Container Registry (imagens Docker)

## Estrutura de pastas
- `agents/senai_empresa_agent/` — definição do agente ADK
- `mcp_server/senai_empresa_mcp/` — MCP Server Python (tools SENAI)
- `scripts/`    — scripts de deploy
- `.bob/`       — configuração IBM Bob

## Variáveis de ambiente obrigatórias (em .env — nunca commitar)
- BOB_API_KEY, ORCHESTRATE_API_KEY, ORCHESTRATE_INSTANCE_URL
- IBM_CLOUD_API_KEY, IBM_CLOUD_REGION, CODE_ENGINE_PROJECT

## Comandos importantes
- Instalar deps:  pip install -r requirements.txt
- Testes:         pytest tests/ -v --cov
- IBM Bob:        Abra o painel de chat do IBM Bob
- Deploy:         bash scripts/deploy.sh

## Padrões e convenções
- Type hints obrigatórios em todas as funções públicas
- Docstrings Google Style para classes e funções
- Confirmar inscrições antes de submeter ao portal SENAI
- Cobertura mínima de testes: 80%
