# Hands-On: IBM Bob + watsonx Orchestrate
## Criando e Usando Agentes com IBM Bob Shell e ADK Python · Deploy no IBM Cloud Code Engine

**Público-alvo:** Desenvolvedores e analistas de TI  
**Duração estimada:** 4 horas  
**Pré-requisitos:** Node.js 18+, Python 3.10+, Docker, conta IBM Cloud, conta IBM watsonx Orchestrate, acesso ao Jira Cloud

---

## Módulo 1 — Visão Geral da Solução

### O que é IBM Bob?
IBM Bob é um assistente de IA para desenvolvedores disponível como aplicativo standalone (IBM Bob IDE) e como ferramenta de linha de comando (**Bob Shell**). Neste workshop utilizamos o **Bob Shell** — sem necessidade de VS Code ou extensão —, que roda diretamente no terminal e oferece as mesmas capacidades agentic: leitura de arquivos, geração de código, execução de comandos, MCP servers, hooks, skills e modos customizados.

### O que é watsonx Orchestrate?
IBM watsonx Orchestrate é uma plataforma de orquestração de agentes de IA que permite criar, compor e implantar agentes inteligentes capazes de executar fluxos de trabalho complexos integrando ferramentas externas (Jira, Salesforce, SAP etc.) via MCP, APIs REST e toolkits nativos.

### O que é IBM Cloud Code Engine?
Code Engine é uma plataforma serverless totalmente gerenciada da IBM Cloud que executa workloads em contêineres sem necessidade de gerenciar infraestrutura. Usaremos o Code Engine para hospedar o agente Python após o desenvolvimento.

### Fluxo do workshop

```
[Bob Shell]  →  desenvolve e testa  →  [Projeto Python + MCP Server]
                                               ↓
                                    [Docker image → ICR]
                                               ↓
                                  [IBM Cloud Code Engine (deploy)]
                                               ↓
                               [watsonx Orchestrate consome o agente]
```

---

## Módulo 2 — Instalando e Configurando o IBM Bob Shell

### 2.1 Instalação — Método recomendado (script oficial)

**macOS / Linux:**
```bash
curl -fsSL https://bob.ibm.com/download/bobshell.sh | bash
```

**Windows (PowerShell):**
```powershell
powershell -ep Bypass "iwr https://bob.ibm.com/download/bobshell.ps1 -OutFile $env:TMP\bob.ps1; &$env:TMP\bob.ps1"
```

**Instalação manual via npm (alternativa):**
```bash
npm install --registry=https://registry.npmjs.org/ \
  --allow-scripts=@officecli/officecli -g @ibm/bob
```

**Verificar instalação:**
```bash
bob --version
```

### 2.2 Autenticação no Bob Shell

**Método 1 — SSO / IBMid (sessões interativas):**
```bash
bob chat
# Bob abre bob.ibm.com/login no browser automaticamente
# Faça login com seu IBMid ou SSO corporativo
```

**Método 2 — API Key (automação / CI/CD):**
```bash
# 1. Acesse https://bob.ibm.com → Account → API Keys → Create API Key
#    Defina o Scope como "Inference"
#    Copie e guarde o valor gerado — não será exibido novamente

# 2. Configure a variável de ambiente
export BOB_API_KEY="<SUA_BOB_API_KEY>"

# Para tornar permanente (macOS/Linux):
echo 'export BOB_API_KEY="<SUA_BOB_API_KEY>"' >> ~/.zshrc
source ~/.zshrc

# 3. Inicie uma sessão interativa
bob chat

# 4. Ou execute um prompt único (não-interativo)
bob run "Liste os arquivos do projeto atual"
```

> **Atenção:** Nunca compartilhe sua API Key. Se usar API Key do tipo `general` em vez de `inference`, adicione `--team-id <SEU_TEAM_ID>` ao comando.

### 2.3 Primeira sessão com Bob Shell

```bash
# Criar pasta do projeto
mkdir senai-agent && cd senai-agent

# Iniciar sessão interativa na pasta do projeto
bob chat

# Dentro do chat, gerar contexto do projeto
/init

# Listar modos disponíveis
/mode
```

---

## Módulo 3 — Configuração do Ambiente Python e watsonx Orchestrate

### 3.1 Pré-requisitos Python

```bash
# Verificar Python (>= 3.10)
python3 --version

# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Instalar dependências
pip install ibm-watsonx-orchestrate-adk requests python-dotenv
```

### 3.2 Estrutura do projeto Python

```
senai-agent/
├── .env                        ← variáveis de ambiente (NÃO commitar)
├── .env.example                ← template de variáveis (commitar)
├── requirements.txt
├── Dockerfile
├── agents/
│   └── senai_dev_agent/
│       ├── __init__.py
│       ├── agent.py            ← definição do agente ADK
│       └── tools.py            ← tools customizadas
├── mcp_server/
│   └── jira_mcp/
│       ├── __init__.py
│       └── server.py           ← MCP server Python
├── scripts/
│   └── deploy.sh               ← script de deploy no Code Engine
└── .bob/
    ├── mcp.json
    ├── settings.json
    ├── custom_modes.yaml
    ├── skills/
    │   ├── code-review-python/SKILL.md
    │   ├── jira-ticket-update/SKILL.md
    │   └── generate-unit-tests/SKILL.md
    └── prompts/
        ├── iniciar-ticket.md
        ├── code-review.md
        └── gerar-docs.md
```

### 3.3 Arquivo .env.example (template — commitar)

