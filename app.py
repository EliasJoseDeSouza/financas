import os
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from sqlalchemy import func

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


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():

    # Todas as competências cadastradas (para o filtro)
    competencias = db.session.query(Lancamento.competencia)\
        .distinct()\
        .order_by(Lancamento.competencia.desc())\
        .all()
    competencias = [c[0] for c in competencias]

    # Competência selecionada via ?competencia=XX/XXXX
    competencia_sel = request.args.get("competencia", "todas")

    # Query base: com ou sem filtro
    if competencia_sel == "todas" or competencia_sel not in competencias:
        competencia_sel = "todas"
        query_base = Lancamento.query
        filtro_extra = []
    else:
        query_base = Lancamento.query.filter_by(competencia=competencia_sel)
        filtro_extra = [Lancamento.competencia == competencia_sel]

    receitas_list = query_base.filter_by(tipo="Receita").all()
    despesas_list = query_base.filter_by(tipo="Despesa").all()

    total_receitas = sum(x.valor for x in receitas_list)
    total_despesas = sum(x.valor for x in despesas_list)
    saldo = total_receitas - total_despesas

    # ── Ranking Forma de Recebimento (Receitas) ──────────────
    q_rec = db.session.query(
        Lancamento.forma_pagamento,
        func.sum(Lancamento.valor).label("total")
    ).filter(Lancamento.tipo == "Receita", *filtro_extra)\
     .group_by(Lancamento.forma_pagamento)\
     .order_by(func.sum(Lancamento.valor).desc())\
     .all()

    # ── Ranking Forma de Pagamento (Despesas) ─────────────────
    q_desp = db.session.query(
        Lancamento.forma_pagamento,
        func.sum(Lancamento.valor).label("total")
    ).filter(Lancamento.tipo == "Despesa", *filtro_extra)\
     .group_by(Lancamento.forma_pagamento)\
     .order_by(func.sum(Lancamento.valor).desc())\
     .all()

    # ── Histórico Receitas vs Despesas (todas as competências) ─
    hist_rec = db.session.query(
        Lancamento.competencia,
        func.sum(Lancamento.valor).label("total")
    ).filter_by(tipo="Receita")\
     .group_by(Lancamento.competencia)\
     .order_by(Lancamento.competencia)\
     .all()

    hist_desp = db.session.query(
        Lancamento.competencia,
        func.sum(Lancamento.valor).label("total")
    ).filter_by(tipo="Despesa")\
     .group_by(Lancamento.competencia)\
     .order_by(Lancamento.competencia)\
     .all()

    meses_set  = sorted(set([r[0] for r in hist_rec] + [d[0] for d in hist_desp]))
    rec_dict   = {r[0]: float(r[1]) for r in hist_rec}
    desp_dict  = {d[0]: float(d[1]) for d in hist_desp}
    meses_rec  = [rec_dict.get(m, 0)  for m in meses_set]
    meses_desp = [desp_dict.get(m, 0) for m in meses_set]

    return render_template(
        "dashboard.html",
        receitas=total_receitas,
        despesas=total_despesas,
        saldo=saldo,
        competencias=competencias,
        competencia_sel=competencia_sel,
        ranking_recebimento=q_rec,
        ranking_pagamento=q_desp,
        meses_labels=meses_set,
        meses_rec=meses_rec,
        meses_desp=meses_desp,
    )


# ─────────────────────────────────────────────────────────────
# LANÇAMENTOS
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# RELATÓRIOS
# ─────────────────────────────────────────────────────────────
@app.route("/relatorios")
def relatorios():
    dados = Lancamento.query.order_by(Lancamento.id.desc()).all()
    return render_template("relatorios.html", dados=dados)


# ─────────────────────────────────────────────────────────────
# EDITAR
# ─────────────────────────────────────────────────────────────
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    item = Lancamento.query.get_or_404(id)

    if request.method == "POST":
        item.tipo = request.form["tipo"]
        item.competencia = request.form["competencia"]
        item.descricao = request.form["descricao"]
        item.valor = float(request.form["valor"])
        item.forma_pagamento = request.form["forma_pagamento"]
        db.session.commit()
        return redirect(url_for("relatorios"))

    return render_template("editar.html", item=item)


# ─────────────────────────────────────────────────────────────
# EXCLUIR
# ─────────────────────────────────────────────────────────────
@app.route("/excluir/<int:id>")
def excluir(id):
    item = Lancamento.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("relatorios"))


if __name__ == "__main__":
    app.run(debug=True)
