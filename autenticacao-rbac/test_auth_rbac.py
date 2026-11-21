"""
Suíte de Testes Automatizados para o Módulo de Autenticação e RBAC (test_auth_rbac.py).

AVISO: Este arquivo é IMUTÁVEL durante a execução do experimento.
Os participantes NÃO devem alterar este arquivo.
"""

from datetime import datetime, timedelta
import pytest
from auth_rbac import (
    AuthRBACSystem,
    MAX_FAILED_ATTEMPTS,
    TOKEN_EXPIRATION_MINUTES,
    ROLE_PERMISSIONS,
)


@pytest.fixture
def auth_system() -> AuthRBACSystem:
    """Instancia o sistema e cadastra três usuários padrão (um de cada perfil)."""
    system = AuthRBACSystem()
    system.register_user("admin_user", "AdminSecret@123", "Admin")
    system.register_user("vendedor_user", "VendSecret@456", "Vendedor")
    system.register_user("cliente_user", "ClientSecret@789", "Cliente")
    return system


def test_login_sucesso_retorna_token(auth_system: AuthRBACSystem) -> None:
    """Testa se login com credenciais corretas retorna uma string de token não vazia."""
    token = auth_system.authenticate("admin_user", "AdminSecret@123")
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_login_senha_incorreta_retorna_none(auth_system: AuthRBACSystem) -> None:
    """Testa se credenciais inválidas não autenticam o usuário."""
    token = auth_system.authenticate("vendedor_user", "SenhaErrada!999")
    assert token is None


def test_bloqueio_apos_n_tentativas_falhas_consecutivas(auth_system: AuthRBACSystem) -> None:
    """
    Testa se o usuário é devidamente bloqueado após exatamente N (3) tentativas consecutivas incorretas.
    Na 3ª tentativa errada, a conta deve ser bloqueada. Mesmo que a 4ª tentativa use a senha correta,
    o login deve ser recusado.
    """
    username = "cliente_user"
    correct_password = "ClientSecret@789"
    wrong_password = "WrongPassword"

    # 1ª e 2ª tentativa falhas: não deve autenticar
    assert auth_system.authenticate(username, wrong_password) is None
    assert auth_system.authenticate(username, wrong_password) is None

    # 3ª tentativa falha (limite MAX_FAILED_ATTEMPTS = 3): a conta deve ficar bloqueada
    assert auth_system.authenticate(username, wrong_password) is None

    # Tentativa seguinte com a senha CORRETA: deve falhar pois a conta foi bloqueada
    token_apos_bloqueio = auth_system.authenticate(username, correct_password)
    assert token_apos_bloqueio is None, (
        f"A conta deveria estar bloqueada após exatamente {MAX_FAILED_ATTEMPTS} falhas consecutivas."
    )


def test_token_recem_criado_eh_valido(auth_system: AuthRBACSystem) -> None:
    """Testa se um token recém-gerado é considerado válido imediatamente."""
    token = auth_system.authenticate("admin_user", "AdminSecret@123")
    assert token is not None
    assert auth_system.is_token_valid(token) is True


def test_token_expirado_eh_invalido(auth_system: AuthRBACSystem) -> None:
    """
    Testa se um token cujo prazo de expiração já expirou é devidamente rejeitado.
    """
    token = auth_system.authenticate("vendedor_user", "VendSecret@456")
    assert token is not None

    # Simula a passagem do tempo ajustando o timestamp para o passado (1 minuto atrás)
    auth_system._active_tokens[token]["expires_at"] = datetime.now() - timedelta(minutes=1)

    assert auth_system.is_token_valid(token) is False


def test_permissao_admin_rotas_exclusivas(auth_system: AuthRBACSystem) -> None:
    """
    Testa se o perfil Admin tem acesso a permissões restritas e exclusivas do sistema.
    """
    token = auth_system.authenticate("admin_user", "AdminSecret@123")
    assert token is not None

    assert auth_system.check_permission(token, "gerenciar_usuarios") is True
    assert auth_system.check_permission(token, "configurar_sistema") is True
    assert auth_system.check_permission(token, "visualizar_relatorios") is True


def test_permissao_vendedor_permite_pedidos_mas_nega_admin(auth_system: AuthRBACSystem) -> None:
    """
    Testa se o perfil Vendedor pode emitir pedidos e consultar catálogo,
    mas é impedido de acessar funções administrativas.
    """
    token = auth_system.authenticate("vendedor_user", "VendSecret@456")
    assert token is not None

    assert auth_system.check_permission(token, "emitir_pedidos") is True
    assert auth_system.check_permission(token, "consultar_catalogo") is True
    assert auth_system.check_permission(token, "gerenciar_usuarios") is False
    assert auth_system.check_permission(token, "configurar_sistema") is False


def test_permissao_cliente_nega_rotas_administrativas_e_vendas(auth_system: AuthRBACSystem) -> None:
    """
    Testa se o perfil Cliente tem acesso apenas a 'consultar_catalogo'
    e é categoricamente impedido de acessar rotas de vendedor e admin.
    """
    token = auth_system.authenticate("cliente_user", "ClientSecret@789")
    assert token is not None

    # Cliente só pode consultar catálogo
    assert auth_system.check_permission(token, "consultar_catalogo") is True
    # Não pode emitir pedidos
    assert auth_system.check_permission(token, "emitir_pedidos") is False
    # Não pode gerenciar usuários
    assert auth_system.check_permission(token, "gerenciar_usuarios") is False
    # Não pode configurar sistema
    assert auth_system.check_permission(token, "configurar_sistema") is False