```bash
# ======================================================
# IDENTIDADES E CREDENCIAIS — Copie para .env e preencha
# ======================================================

# IBM Bob Shell
BOB_API_KEY=<SUA_BOB_API_KEY>

# watsonx Orchestrate ADK
ORCHESTRATE_API_KEY=<SUA_ORCHESTRATE_API_KEY>
ORCHESTRATE_INSTANCE_URL=https://api.us-south.watson.ai/v1

# Jira Cloud
JIRA_BASE_URL=https://<SUA_EMPRESA>.atlassian.net
JIRA_EMAIL=<SEU_EMAIL>@<SUA_EMPRESA>.com
JIRA_API_TOKEN=<SEU_JIRA_API_TOKEN>

# IBM Cloud (para deploy no Code Engine)
IBM_CLOUD_API_KEY=<SUA_IBM_CLOUD_API_KEY>
IBM_CLOUD_REGION=us-south
IBM_CLOUD_RESOURCE_GROUP=Default
IBM_CLOUD_REGISTRY_NAMESPACE=<SEU_NAMESPACE_ICR>
CODE_ENGINE_PROJECT=senai-agent-project
```

### 3.4 Carregando variáveis de ambiente

```bash
# Criar .env a partir do template
cp .env.example .env
# Edite o .env com seus valores reais

# No Python, carregue com dotenv:
# from dotenv import load_dotenv
# load_dotenv()
```

### 3.5 Autenticação no watsonx Orchestrate ADK

```bash
# Carregar .env e autenticar
source .env  # ou use o dotenv no Python

# Login via ADK
wx-orchestrate login --api-key $ORCHESTRATE_API_KEY

# Verificar versão
wx-orchestrate --version
```

---

## Módulo 4 — Criando um Agente no watsonx Orchestrate (Interface Web)

### 4.1 Definição do Agente

| Campo | Valor |
|---|---|
| **Nome** | `SenaiDevAssistant` |
| **Descrição** | Agente de suporte ao desenvolvimento de software, capaz de consultar tickets Jira, revisar código e responder dúvidas técnicas de forma contextualizada. |
| **Behavior / Instructions** | Responda sempre em português. Priorize consultas ao Jira antes de sugerir soluções. Nunca execute ações destrutivas sem confirmação explícita do usuário. Quando não souber a resposta, diga claramente e sugira fontes alternativas. |
| **Modelo** | `ibm/granite-3-8b-instruct` |
| **Temperatura** | `0.3` |

### 4.2 Passo a passo na interface web

1. Acesse o console do watsonx Orchestrate
2. Navegue até **Agents** → **Create agent**
3. Preencha **Name**: `SenaiDevAssistant`
4. Cole a **Description** e o **Behavior** da tabela acima
5. Selecione o modelo `ibm/granite-3-8b-instruct`
6. Clique em **Save**

### 4.3 Adicionando conhecimento base (RAG)

1. Na aba **Knowledge**, clique em **Add document**
2. Faça upload do arquivo `knowledge-base-senai.pdf`
3. Aguarde o processamento (indexação vetorial automática)

---

## Módulo 5 — PDF de Conhecimento Base (RAG)

### 5.1 Estrutura recomendada

```
knowledge-base-senai.pdf
├── 1. Padrões de Codificação SENAI
│   ├── Convenções Python (PEP 8, type hints, docstrings)
│   ├── Estrutura de projetos (src layout, pyproject.toml)
│   └── Regras de revisão de código
├── 2. Processo de Desenvolvimento
│   ├── Fluxo GitFlow adotado
│   ├── Critérios de Definition of Done
│   └── Etapas de code review
├── 3. Infraestrutura e Ambientes
│   ├── Ambientes: dev, staging, prod
│   ├── Pipelines CI/CD
│   └── Configurações Jira e IBM Cloud
└── 4. FAQs Técnicas
    ├── Como usar IBM Bob Shell
    ├── Como usar o ADK do watsonx Orchestrate
    └── Como fazer deploy no Code Engine
```

### 5.2 Gerando o documento com Bob Shell

```bash
# Dentro da sessão bob chat:
bob run "Gere um documento Markdown chamado knowledge-base-senai.md com
padrões de codificação Python seguindo PEP 8, processo de desenvolvimento
com GitFlow, FAQs técnicas sobre IBM Bob Shell e watsonx Orchestrate,
e procedimentos de deploy no IBM Cloud Code Engine."

# Converter para PDF com pandoc
pandoc knowledge-base-senai.md -o knowledge-base-senai.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=2cm \
  -V lang=pt-BR
```

---

## Módulo 6 — Criando o Agente Python com ADK

### 6.1 Tools customizadas

Crie `agents/senai_dev_agent/tools.py`:

