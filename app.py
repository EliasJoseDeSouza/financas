import os
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for
from models import db, Lancamento

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# BANCO DE DADOS
# ─────────────────────────────────────────────────────────────
database_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db.init_app(app)

with app.app_context():
    db.create_all()


# ── Filtro Jinja2: formata float → R$ 1.000,00 ──
@app.template_filter("brl")
def brl_filter(value):
    try:
        value = float(value)
        neg = value < 0
        abs_val = abs(value)
        inteiro, decimal = f"{abs_val:.2f}".split(".")
        # Insere pontos de milhar
        inteiro = "{:,}".format(int(inteiro)).replace(",", ".")
        resultado = f"R$ {inteiro},{decimal}"
        return f"-{resultado}" if neg else resultado
    except (TypeError, ValueError):
        return "R$ 0,00"


@app.route("/")
def dashboard():
    # Todas as competências disponíveis (ordenadas)
    todas_competencias = sorted(
        set(r.competencia for r in Lancamento.query.all()),
        reverse=True
    )

    # Filtro selecionado via query-string (?competencia=2024-01)
    competencia_sel = request.args.get("competencia", "")

    # Query base filtrada
    query = Lancamento.query
    if competencia_sel:
        query = query.filter_by(competencia=competencia_sel)

    todos = query.all()
    receitas_list = [x for x in todos if x.tipo == "Receita"]
    despesas_list = [x for x in todos if x.tipo == "Despesa"]

    total_receitas = sum(x.valor for x in receitas_list)
    total_despesas = sum(x.valor for x in despesas_list)
    saldo = total_receitas - total_despesas

    # ── Gráfico Receitas vs Despesas por competência ──
    # Se há filtro, agrupamos pelo próprio mês; senão, por todos os meses
    if competencia_sel:
        # Mostra só a competência filtrada
        labels_rec_desp = [competencia_sel]
        dados_receitas  = [total_receitas]
        dados_despesas  = [total_despesas]
    else:
        comp_set = sorted(set(r.competencia for r in todos))
        rec_map  = defaultdict(float)
        desp_map = defaultdict(float)
        for x in todos:
            if x.tipo == "Receita":
                rec_map[x.competencia] += x.valor
            else:
                desp_map[x.competencia] += x.valor
        labels_rec_desp = comp_set
        dados_receitas  = [rec_map[c] for c in comp_set]
        dados_despesas  = [desp_map[c] for c in comp_set]

    # ── Ranking forma de recebimento (apenas Receitas) ──
    rec_forma = defaultdict(float)
    for x in receitas_list:
        rec_forma[x.forma_pagamento] += x.valor
    rank_recebimento = sorted(rec_forma.items(), key=lambda t: t[1], reverse=True)

    # ── Ranking forma de pagamento (apenas Despesas) ──
    desp_forma = defaultdict(float)
    for x in despesas_list:
        desp_forma[x.forma_pagamento] += x.valor
    rank_pagamento = sorted(desp_forma.items(), key=lambda t: t[1], reverse=True)

    return render_template(
        "dashboard.html",
        receitas=total_receitas,
        despesas=total_despesas,
        saldo=saldo,
        competencias=todas_competencias,
        competencia_sel=competencia_sel,
        labels_rec_desp=labels_rec_desp,
        dados_receitas=dados_receitas,
        dados_despesas=dados_despesas,
        rank_recebimento=rank_recebimento,
        rank_pagamento=rank_pagamento,
    )


@app.route("/lancamentos", methods=["GET", "POST"])
def lancamentos():
    if request.method == "POST":
        novo = Lancamento(
            tipo=request.form["tipo"],
            competencia=request.form["competencia"],
            descricao=request.form["descricao"],
            valor=float(request.form["valor"]),
            forma_pagamento=request.form["forma_pagamento"]
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("relatorios"))

    return render_template("lancamentos.html")


@app.route("/relatorios")
def relatorios():
    dados = Lancamento.query.order_by(Lancamento.id.desc()).all()
    return render_template("relatorios.html", dados=dados)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    item = Lancamento.query.get_or_404(id)

    if request.method == "POST":
        item.tipo            = request.form["tipo"]
        item.competencia     = request.form["competencia"]
        item.descricao       = request.form["descricao"]
        item.valor           = float(request.form["valor"])
        item.forma_pagamento = request.form["forma_pagamento"]
        db.session.commit()
        return redirect(url_for("relatorios"))

    return render_template("editar.html", item=item)


@app.route("/excluir/<int:id>")
def excluir(id):
    item = Lancamento.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("relatorios"))


if __name__ == "__main__":
    app.run(debug=True)
