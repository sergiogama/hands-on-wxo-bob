# mcp_server/senai_empresa_mcp/server.py
import asyncio
import hashlib
import time
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

SENAI_BASE = "https://www.senai.portaldaindustria.com.br"

app = Server("senai-empresa-mcp")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="listar_solucoes",
            description="Lista soluções e serviços SENAI Para Sua Empresa",
            inputSchema={
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Categoria: capacitacao | consultoria | inovacao",
                    }
                },
            },
        ),
        types.Tool(
            name="detalhar_solucao",
            description="Retorna detalhes de uma solução SENAI",
            inputSchema={
                "type": "object",
                "properties": {
                    "nome_solucao": {
                        "type": "string",
                        "description": "Nome exato da solução SENAI",
                    }
                },
                "required": ["nome_solucao"],
            },
        ),
        types.Tool(
            name="realizar_inscricao",
            description="Inscreve uma empresa em um programa SENAI Para Sua Empresa",
            inputSchema={
                "type": "object",
                "properties": {
                    "nome_empresa":      {"type": "string"},
                    "cnpj":              {"type": "string"},
                    "nome_responsavel":  {"type": "string"},
                    "email_responsavel": {"type": "string"},
                    "telefone":          {"type": "string"},
                    "solucao_interesse": {"type": "string"},
                    "mensagem":          {"type": "string"},
                },
                "required": [
                    "nome_empresa", "cnpj", "nome_responsavel",
                    "email_responsavel", "telefone", "solucao_interesse",
                ],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "listar_solucoes":
        categoria = arguments.get("categoria", "")
        solucoes = [
            {"nome": "Capacitação In Company",        "categoria": "capacitacao"},
            {"nome": "Consultoria em Processos",       "categoria": "consultoria"},
            {"nome": "Laboratórios e Ensaios",         "categoria": "inovacao"},
        ]
        resultado = [s for s in solucoes if not categoria or s["categoria"] == categoria]
        return [types.TextContent(type="text", text=str(resultado))]

    if name == "detalhar_solucao":
        nome = arguments["nome_solucao"]
        return [types.TextContent(
            type="text",
            text=f"Detalhes de '{nome}': consulte {SENAI_BASE}/para-sua-empresa",
        )]

    if name == "realizar_inscricao":
        protocolo = hashlib.md5(
            f"{arguments['cnpj']}{time.time()}".encode()
        ).hexdigest()[:10].upper()
        return [types.TextContent(type="text", text=(
            f"Inscrição recebida! Protocolo: {protocolo}. "
            "Um consultor SENAI entrará em contato em até 2 dias úteis."
        ))]

    raise ValueError(f"Tool desconhecida: {name}")


async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
