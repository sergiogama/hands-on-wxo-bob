# Hands-On IBM Bob + watsonx Orchestrate
### SENAI Para Sua Empresa

> Material completo do workshop de desenvolvimento de agentes de IA com **IBM Bob** e **watsonx Orchestrate**, incluindo MCP Server Python, deploy serverless no IBM Cloud Code Engine e integração com o portal SENAI Para Sua Empresa.

---

## 📋 Conteúdo do repositório

| Arquivo / Pasta | Descrição |
|---|---|
| [`index.html`](./index.html) | Material completo do workshop em HTML (imprimível / PDF) |
| [`senai-agent/`](./senai-agent/) | Esqueleto do projeto construído durante o workshop |

---

## 🗂️ Módulos do Workshop

| # | Módulo |
|---|---|
| 01 | Visão Geral da Solução |
| 02 | Instalando e Configurando o IBM Bob |
| 03 | Ambiente Python e Credenciais |
| 04 | Criando o Agente — Interface Web watsonx Orchestrate |
| 05 | PDF de Conhecimento Base (RAG) |
| 06 | Criando o Agente Python com ADK |
| 07 | MCP Server — SENAI Para Sua Empresa |
| 08 | Registrando o MCP SENAI no watsonx Orchestrate |
| 09 | Criando Hooks de Lifecycle |
| 10 | Criando Skills no IBM Bob |
| 11 | Custom Modes |
| 12 | Templates de Prompts |
| 13 | AGENTS.md e Contexto do Projeto |
| 14 | Dockerfile e Build da Imagem |
| 15 | Deploy no IBM Cloud Code Engine |
| A | Apêndice A — Estrutura de Arquivos |
| B | Apêndice B — Checklist de Credenciais |
| C | Apêndice C — Troubleshooting |

---

## 🚀 Início rápido

### Pré-requisitos

- **IBM Bob** instalado — download em [bob.ibm.com](https://bob.ibm.com) (inclui VS Code embutido)
- Python 3.10+
- Docker Desktop instalado e rodando
- Conta IBM Cloud com acesso ao Code Engine e Container Registry
- Conta IBM watsonx Orchestrate

### 1. Clone o repositório

```bash
git clone https://github.com/sergiogama/hands-on-wxo-bob.git
cd hands-on-wxo-bob
```

### 2. Abra no IBM Bob

1. Abra o IBM Bob
2. **File → Open Folder** → selecione a pasta `hands-on-wxo-bob/`
3. Abra o painel de chat (`Option+Cmd+B` no Mac / `Ctrl+Alt+B` no Windows)

### 3. Configure o projeto Python

```bash
cd senai-agent
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edite .env com suas credenciais reais
```

### 4. Inicialize o contexto do IBM Bob

No painel de chat do IBM Bob:
```
/init
```

---

## 🛠️ Estrutura do projeto `senai-agent/`

```
senai-agent/
├── .env.example           ← template de credenciais (commitar)
├── .env                   ← credenciais reais (NÃO commitar)
├── requirements.txt
├── Dockerfile
├── AGENTS.md              ← gerado por /init no IBM Bob
├── agents/
│   └── senai_empresa_agent/
│       ├── agent.py       ← definição do agente ADK
│       └── tools.py       ← tools SENAI (listar, detalhar, inscrever)
├── mcp_server/
│   └── senai_empresa_mcp/
│       └── server.py      ← MCP Server Python STDIO
├── scripts/
│   └── deploy.sh          ← deploy completo no Code Engine
└── .bob/
    ├── mcp.json           ← configuração do MCP Server
    ├── settings.json      ← hooks de lifecycle
    ├── custom_modes.yaml  ← modos customizados
    ├── skills/            ← skills do IBM Bob
    └── prompts/           ← templates de prompts
```

---

## 📄 Leitura do material

Abra o arquivo [`index.html`](./index.html) diretamente no browser para visualizar ou imprimir o material completo do workshop.

---

## 👤 Autor

**Sergio Gama** · Principal AI Solution Architect · TD Synnex

---

## 📅 Versão

Novembro / 2026 — Versão 1.0
