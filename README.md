# Objetos experimentais D, E e F

Tarefas de depuração em Python para comparar a rapidez e a correção funcional em pair programming sem Antigravity (T1) e com Antigravity (T2).

- [Objeto D — Carrinho de compras](carrinho/README.md)
- [Objeto E — Cupons e promoções](promocoes/README.md)
- [Objeto F — Cancelamento de pedidos](cancelamentos/README.md)

## Preparação

Antes da sessão, prepare Python 3.10 ou superior, Git e Pytest na estação. Crie um ambiente virtual e instale o Pytest nele.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest==9.2.0
```

Prepare também o repositório Git do objeto com um commit inicial antes da sessão. Use o Python do ambiente virtual. No terminal com o ambiente ativado, entre na pasta do objeto atribuído e execute `python -m pytest -q`. A suíte contém seis testes. Corrija o módulo Python e mantenha os testes originais.

## Sessão

- **00:00** — Inicie a tarefa e leia o README do objeto dentro do tempo da sessão.
- **08:00** — Pare a edição, salve, rode a suíte completa e faça o commit intermediário. O observador registra a taxa de aprovação e o hash. Retome a edição em seguida.
- **16:00** — Encerre a edição, rode a suíte completa e faça o commit final. O observador registra a taxa de aprovação e o hash.
- **Conclusão antecipada** — Comunique a conclusão ao observador. Após a confirmação, encerre a edição e siga o procedimento final. O observador registra o tempo efetivo e marca o término antecipado.

Calcule a taxa de aprovação dividindo o número de testes aprovados pelos seis testes previstos e multiplicando por 100.
