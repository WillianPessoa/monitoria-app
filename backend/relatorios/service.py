import calendar
from datetime import date

from relatorios import repository


def get_relatorio_participacao(disciplina_id, data_inicio, data_fim):
    sumario = repository.get_sumario_participacao(disciplina_id, data_inicio, data_fim)
    monitores = repository.get_detalhes_por_monitor(disciplina_id, data_inicio, data_fim)
    return {
        "sumario": sumario,
        "monitores": monitores,
    }


def get_painel_horas(disciplina_id=None):
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

    minimo_horas = sum(
        1 for week in calendar.monthcalendar(hoje.year, hoje.month)
        if week[6] > 0 and date(hoje.year, hoje.month, week[6]) < hoje
    )

    linhas = repository.list_horas_por_monitor(primeiro_dia, ultimo_dia, disciplina_id)

    for linha in linhas:
        linha["abaixo_minimo"] = linha["total_horas"] < minimo_horas

    return {
        "linhas": linhas,
        "mes": hoje.month,
        "ano": hoje.year,
        "primeiro_dia": primeiro_dia,
        "ultimo_dia": ultimo_dia,
        "minimo_horas": minimo_horas,
    }
