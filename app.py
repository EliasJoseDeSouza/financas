from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from database import db, Lancamento
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'financas-familia-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    lancamentos = Lancamento.query.all()

    total_receita = sum(l.valor for l in lancamentos if l.tipo == 'receita')
    total_despesa = sum(l.valor for l in lancamentos if l.tipo == 'despesa')
    saldo = total_receita - total_despesa

    despesas_por_tipo = {}
    for l in lancamentos:
        if l.tipo == 'despesa':
            if l.descricao not in despesas_por_tipo:
                despesas_por_tipo[l.descricao] = 0
            despesas_por_tipo[l.descricao] += l.valor

    # Agrupar por competência
    por_competencia = {}
    for l in lancamentos:
        comp = l.competencia
        if comp not in por_competencia:
            por_competencia[comp] = {'receita': 0, 'despesa': 0}
        por_competencia[comp][l.tipo] += l.valor

    competencias_sorted = sorted(por_competencia.keys(), key=lambda x: (
        int(x.split('/')[1]), int(x.split('/')[0])
    ) if '/' in x else (0, 0))

    chart_labels = competencias_sorted[-6:] if len(competencias_sorted) > 6 else competencias_sorted
    chart_receitas = [round(por_competencia[c]['receita'], 2) for c in chart_labels]
    chart_despesas = [round(por_competencia[c]['despesa'], 2) for c in chart_labels]

    # Top despesas por descrição
    top_despesas = sorted(despesas_por_tipo.items(), key=lambda x: x[1], reverse=True)[:8]

    return render_template('index.html',
        total_receita=total_receita,
        total_despesa=total_despesa,
        saldo=saldo,
        top_despesas=top_despesas,
        chart_labels=chart_labels,
        chart_receitas=chart_receitas,
        chart_despesas=chart_despesas,
        total_lancamentos=len(lancamentos)
    )


@app.route('/lancamentos')
def lancamentos():
    tipo = request.args.get('tipo', '')
    competencia = request.args.get('competencia', '')

    query = Lancamento.query
    if tipo:
        query = query.filter_by(tipo=tipo)
    if competencia:
        query = query.filter_by(competencia=competencia)

    items = query.order_by(Lancamento.id.desc()).all()
    competencias = db.session.query(Lancamento.competencia).distinct().all()
    competencias = [c[0] for c in competencias]

    return render_template('lancamentos.html',
        lancamentos=items,
        competencias=competencias,
        filtro_tipo=tipo,
        filtro_competencia=competencia
    )


@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        competencia = request.form.get('competencia', '').strip()
        descricao = request.form.get('descricao', '').strip()
        valor_str = request.form.get('valor', '').strip().replace(',', '.')
        forma = request.form.get('forma', '').strip()

        errors = []
        if not tipo:
            errors.append('Tipo é obrigatório.')
        if not competencia:
            errors.append('Competência é obrigatória.')
        if not descricao:
            errors.append('Descrição é obrigatória.')
        if not valor_str:
            errors.append('Valor é obrigatório.')
        else:
            try:
                valor = float(valor_str)
                if valor <= 0:
                    errors.append('Valor deve ser maior que zero.')
            except ValueError:
                errors.append('Valor inválido.')
        if not forma:
            errors.append('Forma de pagamento/recebimento é obrigatória.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('form_lancamento.html',
                titulo='Novo Lançamento',
                action=url_for('novo'),
                dados=request.form
            )

        lancamento = Lancamento(
            tipo=tipo,
            competencia=competencia,
            descricao=descricao,
            valor=float(valor_str),
            forma=forma,
            criado_em=datetime.now()
        )
        db.session.add(lancamento)
        db.session.commit()
        flash('Lançamento criado com sucesso!', 'success')
        return redirect(url_for('lancamentos'))

    return render_template('form_lancamento.html',
        titulo='Novo Lançamento',
        action=url_for('novo'),
        dados={}
    )


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    lancamento = Lancamento.query.get_or_404(id)

    if request.method == 'POST':
        tipo = request.form.get('tipo', '').strip()
        competencia = request.form.get('competencia', '').strip()
        descricao = request.form.get('descricao', '').strip()
        valor_str = request.form.get('valor', '').strip().replace(',', '.')
        forma = request.form.get('forma', '').strip()

        errors = []
        if not tipo: errors.append('Tipo é obrigatório.')
        if not competencia: errors.append('Competência é obrigatória.')
        if not descricao: errors.append('Descrição é obrigatória.')
        if not valor_str:
            errors.append('Valor é obrigatório.')
        else:
            try:
                valor = float(valor_str)
                if valor <= 0:
                    errors.append('Valor deve ser maior que zero.')
            except ValueError:
                errors.append('Valor inválido.')
        if not forma: errors.append('Forma de pagamento/recebimento é obrigatória.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('form_lancamento.html',
                titulo='Editar Lançamento',
                action=url_for('editar', id=id),
                dados=request.form,
                lancamento=lancamento
            )

        lancamento.tipo = tipo
        lancamento.competencia = competencia
        lancamento.descricao = descricao
        lancamento.valor = float(valor_str)
        lancamento.forma = forma
        db.session.commit()
        flash('Lançamento atualizado com sucesso!', 'success')
        return redirect(url_for('lancamentos'))

    dados = {
        'tipo': lancamento.tipo,
        'competencia': lancamento.competencia,
        'descricao': lancamento.descricao,
        'valor': f'{lancamento.valor:.2f}',
        'forma': lancamento.forma
    }
    return render_template('form_lancamento.html',
        titulo='Editar Lançamento',
        action=url_for('editar', id=id),
        dados=dados,
        lancamento=lancamento
    )


@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    lancamento = Lancamento.query.get_or_404(id)
    db.session.delete(lancamento)
    db.session.commit()
    flash('Lançamento excluído com sucesso!', 'success')
    return redirect(url_for('lancamentos'))


if __name__ == '__main__':
    app.run(debug=True)
