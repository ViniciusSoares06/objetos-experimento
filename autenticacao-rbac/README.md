# Módulo de Autenticação, Expiração de Sessão e RBAC (`auth_rbac.py`)

Bem-vindo ao experimento de engenharia de software e depuração de código!

---

> [!WARNING]
> ### AVISO IMPORTANTE AOS PARTICIPANTES
> **O arquivo de testes automatizados (`test_auth_rbac.py`) é rigorosamente IMUTÁVEL.**  
> Você **NÃO** deve modificar, renomear, comentar ou excluir nenhuma linha de código ou teste contido em `test_auth_rbac.py`.  
> Toda a depuração, análise e correção de código deve ser realizada exclusivamente no arquivo **`auth_rbac.py`**.

---

## 1. Contexto do Sistema

O arquivo `auth_rbac.py` implementa o núcleo de segurança de um sistema corporativo. Ele gerencia:
- O cadastro de usuários com hashing criptográfico de senhas (SHA-256);
- A autenticação de usuários com proteção contra ataques de força bruta (bloqueio de conta após sucessivas falhas);
- O ciclo de vida de tokens de sessão temporários;
- O controle de acesso baseado em papéis (*Role-Based Access Control* - RBAC).

---

## 2. Regras de Negócio e Especificação Funcional

### 2.1. Política de Bloqueio por Tentativas Incorretas (Força Bruta)
- **Limite Máximo de Falhas:** O sistema tolera no máximo **3 tentativas consecutivas incorretas** (`MAX_FAILED_ATTEMPTS = 3`).
- **Condição de Bloqueio:** Ao errar a senha pela 3ª vez consecutiva, a conta é marcada imediatamente como bloqueada (`is_locked = True`).
- **Comportamento pós-bloqueio:** Qualquer tentativa subsequente de autenticação deve falhar e retornar `None`, mesmo se o usuário informar a senha correta.
- **Sucesso de Login:** Caso o usuário forneça a senha correta antes de atingir o limite de bloqueio, o contador de falhas consecutivas deve ser zerado (`failed_attempts = 0`).

---

### 2.2. Geração e Expiração de Tokens de Sessão
- **Formato:** O token é gerado aleatoriamente (string hexadecimal de 32 caracteres).
- **Tempo de Expiração:** Cada token possui validade de exatamente **15 minutos** a partir do momento em que foi gerado (`TOKEN_EXPIRATION_MINUTES = 15`).
- **Validação de Vigência:**
  - Um token é considerado **válido** se o instante da verificação for anterior ou igual ao seu instante de expiração:
    $$\text{datetime.now()} \le \text{expires\_at}$$
  - Se o instante atual for estritamente posterior ao prazo de expiração ($\text{datetime.now()} > \text{expires\_at}$), o token é considerado **inválido / expirado**.
  - Tokens inexistentes são considerados **inválidos**.

---

### 2.3. Matriz de Perfis e Permissões (RBAC)

O sistema define 3 papéis (*Roles*): `Admin`, `Vendedor` e `Cliente`. Cada ação no sistema exige uma permissão explícita.

| Permissão / Ação | Admin | Vendedor | Cliente |
| :--- | :---: | :---: | :---: |
| `visualizar_relatorios` | Sim | Não | Não |
| `gerenciar_usuarios` | Sim | Não | Não |
| `configurar_sistema` | Sim | Não | Não |
| `emitir_pedidos` | Sim | Sim | Não |
| `consultar_catalogo` | Sim | Sim | Sim |

**Regras de Autorização:**
1. A checagem de permissão (`check_permission`) deve primeiro validar se o token informado é válido e não expirado. Se o token for inválido, a permissão é automaticamente negada (`False`).
2. Uma permissão deve ser concedida (`True`) **apenas e exclusivamente se** ela estiver presente na lista oficial de permissões associada ao papel do usuário autenticado.

---

## 3. Como Executar os Testes Automatizados

Certifique-se de estar no diretório raiz do projeto e execute a suíte de testes com o Pytest:

```bash
pytest test_auth_rbac.py
```

Ou, caso utilize o módulo diretamente pelo interpretador Python:

```bash
python -m pytest test_auth_rbac.py
```

### Critério de Conclusão da Tarefa
- **Estado Inicial:** A suíte executará 8 testes automatizados, dos quais alguns falharão de forma determinística devido a defeitos lógicos introduzidos na implementação.
- **Estado Concluído:** Após a correta identificação e correção dos defeitos lógicos em `auth_rbac.py`, **100% dos testes devem passar (8 passed)**.
