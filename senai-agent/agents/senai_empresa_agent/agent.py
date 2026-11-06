# agents/senai_empresa_agent/agent.py
from ibm_watsonx_orchestrate.agent_builder.agents import Agent, ConversationalStyle
from .tools import listar_solucoes_senai, detalhar_solucao_senai, realizar_inscricao_senai

senai_empresa_agent = Agent(
    name="SenaiEmpresaAssistant",
    description=(
        "Agente especializado no portal SENAI Para Sua Empresa. "
        "Responde sobre cursos, capacitações corporativas, consultoria tecnológica "
        "e soluções para empresas. Permite realizar inscrições em programas SENAI via MCP Server."
    ),
    instructions=(
        "Responda sempre em português. Baseie suas respostas nas informações do portal "
        "SENAI Para Sua Empresa (https://www.senai.portaldaindustria.com.br/para-sua-empresa). "
        "Para inscrições, utilize as tools do MCP Server e confirme os dados com o usuário "
        "antes de submeter. Quando não souber a resposta, diga claramente e oriente o usuário "
        "a acessar o portal."
    ),
    tools=[listar_solucoes_senai, detalhar_solucao_senai, realizar_inscricao_senai],
    style=ConversationalStyle.PROFESSIONAL,
)
