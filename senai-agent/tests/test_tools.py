# tests/test_tools.py
import pytest
from agents.senai_empresa_agent.tools import (
    listar_solucoes_senai,
    detalhar_solucao_senai,
    realizar_inscricao_senai,
)


def test_deve_listar_todas_solucoes_quando_sem_categoria():
    # Arrange / Act
    resultado = listar_solucoes_senai()
    # Assert
    assert isinstance(resultado, list)
    assert len(resultado) > 0


def test_deve_filtrar_solucoes_por_categoria():
    resultado = listar_solucoes_senai(categoria="capacitacao")
    assert all(s["categoria"] == "capacitacao" for s in resultado)


def test_deve_retornar_erro_quando_solucao_nao_encontrada():
    resultado = detalhar_solucao_senai("Solução Inexistente")
    assert "erro" in resultado


def test_deve_retornar_protocolo_na_inscricao():
    resultado = realizar_inscricao_senai(
        nome_empresa="Empresa Teste SA",
        cnpj="12345678000199",
        nome_responsavel="João Silva",
        email_responsavel="joao@empresa.com",
        telefone="11999990000",
        solucao_interesse="Capacitação In Company",
    )
    assert "protocolo" in resultado
    assert resultado["status"] == "recebida"