```python
# agents/senai_dev_agent/tools.py
import os
import requests
from ibm_watsonx_orchestrate.agent_builder.tools import tool


def _jira_headers() -> dict:
    """Retorna os headers de autenticação para a API Jira."""
    import base64
    creds = f"{os.environ['JIRA_EMAIL']}:{os.environ['JIRA_API_TOKEN']}"
    token = base64.b64encode(creds.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }


@tool
def get_jira_ticket(ticket_key: str) -> dict:
    """Busca detalhes de um ticket Jira pelo seu identificador.

    Args:
        ticket_key: Identificador do ticket no formato PROJETO-NUMERO (ex: SCRUM-12)

    Returns:
        Dicionário com key, summary, status, assignee e description do ticket.
    """
    base_url = os.environ["JIRA_BASE_URL"]
    url = f"{base_url}/rest/api/3/issue/{ticket_key}"
    resp = requests.get(url, headers=_jira_headers())
    resp.raise_for_status()
    issue = resp.json()
    return {
        "key": issue["key"],
        "summary": issue["fields"]["summary"],
        "status": issue["fields"]["status"]["name"],
        "assignee": (issue["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
        "description": str(issue["fields"].get("description", "")),
    }


@tool
def list_jira_tickets(project_key: str, status: str = "") -> list:
    """Lista tickets de um projeto Jira, opcionalmente filtrando por status.

    Args:
        project_key: Chave do projeto Jira (ex: SCRUM)
        status: Status para filtrar (ex: "Em andamento"). Deixe vazio para todos.

    Returns:
        Lista de dicionários com key, summary e status de cada ticket.
    """
    base_url = os.environ["JIRA_BASE_URL"]
    jql = f"project={project_key}"
    if status:
        jql += f' AND status="{status}"'
    url = f"{base_url}/rest/api/3/search"
    resp = requests.get(url, headers=_jira_headers(), params={"jql": jql, "maxResults": 20})
    resp.raise_for_status()
    issues = resp.json().get("issues", [])
    return [
        {
            "key": i["key"],
            "summary": i["fields"]["summary"],
            "status": i["fields"]["status"]["name"],
        }
        for i in issues
    ]


@tool
def add_jira_comment(ticket_key: str, comment: str) -> dict:
    """Adiciona um comentário a um ticket Jira.

    Args:
        ticket_key: Identificador do ticket (ex: SCRUM-12)
        comment: Texto do comentário a ser adicionado

    Returns:
        Dicionário confirmando id e autor do comentário criado.
    """
    base_url = os.environ["JIRA_BASE_URL"]
    url = f"{base_url}/rest/api/3/issue/{ticket_key}/comment"
    body = {"body": {"type": "doc", "version": 1, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": comment}]}
    ]}}
    resp = requests.post(url, headers=_jira_headers(), json=body)
    resp.raise_for_status()
    data = resp.json()
    return {"id": data["id"], "author": data["author"]["displayName"]}
```

### 6.2 Definição do agente

Crie `agents/senai_dev_agent/agent.py`:

```python
# agents/senai_dev_agent/agent.py
from dotenv import load_dotenv
load_dotenv()

from ibm_watsonx_orchestrate.agent_builder.agents import Agent, AgentKind
from .tools import get_jira_ticket, list_jira_tickets, add_jira_comment

senai_dev_agent = Agent(
    name="SenaiDevAssistant",
    description=(
        "Agente de suporte ao desenvolvimento de software para o SENAI. "
        "Consulta tickets Jira, revisa código e responde dúvidas técnicas."
    ),
    instructions=(
        "Responda sempre em português. "
        "Priorize consultas ao Jira antes de sugerir soluções. "
        "Nunca execute ações destrutivas sem confirmação explícita do usuário. "
        "Quando não souber a resposta, diga claramente e sugira fontes alternativas."
    ),
    tools=[get_jira_ticket, list_jira_tickets, add_jira_comment],
    kind=AgentKind.EXTERNAL,
    llm="ibm/granite-3-8b-instruct",
)
```

### 6.3 `__init__.py` do pacote

Crie `agents/senai_dev_agent/__init__.py`:

```python
from .agent import senai_dev_agent
```

### 6.4 requirements.txt

```
ibm-watsonx-orchestrate-adk>=1.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### 6.5 Deploy e teste local com ADK

```bash
# Ativar venv e carregar variáveis
source .venv/bin/activate
source .env  # ou export manual de cada variável

# Deploy para o ambiente watsonx Orchestrate
wx-orchestrate agents deploy agents/senai_dev_agent/agent.py

# Verificar agentes deployados
wx-orchestrate agents list

# Testar o agente via CLI
wx-orchestrate agents invoke SenaiDevAssistant \
  --message "Quais são os tickets em andamento do projeto SCRUM?"

# Testar outra chamada
wx-orchestrate agents invoke SenaiDevAssistant \
  --message "Busque os detalhes do ticket SCRUM-12"
```

---

## Módulo 7 — Conectando o Jira via MCP no Bob Shell

O Jira disponibiliza um **servidor MCP oficial** acessível via Streamable HTTP com autenticação OAuth. Não é necessário criar nem hospedar nenhum servidor — basta configurar o `.bob/mcp.json` do projeto.

### 7.1 Como funciona o MCP oficial do Jira

O Atlassian expõe o endpoint `https://mcp.atlassian.com/v2/mcp` que implementa o protocolo MCP sobre HTTP. A autenticação é feita via **OAuth 2.1**: ao conectar pela primeira vez, o Bob Shell abre o browser para você aprovar o acesso à sua conta Atlassian. Os tokens são armazenados e renovados automaticamente — nenhuma credencial fica no arquivo de configuração.

**Fluxo de autenticação OAuth:**
```
Bob Shell  →  detecta OAuth (401)  →  abre browser  →  você aprova
         ←  recebe tokens          ←  Atlassian
Bob Shell  →  requisições autenticadas  →  mcp.atlassian.com
         (refresh automático antes de expirar)
```

### 7.2 Configuração no .bob/mcp.json (projeto)

Crie `.bob/mcp.json` na raiz do projeto `senai-agent/`:

```json
{
  "mcpServers": {
    "jira": {
      "type": "streamable-http",
      "url": "https://mcp.atlassian.com/v2/mcp",
      "oauth": {
        "enabled": true,
        "scope": "read:jira:agent-interface search:jira:agent-interface write:jira:agent-interface"
      },
      "alwaysAllow": ["get_issue", "list_issues", "search_issues"],
      "disabled": false
    }
  }
}
```

> **Nota:** A configuração de projeto (`.bob/mcp.json`) tem precedência sobre a global (`~/.bob/settings/mcp.json`). É seguro commitar este arquivo — não contém credenciais.

