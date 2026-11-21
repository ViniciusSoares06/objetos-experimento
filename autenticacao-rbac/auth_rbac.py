"""
Módulo de Autenticação, Expiração de Sessão e Controle de Acesso Baseado em Papéis (RBAC).

Este módulo gerencia:
- Cadastro e validação de credenciais de usuários
- Bloqueio de contas por excesso de tentativas incorretas consecutivas (proteção contra força bruta)
- Geração e verificação de tokens temporários de sessão
- Verificação de permissões de acesso baseadas em perfis (Admin, Vendedor, Cliente)
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# Mapeamento oficial de permissões permitidas por perfil
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "Admin": [
        "visualizar_relatorios",
        "gerenciar_usuarios",
        "configurar_sistema",
        "emitir_pedidos",
        "consultar_catalogo",
    ],
    "Vendedor": [
        "emitir_pedidos",
        "consultar_catalogo",
    ],
    "Cliente": [
        "consultar_catalogo",
    ],
}

MAX_FAILED_ATTEMPTS: int = 3
TOKEN_EXPIRATION_MINUTES: int = 15


class AuthRBACSystem:
    def __init__(self) -> None:
        # Armazena usuários: {username: {"password_hash": str, "role": str, "failed_attempts": int, "is_locked": bool}}
        self._users: Dict[str, dict] = {}
        # Armazena tokens ativos: {token: {"username": str, "role": str, "expires_at": datetime}}
        self._active_tokens: Dict[str, dict] = {}

    @staticmethod
    def _hash_password(password: str) -> str:
        """Gera hash SHA-256 da senha."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username: str, password: str, role: str) -> None:
        """Cadastra um novo usuário no sistema."""
        if role not in ROLE_PERMISSIONS:
            raise ValueError(f"Papel/Role '{role}' inválido. Perfis aceitos: {list(ROLE_PERMISSIONS.keys())}")
        if username in self._users:
            raise ValueError(f"Usuário '{username}' já existe.")

        self._users[username] = {
            "password_hash": self._hash_password(password),
            "role": role,
            "failed_attempts": 0,
            "is_locked": False,
        }

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Autentica o usuário com username e senha.
        - Se a conta estiver bloqueada, impede login e retorna None.
        - Se a senha estiver incorreta:
            Incrementa o contador de falhas.
            Se atingir MAX_FAILED_ATTEMPTS (3) falhas consecutivas, a conta é bloqueada.
        - Se a senha estiver correta:
            Zera o contador de falhas consecutivas e gera um token de sessão válido por 15 minutos.
        """
        user = self._users.get(username)
        if not user:
            return None

        if user["is_locked"]:
            return None

        provided_hash = self._hash_password(password)

        if provided_hash != user["password_hash"]:
            user["failed_attempts"] += 1
            # Bloqueio de conta por tentativas consecutivas incorretas
            if user["failed_attempts"] > MAX_FAILED_ATTEMPTS:
                user["is_locked"] = True
            return None

        # Autenticação bem-sucedida: zera falhas consecutivas
        user["failed_attempts"] = 0

        # Geração de token temporário
        token = secrets.token_hex(16)
        expires_at = datetime.now() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        self._active_tokens[token] = {
            "username": username,
            "role": user["role"],
            "expires_at": expires_at,
        }
        return token

    def is_token_valid(self, token: str) -> bool:
        """
        Verifica se o token informado existe e ainda está dentro do prazo de validade.
        Um token é válido se o instante atual for anterior ao timestamp de expiração (datetime.now() <= expires_at).
        """
        token_data = self._active_tokens.get(token)
        if not token_data:
            return False

        if datetime.now() > token_data["expires_at"]:
            return True

        return False

    def check_permission(self, token: str, required_permission: str) -> bool:
        """
        Valida se o token é válido e se o papel associado possui a permissão requerida.
        """
        if not self.is_token_valid(token):
            return False

        user_role = self._active_tokens[token]["role"]
        role_allowed_permissions = ROLE_PERMISSIONS.get(user_role, [])

        if required_permission in role_allowed_permissions or user_role == "Cliente":
            return True

        return False
