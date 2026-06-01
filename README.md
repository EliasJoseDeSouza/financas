# 💰 Finanças Família

Sistema web para controle de receitas e despesas familiares. Desenvolvido com Python (Flask) e SQLite, com interface moderna em tema escuro.

## ✨ Funcionalidades

- **Dashboard** com KPIs (total receitas, despesas, saldo, lançamentos)
- **Gráficos** comparativos por competência e distribuição receita/despesa
- **Relatórios** em tabela com filtros por tipo e competência
- **Lançamentos** com suporte a receita e despesa
- **Edição e exclusão** de lançamentos com confirmação
- Design responsivo com tema escuro e sidebar de navegação

## 🗂️ Estrutura

```
financas-familia/
├── app.py               # Aplicação Flask principal
├── database.py          # Modelos SQLAlchemy
├── requirements.txt     # Dependências Python
├── .gitignore
├── templates/
│   ├── base.html        # Layout base com sidebar
│   ├── index.html       # Dashboard
│   ├── lancamentos.html # Relatórios / listagem
│   └── form_lancamento.html  # Novo / editar lançamento
└── static/
    ├── css/style.css    # Estilos (tema escuro)
    └── js/main.js       # Scripts
```

## 🚀 Como rodar localmente

### Pré-requisitos
- Python 3.9+

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/financas-familia.git
cd financas-familia

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode a aplicação
python app.py
```

Acesse em: **http://localhost:5000**

O banco de dados SQLite (`instance/financas.db`) é criado automaticamente na primeira execução.

## 📋 Campos de lançamento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| Tipo | Seleção | Receita ou Despesa |
| Competência | Texto | Formato MM/AAAA (ex: 06/2026) |
| Descrição | Texto livre | Descrição do lançamento |
| Valor | Decimal | Valor com 2 casas decimais |
| Forma Pgto/Receb. | Texto livre | PIX, Débito, Dinheiro, etc. |

## 🛠️ Tecnologias

- **Backend**: Python 3 + Flask + SQLAlchemy
- **Banco de dados**: SQLite
- **Frontend**: HTML5 + CSS3 + Vanilla JS
- **Gráficos**: Chart.js
- **Fontes**: Syne + DM Sans (Google Fonts)
