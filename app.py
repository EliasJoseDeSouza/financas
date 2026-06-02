from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from models import db, Lancamento

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# BANCO DE DADOS
# O arquivo database.db fica dentro da pasta /instance
# O Render usa armazenamento temporário, por isso os dados
# somem quando o servidor reinicia. Para dados permanentes,
# use um banco externo como PostgreSQL (ex: Neon, Supabase).
# ─────────────────────────────────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def dashboard():
    receitas = Lancamento.query.filter_by(tipo="Receita").all()
    despesas = Lancamento.query.filter_by(tipo="Despesa").all()

    total_receitas = sum(x.valor for x in receitas)
    total_despesas = sum(x.valor for x in despesas)
    saldo = total_receitas - total_despesas

    return render_template(
        "dashboard.html",
        receitas=total_receitas,
        despesas=total_despesas,
        saldo=saldo
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
        item.tipo = request.form["tipo"]
        item.competencia = request.form["competencia"]
        item.descricao = request.form["descricao"]
        item.valor = float(request.form["valor"])
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
