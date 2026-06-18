import calendar
import csv
import io
from datetime import date

from flask import abort, make_response, render_template, request

from auth.decorators import login_required, require_role
from disciplinas import repository as disciplinas_repository
from relatorios import bp, service


@bp.get("/")
@login_required
@require_role("ADMIN")
def index():
    disciplina_id_raw = request.args.get("disciplina_id", "")
    disciplina_id = None
    if disciplina_id_raw:
        try:
            disciplina_id = int(disciplina_id_raw)
        except (TypeError, ValueError):
            disciplina_id = None

    painel = service.get_painel_horas(disciplina_id)
    disciplinas = disciplinas_repository.list_disciplinas()

    return render_template(
        "relatorios/horas.html",
        painel=painel,
        disciplinas=disciplinas,
        filtro_disciplina_id=disciplina_id,
    )


def _parse_periodo():
    hoje = date.today()
    mes_ant = hoje.month - 1 or 12
    ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
    primeiro = date(ano_ant, mes_ant, 1)
    ultimo = date(ano_ant, mes_ant, calendar.monthrange(ano_ant, mes_ant)[1])
    try:
        data_inicio = date.fromisoformat(request.args.get("data_inicio", primeiro.isoformat()))
    except (TypeError, ValueError):
        data_inicio = primeiro
    try:
        data_fim = date.fromisoformat(request.args.get("data_fim", ultimo.isoformat()))
    except (TypeError, ValueError):
        data_fim = ultimo
    return data_inicio, data_fim


@bp.get("/participacao")
@login_required
@require_role("ADMIN")
def participacao():
    disciplina_id = request.args.get("disciplina_id", type=int)
    data_inicio, data_fim = _parse_periodo()
    disciplinas = disciplinas_repository.list_disciplinas()

    relatorio = None
    if disciplina_id:
        relatorio = service.get_relatorio_participacao(disciplina_id, data_inicio, data_fim)

    return render_template(
        "relatorios/participacao.html",
        disciplinas=disciplinas,
        relatorio=relatorio,
        filtro_disciplina_id=disciplina_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@bp.get("/participacao/exportar.csv")
@login_required
@require_role("ADMIN")
def participacao_csv():
    disciplina_id = request.args.get("disciplina_id", type=int)
    if not disciplina_id:
        abort(400)
    data_inicio, data_fim = _parse_periodo()

    relatorio = service.get_relatorio_participacao(disciplina_id, data_inicio, data_fim)

    output = io.StringIO()
    writer = csv.writer(output)
    sumario = relatorio["sumario"] or {}
    writer.writerow([
        f"Relatório de Participação — {sumario.get('disciplina_codigo', '')} {sumario.get('disciplina_nome', '')}",
    ])
    writer.writerow([f"Período: {data_inicio} a {data_fim}"])
    writer.writerow([])
    writer.writerow(["Total de sessões", "Alunos atendidos", "Horas realizadas", "Monitores ativos"])
    writer.writerow([
        sumario.get("total_sessoes", 0),
        sumario.get("alunos_atendidos", 0),
        sumario.get("horas_realizadas", 0),
        sumario.get("monitores_ativos", 0),
    ])
    writer.writerow([])
    writer.writerow(["Monitor", "Sessões", "Horas", "Alunos atendidos"])
    for m in relatorio["monitores"]:
        writer.writerow([m["monitor_nome"], m["sessoes"], m["horas"], m["alunos_atendidos"]])

    nome_arquivo = (
        f"participacao_{sumario.get('disciplina_codigo', disciplina_id)}"
        f"_{data_inicio}_{data_fim}.csv"
    )
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}"
    return response