### 7.3 Configuração global (opcional — todos os projetos)

Para disponibilizar o Jira MCP em todos os projetos, edite `~/.bob/settings/mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "type": "streamable-http",
      "url": "https://mcp.atlassian.com/v2/mcp",
      "oauth": {
        "enabled": true,
        "scope": "read:jira:agent-interface search:jira:agent-interface write:jira:agent-interface"
      },
      "disabled": false
    }
  }
}
```

### 7.4 Propriedades de configuração MCP (referência)

| Propriedade | Tipo | Obrigatória | Descrição |
|---|---|---|---|
| `type` | string | Não | `"streamable-http"` para servidores HTTP remotos |
| `url` | string | **Sim** | URL do endpoint MCP |
| `oauth.enabled` | boolean | Não | `true` para exigir OAuth (padrão quando sem `Authorization` header) |
| `oauth.clientId` | string | Não | Client ID pré-registrado no provedor de identidade |
| `oauth.clientSecret` | string | Não | Client secret (apenas para clientes confidenciais) |
| `oauth.scope` | string | Não | Escopos OAuth separados por espaço |
| `headers` | object | Não | Headers HTTP customizados (para token estático — **desativa OAuth**) |
| `alwaysAllow` | array | Não | Nomes de tools aprovadas automaticamente sem confirmação |
| `disabled` | boolean | Não | `true` para desabilitar o servidor |
| `timeout` | number | Não | Timeout em ms (padrão: 600.000) |

> **Atenção:** Adicionar um header `Authorization` estático **desativa o OAuth**. Use apenas um método de autenticação por servidor.

### 7.5 Primeira conexão — fluxo OAuth

1. Inicie o Bob Shell na pasta do projeto: `bob chat`
2. O Bob detecta o servidor Jira MCP no `.bob/mcp.json`
3. Uma janela do browser é aberta em `https://mcp.atlassian.com`
4. Faça login com sua conta Atlassian e aprove os escopos solicitados
5. O Bob recebe e armazena os tokens automaticamente
6. A partir daí, o Bob tem acesso às tools do Jira sem intervenção

Para trocar de conta ou revogar o acesso: **Configurações do Bob → MCP → Jira → Reset auth**

### 7.6 Usando o Jira via Bob Shell

```bash
# Iniciar sessão na pasta do projeto
cd senai-agent
bob chat

# Exemplos no chat:
# "Mostre todos os tickets abertos do projeto SCRUM com status Em andamento"
# "Busque os detalhes do ticket SCRUM-12"
# "Crie um ticket no projeto SCRUM: Implementar endpoint GET /clientes, tipo Story"
# "Adicione um comentário ao SCRUM-12 dizendo que a análise foi concluída"
# "Mude o status do SCRUM-12 para Em andamento"
```

---

## Módulo 8 — Registrando o MCP Jira no watsonx Orchestrate

### 8.1 Registrar o servidor MCP remoto

```bash
wx-orchestrate mcp register \
  --name jira \
  --transport streamable-http \
  --url https://mcp.atlassian.com/v2/mcp \
  --oauth-scope "read:jira:agent-interface search:jira:agent-interface write:jira:agent-interface"
```

### 8.2 Verificar registro e listar tools disponíveis

```bash
# Listar servidores MCP registrados no Orchestrate
wx-orchestrate mcp list

# Listar tools expostas pelo servidor Jira
wx-orchestrate mcp tools --name jira
```

---

## Módulo 9 — Criando Hooks no Bob Shell

### 9.1 Hooks disponíveis

| Hook | Quando executa | Bloqueante | Stdout |
|---|---|---|---|
| `SessionStart` | Ao iniciar sessão | Não | Injetado como contexto |
| `UserPromptSubmit` | A cada prompt enviado | Sim (exit 2) | Injetado com o prompt |
| `PreToolUse` | Antes de executar tool | Sim (exit 2 / JSON deny) | JSON para negar/substituir |
| `PostToolUse` | Após tool executar | Não | Anexado ao resultado |
| `PreCompact` | Antes da compactação | Sim (exit 2) | Ignorado |
| `Stop` | Quando o agente para | Não | Ignorado |

