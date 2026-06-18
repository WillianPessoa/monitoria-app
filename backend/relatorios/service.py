import calendar
from datetime import date

from relatorios import repository


def get_painel_horas(disciplina_id=None):
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

    semanas_no_mes = len(calendar.monthcalendar(hoje.year, hoje.month))
    minimo_horas = round(semanas_no_mes * 1, 2)

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
