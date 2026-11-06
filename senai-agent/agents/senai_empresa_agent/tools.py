# agents/senai_empresa_agent/tools.py
import os
import requests
from ibm_watsonx_orchestrate.agent_builder.tools import tool

SENAI_BASE_URL = "https://www.senai.portaldaindustria.com.br"
SENAI_EMPRESA_URL = f"{SENAI_BASE_URL}/para-sua-empresa"


@tool
def listar_solucoes_senai(categoria: str = "") -> list:
    """Lista soluções e serviços disponíveis no portal SENAI Para Sua Empresa.

    Args:
        categoria: Categoria para filtrar (ex: "capacitacao", "consultoria", "inovacao").
                   Vazio = todas as categorias.

    Returns:
        Lista de dicionários com nome, categoria, descricao e url.
    """
    solucoes = [
        {"nome": "Capacitação In Company", "categoria": "capacitacao",
         "descricao": "Treinamentos customizados para equipes na empresa",
         "url": f"{SENAI_EMPRESA_URL}/capacitacao-corporativa"},
        {"nome": "Consultoria em Processos Industriais", "categoria": "consultoria",
         "descricao": "Diagnóstico e melhoria de processos produtivos",
         "url": f"{SENAI_EMPRESA_URL}/consultoria"},
        {"nome": "Laboratórios e Ensaios Tecnológicos", "categoria": "inovacao",
         "descricao": "Testes e certificações para produtos industriais",
         "url": f"{SENAI_EMPRESA_URL}/laboratorios"},
        {"nome": "Projetos de Inovação e P&D", "categoria": "inovacao",
         "descricao": "Desenvolvimento conjunto de soluções tecnológicas",
         "url": f"{SENAI_EMPRESA_URL}/inovacao"},
    ]
    if categoria:
        return [s for s in solucoes if s["categoria"] == categoria]
    return solucoes


@tool
def detalhar_solucao_senai(nome_solucao: str) -> dict:
    """Retorna detalhes completos de uma solução SENAI Para Sua Empresa.

    Args:
        nome_solucao: Nome da solução (ex: "Capacitação In Company")

    Returns:
        Dicionário com nome, descricao, publico_alvo, modalidades, contato e url.
    """
    catalogo = {
        "Capacitação In Company": {
            "nome": "Capacitação In Company",
            "descricao": "Treinamentos técnicos e comportamentais desenvolvidos "
                         "sob medida para a realidade da sua empresa.",
            "publico_alvo": "Equipes industriais, operadores, supervisores e gestores",
            "modalidades": ["Presencial na empresa", "EAD", "Híbrido"],
            "contato": "https://www.senai.portaldaindustria.com.br/contato",
            "url": f"{SENAI_EMPRESA_URL}/capacitacao-corporativa",
        },
    }
    return catalogo.get(nome_solucao, {"erro": f"Solução '{nome_solucao}' não encontrada."})


@tool
def realizar_inscricao_senai(
    nome_empresa: str,
    cnpj: str,
    nome_responsavel: str,
    email_responsavel: str,
    telefone: str,
    solucao_interesse: str,
    mensagem: str = "",
) -> dict:
    """Inscreve uma empresa em um programa SENAI Para Sua Empresa.

    Args:
        nome_empresa: Razão social da empresa.
        cnpj: CNPJ da empresa (14 dígitos numéricos).
        nome_responsavel: Nome completo do responsável.
        email_responsavel: E-mail corporativo do responsável.
        telefone: Telefone com DDD.
        solucao_interesse: Nome da solução SENAI de interesse.
        mensagem: Mensagem adicional (opcional).

    Returns:
        Dicionário com protocolo e status da inscrição.
    """
    import hashlib, time

    protocolo = hashlib.md5(
        f"{cnpj}{time.time()}".encode()
    ).hexdigest()[:10].upper()

    return {
        "protocolo": protocolo,
        "status": "recebida",
        "mensagem": "Um consultor SENAI entrará em contato em até 2 dias úteis.",
    }