### 9.2 Configurando hooks — ~/.bob/settings/settings.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "sh ~/.bob/hooks/session-start.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "^write_file$",
        "hooks": [
          {
            "type": "command",
            "command": "sh ~/.bob/hooks/log-writes.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "https://hooks.slack.com/services/<SEU_WEBHOOK>",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### 9.3 Script de SessionStart

```bash
#!/bin/sh
# ~/.bob/hooks/session-start.sh
# Injeta contexto do projeto no início de cada sessão Bob Shell

mkdir -p ~/.bob/hooks

PROJECT=$(basename "$PWD")
BRANCH=$(git branch --show-current 2>/dev/null || echo "not a git repo")
PYTHON_VER=$(python3 --version 2>/dev/null || echo "python3 not found")
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== Contexto da Sessão SENAI ==="
echo "Projeto:  $PROJECT"
echo "Branch:   $BRANCH"
echo "Python:   $PYTHON_VER"
echo "Data/Hora: $DATE"
echo "================================"
```

### 9.4 Script de auditoria de writes

```bash
#!/bin/sh
# ~/.bob/hooks/log-writes.sh
# Audita toda chamada write_file do Bob Shell

LOGFILE="$HOME/.bob/hooks/write-audit.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') | WRITE_FILE | $(cat)" >> "$LOGFILE"
```

### 9.5 Aplicar permissões

```bash
chmod +x ~/.bob/hooks/session-start.sh
chmod +x ~/.bob/hooks/log-writes.sh
```

---

## Módulo 10 — Criando Skills no Bob Shell

### 10.1 Estrutura de pastas

```
.bob/
└── skills/
    ├── code-review-python/
    │   └── SKILL.md
    ├── jira-ticket-update/
    │   └── SKILL.md
    └── generate-unit-tests/
        └── SKILL.md
```

### 10.2 Skill — Revisão de Código Python

Crie `.bob/skills/code-review-python/SKILL.md`:

```markdown
---
name: code-review-python
description: Revisa código Python verificando PEP 8, segurança, performance e padrões SENAI
---

Ao revisar código Python, verifique:

## Segurança
- SQL Injection: nunca concatene strings em queries; use parâmetros
- Segredos: variáveis com API Keys, tokens ou senhas nunca em código-fonte
- Valide e sanitize todos os inputs antes de processar

## Qualidade de código
- Siga PEP 8: 79 chars/linha, snake_case, CamelCase para classes
- Type hints obrigatórios em todas as funções públicas
- Docstrings no formato Google Style para classes e funções públicas
- Máximo 20 linhas por função
- Evite variáveis de uma letra (exceto em list comprehensions)

## Performance
- Prefira list comprehensions a loops for com append
- Use generators para coleções grandes
- Feche conexões e arquivos com context managers (with)

## Testes
- Cobertura mínima de 80% para módulos de negócio
- Testes de happy path, edge cases e exceções

## Saída
Tabela: Arquivo | Linha | Severidade | Descrição | Sugestão
Severidades: CRÍTICO, ALTO, MÉDIO, BAIXO, INFO
Termine com: Aprovado ✅ / Reprovado ❌ + justificativa
```

### 10.3 Skill — Atualizar Ticket Jira

Crie `.bob/skills/jira-ticket-update/SKILL.md`:

```markdown
---
name: jira-ticket-update
description: Atualiza tickets Jira com comentários de progresso após cada tarefa concluída pelo Bob Shell
---

Após concluir qualquer tarefa relacionada a um ticket Jira:

1. Identifique o ticket no formato PROJETO-NÚMERO (ex: SCRUM-12)
2. Redija um comentário profissional em português:
   - O que foi feito
   - Arquivos criados/modificados (com caminhos)
   - Próximos passos (se houver)
   - Status atual da tarefa
3. Use a tool `add_comment` do MCP server jira para postar
4. Se 100% concluída, use `update_status` com transition "Done" ou "Concluído"

Formato do comentário:
### ✅ Atualização IBM Bob
**O que foi feito:** [descrição objetiva]
**Arquivos:** [lista de arquivos]
**Status:** Em andamento | Concluído
**Próximos passos:** [se houver]
```

### 10.4 Skill — Gerar Testes Unitários Python

Crie `.bob/skills/generate-unit-tests/SKILL.md`:

```markdown
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

## Exemplo de estrutura
def test_deve_retornar_ticket_quando_chave_valida(mock_requests):
    # Arrange
    mock_requests.get.return_value.json.return_value = {
        "key": "SCRUM-1", "fields": {...}
    }
    # Act
    result = get_jira_ticket("SCRUM-1")
    # Assert
    assert result["key"] == "SCRUM-1"
```

### 10.5 Invocando skills no Bob Shell

```bash
# No chat do Bob Shell:
# Invocação explícita via slash command
/code-review-python

# Bob ativa automaticamente ao detectar contexto
"Revise o arquivo agents/senai_dev_agent/tools.py"

# Listar skills disponíveis
/skills
```

---

## Módulo 11 — Modos Customizados (Custom Modes)

Crie `.bob/custom_modes.yaml`:

```yaml
customModes:
  - slug: senai-dev
    name: 🎓 SENAI Dev Assistant
    roleDefinition: >-
      Você é um assistente de desenvolvimento especializado nos padrões e
      processos do SENAI. Você conhece Python, FastAPI, microsserviços,
      IBM Cloud e watsonx Orchestrate. Responda sempre em português e
      priorize soluções práticas, objetivas e seguras.
    whenToUse: >-
      Use para desenvolvimento de features, revisão de código, resolução
      de bugs, criação de agentes ADK e deploy no Code Engine.
    customInstructions: |-
      Diretrizes obrigatórias:
      - Verifique tickets Jira antes de iniciar qualquer desenvolvimento
      - Siga os padrões definidos no AGENTS.md do projeto
      - Use type hints e docstrings em todo código Python
      - Sempre escreva testes para o código gerado
      - Prefira soluções simples e legíveis
      - Variáveis de ambiente para credenciais, nunca hardcode
    groups:
      - read
      - edit
      - execute
      - mcp
      - skill

  - slug: senai-reviewer
    name: 👀 SENAI Code Reviewer
    roleDefinition: >-
      Você é um revisor de código sênior focado em qualidade, segurança
      e conformidade com padrões SENAI. Você nunca modifica código
      diretamente — apenas analisa e sugere melhorias.
    whenToUse: >-
      Use para revisões de pull requests, auditorias de segurança
      e validação de conformidade com padrões de código Python.
    customInstructions: |-
      - Apenas leia arquivos, nunca modifique
      - Classifique por severidade: CRÍTICO, ALTO, MÉDIO, BAIXO
      - Forneça sempre um exemplo concreto de correção
      - Agrupe findings por: Segurança, Performance, Manutenibilidade
    groups:
      - read
      - mcp
      - skill
```

---

## Módulo 12 — Templates de Prompts

### Estrutura de pastas

```
.bob/
└── prompts/
    ├── iniciar-ticket.md
    ├── code-review.md
    └── gerar-docs.md
```

### Template — Iniciar Ticket (.bob/prompts/iniciar-ticket.md)

```markdown
---
name: iniciar-ticket
description: Inicia o trabalho em um ticket Jira, lendo o contexto e planejando a implementação
---

Execute os seguintes passos para iniciar o trabalho no ticket {{TICKET_KEY}}:

1. Use a tool `get_issue` do MCP server jira para buscar detalhes do ticket
2. Leia os arquivos relevantes do projeto para entender o contexto
3. Crie um plano de implementação com:
   - Arquivos Python que serão criados/modificados
   - Dependências pip necessárias
   - Estimativa de esforço (horas)
   - Riscos identificados
4. Atualize o ticket com comentário inicial via `add_comment`
5. Aguarde minha confirmação antes de iniciar a implementação
```

### Template — Code Review (.bob/prompts/code-review.md)

```markdown
---
name: code-review
description: Revisão completa de código Python com foco em segurança, performance e padrões
---

Realize revisão completa nos arquivos fornecidos:

**Escopo:**
- Segurança: injeções, secrets expostos, validação de inputs
- Performance: I/O síncrono desnecessário, queries N+1, memory leaks
- Qualidade: type hints, docstrings, complexidade, cobertura de testes
- Padrões SENAI: PEP 8, nomenclatura, estrutura de projeto

**Formato de saída:**
1. Resumo executivo (3-5 linhas)
2. Tabela de findings ordenada por severidade
3. Top 3 itens críticos para correção imediata
4. Veredicto: ✅ Aprovado / ❌ Reprovado + justificativa
```

### Template — Gerar Docs (.bob/prompts/gerar-docs.md)

```markdown
---
name: gerar-docs
description: Gera documentação técnica completa para módulos Python e APIs
---

Gere documentação técnica para o código fornecido:

1. **Docstrings** (Google Style) para todas as classes e funções públicas
2. **README.md** do módulo com:
   - Propósito e responsabilidades
   - Como instalar e configurar (incluindo variáveis de ambiente)
   - Exemplos de uso com código
   - Endpoints REST expostos (se houver)
3. **Diagrama de sequência** em Mermaid para o fluxo principal

Documentação em português, clara e objetiva.
```

---

## Módulo 13 — AGENTS.md e Contexto do Projeto

### 13.1 Gerando com /init no Bob Shell

```bash
# Na pasta senai-agent/, inicie o Bob Shell
cd senai-agent
bob chat

# Execute o comando de inicialização
/init
```

Arquivos gerados:
```
AGENTS.md                          ← contexto principal do projeto
.bob/rules-agent/AGENTS.md        ← regras do modo Agent
.bob/rules-plan/AGENTS.md         ← regras do modo Plan
.bob/rules-ask/AGENTS.md          ← regras do modo Ask
```

### 13.2 AGENTS.md customizado para o projeto

Edite o `AGENTS.md` gerado para incluir:

```markdown
# senai-agent — Contexto do Projeto

## Stack tecnológico
- Python 3.10+, watsonx Orchestrate ADK
- IBM Cloud Code Engine (deploy serverless)
- IBM Cloud Container Registry (imagens Docker)
- Jira Cloud para gestão de tarefas

## Estrutura de pastas
- `agents/` — definições de agentes ADK
- `mcp_server/` — servidores MCP Python
- `scripts/` — scripts de deploy
- `.bob/` — configuração IBM Bob Shell

## Variáveis de ambiente obrigatórias
Todas em `.env` (nunca commitar):
- BOB_API_KEY, ORCHESTRATE_API_KEY, ORCHESTRATE_INSTANCE_URL
- JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
- IBM_CLOUD_API_KEY, IBM_CLOUD_REGION, CODE_ENGINE_PROJECT

## Comandos importantes
- Instalar deps:  pip install -r requirements.txt
- Testes:         pytest tests/ -v --cov
- Bob Shell:      bob chat
- Deploy:         bash scripts/deploy.sh

## Padrões e convenções
- Branches: feature/SCRUM-XX-descricao, fix/SCRUM-XX-descricao
- Commits: Conventional Commits (feat, fix, docs, test, chore)
- Type hints obrigatórios; docstrings Google Style
- Cobertura mínima: 80%
```

---

## Módulo 14 — Dockerfile e Build da Imagem

### 14.1 Dockerfile

Crie `Dockerfile` na raiz do projeto:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Variáveis de build
LABEL maintainer="SENAI Dev Team"
LABEL description="SENAI Dev Assistant — watsonx Orchestrate Agent"

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python primeiro (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY agents/ ./agents/
COPY mcp_server/ ./mcp_server/

# Usuário não-root por segurança
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Porta padrão (se expor HTTP futuramente)
EXPOSE 8080

# Comando padrão — executa o agente
CMD ["python", "-m", "agents.senai_dev_agent"]
```

### 14.2 .dockerignore

Crie `.dockerignore`:

```
.env
.env.*
.venv/
__pycache__/
*.pyc
*.pyo
.git/
.bob/
tests/
*.md
*.pdf
```

### 14.3 Build local para teste

```bash
# Build da imagem
docker build -t senai-dev-assistant:latest .

# Testar localmente
docker run --env-file .env senai-dev-assistant:latest
```

---

## Módulo 15 — Deploy no IBM Cloud Code Engine

### 15.1 Pré-requisitos IBM Cloud

```bash
# 1. Instalar IBM Cloud CLI
# macOS/Linux:
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
# Linux:
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh

# 2. Instalar plugin Code Engine
ibmcloud plugin install code-engine
ibmcloud plugin install container-registry

# 3. Verificar plugins
ibmcloud plugin show code-engine
ibmcloud plugin show container-registry
```

### 15.2 Script de deploy completo

Crie `scripts/deploy.sh`:

```bash
#!/bin/bash
# =============================================================================
# scripts/deploy.sh
# Deploy do SENAI Dev Assistant no IBM Cloud Code Engine
#
# COMO USAR:
#   1. Preencha as variáveis no arquivo .env (copie de .env.example)
#   2. Execute: bash scripts/deploy.sh
# =============================================================================

set -euo pipefail

# ─── Carregar variáveis de ambiente ──────────────────────────────────────────
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ Arquivo .env não encontrado. Copie .env.example para .env e preencha."
  exit 1
fi

# ─── Variáveis obrigatórias ───────────────────────────────────────────────────
: "${IBM_CLOUD_API_KEY:?Variável IBM_CLOUD_API_KEY não definida no .env}"
: "${IBM_CLOUD_REGION:?Variável IBM_CLOUD_REGION não definida no .env}"
: "${IBM_CLOUD_RESOURCE_GROUP:?Variável IBM_CLOUD_RESOURCE_GROUP não definida no .env}"
: "${IBM_CLOUD_REGISTRY_NAMESPACE:?Variável IBM_CLOUD_REGISTRY_NAMESPACE não definida no .env}"
: "${CODE_ENGINE_PROJECT:?Variável CODE_ENGINE_PROJECT não definida no .env}"

# ─── Configurações derivadas ──────────────────────────────────────────────────
APP_NAME="senai-dev-assistant"
IMAGE_TAG="${IBM_CLOUD_REGION}.icr.io/${IBM_CLOUD_REGISTRY_NAMESPACE}/${APP_NAME}:latest"

echo "==================================================="
echo " Deploy: SENAI Dev Assistant → IBM Cloud Code Engine"
echo "==================================================="
echo " Region:    $IBM_CLOUD_REGION"
echo " Project:   $CODE_ENGINE_PROJECT"
echo " Image:     $IMAGE_TAG"
echo "==================================================="

# ─── 1. Login na IBM Cloud ────────────────────────────────────────────────────
echo ""
echo "📋 Passo 1/7 — Login na IBM Cloud..."
ibmcloud login --apikey "$IBM_CLOUD_API_KEY" -r "$IBM_CLOUD_REGION" -g "$IBM_CLOUD_RESOURCE_GROUP" --quiet

# ─── 2. Login no Container Registry ─────────────────────────────────────────
echo "📋 Passo 2/7 — Login no Container Registry..."
ibmcloud cr login
ibmcloud cr region-set "$IBM_CLOUD_REGION"

# ─── 3. Criar namespace do registry (se não existir) ─────────────────────────
echo "📋 Passo 3/7 — Verificando namespace do registry..."
if ! ibmcloud cr namespace-list | grep -q "$IBM_CLOUD_REGISTRY_NAMESPACE"; then
  echo "   Criando namespace: $IBM_CLOUD_REGISTRY_NAMESPACE"
  ibmcloud cr namespace-add "$IBM_CLOUD_REGISTRY_NAMESPACE"
else
  echo "   Namespace já existe: $IBM_CLOUD_REGISTRY_NAMESPACE"
fi

# ─── 4. Build e push da imagem Docker ────────────────────────────────────────
echo "📋 Passo 4/7 — Build e push da imagem Docker..."
docker build -t "$IMAGE_TAG" .
docker push "$IMAGE_TAG"
echo "   ✅ Imagem publicada: $IMAGE_TAG"

# ─── 5. Selecionar / criar projeto Code Engine ───────────────────────────────
echo "📋 Passo 5/7 — Configurando projeto Code Engine..."
if ibmcloud ce project list | grep -q "$CODE_ENGINE_PROJECT"; then
  echo "   Selecionando projeto existente: $CODE_ENGINE_PROJECT"
  ibmcloud ce project select --name "$CODE_ENGINE_PROJECT"
else
  echo "   Criando novo projeto: $CODE_ENGINE_PROJECT"
  ibmcloud ce project create --name "$CODE_ENGINE_PROJECT"
fi

# ─── 6. Criar secret com credenciais da aplicação ────────────────────────────
echo "📋 Passo 6/7 — Criando/atualizando secret com credenciais..."
ibmcloud ce secret delete --name senai-agent-secrets --ignore-not-found --force 2>/dev/null || true

ibmcloud ce secret create \
  --name senai-agent-secrets \
  --from-literal ORCHESTRATE_API_KEY="$ORCHESTRATE_API_KEY" \
  --from-literal ORCHESTRATE_INSTANCE_URL="$ORCHESTRATE_INSTANCE_URL" \
  --from-literal JIRA_BASE_URL="$JIRA_BASE_URL" \
  --from-literal JIRA_EMAIL="$JIRA_EMAIL" \
  --from-literal JIRA_API_TOKEN="$JIRA_API_TOKEN"

echo "   ✅ Secret 'senai-agent-secrets' criado"

# ─── 7. Deploy / atualizar aplicação no Code Engine ──────────────────────────
echo "📋 Passo 7/7 — Deploy da aplicação no Code Engine..."

if ibmcloud ce app list | grep -q "$APP_NAME"; then
  echo "   Atualizando aplicação existente: $APP_NAME"
  ibmcloud ce app update \
    --name "$APP_NAME" \
    --image "$IMAGE_TAG" \
    --env-from-secret senai-agent-secrets \
    --min-scale 0 \
    --max-scale 5 \
    --memory 2G \
    --cpu 0.5
else
  echo "   Criando nova aplicação: $APP_NAME"
  ibmcloud ce app create \
    --name "$APP_NAME" \
    --image "$IMAGE_TAG" \
    --env-from-secret senai-agent-secrets \
    --min-scale 0 \
    --max-scale 5 \
    --memory 2G \
    --cpu 0.5 \
    --port 8080
fi

# ─── Resultado ────────────────────────────────────────────────────────────────
echo ""
echo "==================================================="
echo " ✅ Deploy concluído com sucesso!"
echo "==================================================="

# Obter URL da aplicação
APP_URL=$(ibmcloud ce app get --name "$APP_NAME" --output json | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status',{}).get('url','N/A'))")

echo " URL da aplicação: $APP_URL"
echo ""
echo " Para verificar o status:"
echo "   ibmcloud ce app get --name $APP_NAME"
echo ""
echo " Para ver os logs em tempo real:"
echo "   ibmcloud ce app logs --name $APP_NAME --follow"
echo "==================================================="
```

### 15.3 Tornar o script executável

```bash
chmod +x scripts/deploy.sh
```

### 15.4 Executar o deploy

```bash
# Garantir que o .env está preenchido
cat .env.example   # verifique todos os campos

# Executar o deploy
bash scripts/deploy.sh
```

### 15.5 Comandos úteis pós-deploy

```bash
# Ver status da aplicação
ibmcloud ce app get --name senai-dev-assistant

# Acompanhar logs em tempo real
ibmcloud ce app logs --name senai-dev-assistant --follow

# Listar revisões (versões deployadas)
ibmcloud ce app revision list --app senai-dev-assistant

# Fazer rollback para revisão anterior
ibmcloud ce app rollout --name senai-dev-assistant --revision <revision-name>

# Escalar manualmente
ibmcloud ce app update --name senai-dev-assistant --min-scale 1 --max-scale 10

# Deletar aplicação (cuidado!)
ibmcloud ce app delete --name senai-dev-assistant
```

---

## Apêndice A — Referência Rápida de Configuração

### Estrutura completa do projeto

```
senai-agent/
├── .env                         ← NÃO commitar
├── .env.example                 ← commitar (sem valores)
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
├── AGENTS.md                    ← gerado por /init
├── agents/
│   └── senai_dev_agent/
│       ├── __init__.py
│       ├── agent.py
│       └── tools.py
├── mcp_server/
│   └── jira_mcp/
│       ├── __init__.py
│       └── server.py
├── tests/
│   ├── test_tools.py
│   └── test_agent.py
├── scripts/
│   └── deploy.sh
└── .bob/
    ├── mcp.json
    ├── settings.json
    ├── custom_modes.yaml
    ├── rules-agent/AGENTS.md
    ├── rules-plan/AGENTS.md
    ├── rules-ask/AGENTS.md
    ├── skills/
    │   ├── code-review-python/SKILL.md
    │   ├── jira-ticket-update/SKILL.md
    │   └── generate-unit-tests/SKILL.md
    └── prompts/
        ├── iniciar-ticket.md
        ├── code-review.md
        └── gerar-docs.md
```

### Configurações globais Bob Shell (~/.bob/)

```
~/.bob/
├── settings/
│   ├── settings.json            ← Hooks globais
│   ├── mcp.json                 ← MCP servers globais
│   └── custom_modes.yaml        ← Modos globais
├── hooks/
│   ├── session-start.sh
│   └── log-writes.sh
└── AGENTS.md                    ← Contexto global
```

---

## Apêndice B — Credenciais Necessárias (Checklist)

| Credencial | Onde obter | Variável |
|---|---|---|
| Bob API Key | https://bob.ibm.com → Account → API Keys | `BOB_API_KEY` |
| watsonx Orchestrate API Key | Console watsonx Orchestrate → Settings → API Keys | `ORCHESTRATE_API_KEY` |
| Jira API Token | Jira → Perfil → Gerenciar conta → Segurança → Tokens de API | `JIRA_API_TOKEN` |
| IBM Cloud API Key | IBM Cloud → Gerenciar → Acesso → Chaves de API | `IBM_CLOUD_API_KEY` |
| ICR Namespace | IBM Cloud → Container Registry → Namespaces | `IBM_CLOUD_REGISTRY_NAMESPACE` |

---

## Apêndice C — Troubleshooting

| Problema | Causa provável | Solução |
|---|---|---|
| `bob: command not found` | Instalação incompleta ou PATH não atualizado | Execute o script de instalação novamente; reinicie o terminal |
| Bob pede login toda sessão | BOB_API_KEY não configurada permanentemente | Adicione `export BOB_API_KEY=...` ao `~/.zshrc` ou `~/.bashrc` |
| MCP server não conecta | Caminho ou comando incorreto no mcp.json | Teste o servidor manualmente: `python -m mcp_server.jira_mcp.server` |
| Tool Jira retorna 401 | Token Jira expirado ou inválido | Gere novo token em Jira → Segurança → Tokens de API |
| Skill não ativa automaticamente | Description ausente ou vaga | Adicione `description` detalhada no front matter SKILL.md |
| Hook não executa | Arquivo sem permissão de execução | `chmod +x ~/.bob/hooks/*.sh` |
| `docker push` falha | Não autenticado no ICR | Execute `ibmcloud cr login` antes do push |
| Code Engine deploy falha | Projeto não selecionado | Execute `ibmcloud ce project select --name <nome>` |
| ADK deploy falha | Credenciais não configuradas | Exporte `ORCHESTRATE_API_KEY` e `ORCHESTRATE_INSTANCE_URL` |
| `ibmcloud ce app create` falha com 403 | API Key sem permissões | Garanta que a API Key IBM Cloud tem role Manager no Code Engine |

---

*Documento gerado com IBM Bob Shell | SENAI Hands-On — IBM Bob + watsonx Orchestrate + IBM Cloud Code Engine*
