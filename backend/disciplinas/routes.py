from datetime import datetime, time, timedelta

from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required, require_role
from disciplinas import bp, repository, service
from monitorias import service as monitoria_service
from usuarios import repository as usuarios_repository
from utils.time import hours_until, now_sp_naive, week_bounds_sp


@bp.route("/", methods=["GET", "POST"])
@login_required
@require_role("ADMIN")
def index():
    if request.method == "POST":
        codigo = request.form.get("codigo", "")
        nome = request.form.get("nome", "")
        professor_id_raw = request.form.get("professor_id", "")

        try:
            professor_id = int(professor_id_raw)
        except (TypeError, ValueError):
            professor_id = None

        disciplina_id, error = service.create_disciplina(codigo, nome, professor_id)
        if error:
            flash(error, "error")
        else:
            flash("Disciplina criada com sucesso.", "success")
            return redirect(url_for("disciplinas.index"))

    disciplinas = service.list_disciplinas()
    professores = usuarios_repository.list_active_professors()
    alunos = usuarios_repository.list_active_students()
    monitorias_ativas = monitoria_service.list_active_monitorias()
    disciplinas_admin = service.list_disciplinas_admin()
    return render_template(
        "disciplinas/index.html",
        disciplinas=disciplinas,
        disciplinas_admin=disciplinas_admin,
        professores=professores,
        alunos=alunos,
        monitorias_ativas=monitorias_ativas,
    )


@bp.post("/<int:disciplina_id>/editar")
@login_required
@require_role("ADMIN")
def editar(disciplina_id):
    codigo = request.form.get("codigo", "")
    nome = request.form.get("nome", "")
    professor_id_raw = request.form.get("professor_id", "")
    monitor_id_raw = request.form.get("monitor_id", "")

    try:
        professor_id = int(professor_id_raw)
    except (TypeError, ValueError):
        professor_id = None

    monitor_id = None
    if monitor_id_raw:
        try:
            monitor_id = int(monitor_id_raw)
        except (TypeError, ValueError):
            monitor_id = None

    if not professor_id:
        flash("Professor inválido.", "error")
        return redirect(url_for("disciplinas.index"))

    error = service.update_disciplina(disciplina_id, codigo, nome, professor_id, monitor_id)
    if error:
        flash(error, "error")
    else:
        flash("Disciplina atualizada.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/desativar")
@login_required
@require_role("ADMIN")
def desativar(disciplina_id):
    error = service.set_disciplina_status(disciplina_id, "INATIVA")
    if error:
        flash(error, "error")
    else:
        flash("Disciplina desativada.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/ativar")
@login_required
@require_role("ADMIN")
def ativar(disciplina_id):
    error = service.set_disciplina_status(disciplina_id, "ATIVA")
    if error:
        flash(error, "error")
    else:
        flash("Disciplina reativada.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/matricular")
@login_required
@require_role("ADMIN")
def matricular(disciplina_id):
    emails_raw = request.form.get("alunos_emails", "")
    if emails_raw.strip():
        normalized = emails_raw.replace(";", ",").replace("\n", ",")
        emails = [item.strip() for item in normalized.split(",")]
        error, count = service.bulk_add_alunos_to_disciplina(disciplina_id, emails)
        if error:
            flash(error, "error")
        else:
            flash(f"{count} alunos adicionados à disciplina.", "success")
        return redirect(url_for("disciplinas.index"))

    aluno_id_raw = request.form.get("aluno_id", "")
    try:
        aluno_id = int(aluno_id_raw)
    except (TypeError, ValueError):
        aluno_id = None

    if not aluno_id:
        flash("Aluno inválido.", "error")
        return redirect(url_for("disciplinas.index"))

    error = service.add_aluno_to_disciplina(disciplina_id, aluno_id)
    if error:
        flash(error, "error")
    else:
        flash("Aluno adicionado à disciplina.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.post("/<int:disciplina_id>/remover-aluno")
@login_required
@require_role("ADMIN")
def remover_aluno(disciplina_id):
    aluno_ids_raw = request.form.getlist("alunos_ids")
    if aluno_ids_raw:
        try:
            aluno_ids = [int(aluno_id) for aluno_id in aluno_ids_raw]
        except (TypeError, ValueError):
            aluno_ids = []

        if not aluno_ids:
            flash("Alunos inválidos.", "error")
            return redirect(url_for("disciplinas.index"))

        error, removed = service.bulk_remove_alunos_from_disciplina(disciplina_id, aluno_ids)
        if error:
            flash(error, "error")
        else:
            flash(f"{removed} alunos removidos da disciplina.", "success")
        return redirect(url_for("disciplinas.index"))

    aluno_id_raw = request.form.get("aluno_id", "")
    try:
        aluno_id = int(aluno_id_raw)
    except (TypeError, ValueError):
        aluno_id = None

    if not aluno_id:
        flash("Aluno inválido.", "error")
        return redirect(url_for("disciplinas.index"))

    error = service.remove_aluno_from_disciplina(disciplina_id, aluno_id)
    if error:
        flash(error, "error")
    else:
        flash("Aluno removido da disciplina.", "success")
    return redirect(url_for("disciplinas.index"))


@bp.get("/<int:disciplina_id>")
@login_required
def detalhe(disciplina_id):
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("home"))

    user_id = session.get("user_id")
    role = session.get("papel")
    monitor = monitoria_service.get_active_monitor_for_disciplina(disciplina_id)
    is_monitor_for_disciplina = monitor and monitor.get("monitor_id") == user_id
    is_aluno = role == "ALUNO" and repository.is_aluno_matriculado(disciplina_id, user_id)

    if not (is_aluno or is_monitor_for_disciplina):
        flash("Você não tem permissão para acessar esta disciplina.", "error")
        return redirect(url_for("home"))

    now_value = now_sp_naive()
    semana_inicio, semana_fim = week_bounds_sp(now_value)
    sessoes_semana = monitoria_service.get_weekly_sessions(
        disciplina_id,
        semana_inicio,
        semana_fim,
    )
    sessoes_futuras = [
        sessao for sessao in sessoes_semana if sessao["data_inicio"] >= now_value
    ]
    sessoes_passadas = [
        sessao for sessao in sessoes_semana if sessao["data_inicio"] < now_value
    ]
    can_cancel_map = {
        sessao["id"]: hours_until(sessao["data_inicio"], now_value) > 6
        for sessao in sessoes_futuras
    }

    votacao = None
    opcoes = []
    opcoes_display = []
    votacao_weekdays = []
    votacao_hours = []
    voto_atual = []
    voto_ids = set()
    show_votacao = not sessoes_futuras and monitor is not None and is_aluno
    if show_votacao:
        votacao = monitoria_service.get_open_or_create_votacao(
            disciplina_id,
            semana_inicio,
            semana_fim,
            monitor["monitor_id"],
        )
        if votacao:
            opcoes = monitoria_service.list_votacao_opcoes(votacao["id"])
            opcoes_display = [_build_opcao_display(opcao, semana_inicio) for opcao in opcoes]
            opcoes_display = [
                opcao for opcao in opcoes_display if opcao["slot1_datetime"] >= now_value
            ]
            opcoes_display = _dedupe_opcoes_por_slot(opcoes_display)
            votacao_weekdays = sorted({item["slot1_weekday"] for item in opcoes_display})
            votacao_hours = sorted({item["slot1_hour"] for item in opcoes_display if item["slot1_hour"] is not None})
            if is_aluno:
                voto_atual = monitoria_service.get_voto_by_aluno(votacao["id"], user_id)
                voto_ids = {item["opcao_id"] for item in voto_atual}

    presenca_map = {}
    if is_aluno and sessoes_semana:
        sessao_ids = [sessao["id"] for sessao in sessoes_semana]
        presencas = monitoria_service.list_presencas_for_aluno(user_id, sessao_ids)
        presenca_map = {item["sessao_id"]: item["status"] for item in presencas}

    title = f"Disciplina: {disciplina['codigo']} - {disciplina['nome']}"
    return render_template(
        "disciplinas/detalhe.html",
        section_title=title,
        disciplina=disciplina,
        monitor=monitor,
        sessoes_futuras=sessoes_futuras,
        sessoes_passadas=sessoes_passadas,
        can_cancel_map=can_cancel_map,
        presenca_map=presenca_map,
        votacao=votacao,
        opcoes=opcoes_display,
        voto_atual=voto_atual,
        voto_ids=voto_ids,
        show_votacao=show_votacao,
        votacao_weekdays=votacao_weekdays,
        votacao_hours=votacao_hours,
        is_aluno=is_aluno,
        is_monitor=is_monitor_for_disciplina,
    )


@bp.get("/<int:disciplina_id>/sessoes/<int:sessao_id>")
@login_required
def sessao_detalhe(disciplina_id, sessao_id):
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("home"))

    user_id = session.get("user_id")
    role = session.get("papel")
    monitor = monitoria_service.get_active_monitor_for_disciplina(disciplina_id)
    is_monitor_for_disciplina = monitor and monitor.get("monitor_id") == user_id
    is_aluno = role == "ALUNO" and repository.is_aluno_matriculado(disciplina_id, user_id)

    if not (is_aluno or is_monitor_for_disciplina):
        flash("Você não tem permissão para acessar esta disciplina.", "error")
        return redirect(url_for("home"))

    sessao = monitoria_service.get_session_by_id(sessao_id)
    if not sessao or sessao["disciplina_id"] != disciplina_id:
        flash("Sessão não encontrada.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    title = f"Detalhes da monitoria — {disciplina['codigo']} {disciplina['nome']}"
    return render_template("placeholder.html", section_title=title)


def _build_opcao_display(opcao, semana_inicio):
    slot1_label = _format_time_value(opcao.get("slot1_hora_inicio"))
    slot2_label = _format_time_value(opcao.get("slot2_hora_inicio")) if opcao.get("slot2_hora_inicio") else None
    slot1_hour = _extract_hour(slot1_label)
    slot1_datetime = _build_slot_datetime(semana_inicio, opcao.get("slot1_weekday"), slot1_label)
    return {
        "id": opcao.get("id"),
        "modo": opcao.get("modo"),
        "slot1_weekday": opcao.get("slot1_weekday"),
        "slot2_weekday": opcao.get("slot2_weekday"),
        "slot1_label": slot1_label,
        "slot2_label": slot2_label,
        "slot1_hour": slot1_hour,
        "slot1_datetime": slot1_datetime,
    }


def _format_time_value(value):
    if value is None:
        return ""
    if hasattr(value, "seconds"):
        hour = int(value.seconds / 3600)
        return f"{hour:02d}:00"
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    parts = str(value).split(":")
    return f"{int(parts[0]):02d}:{int(parts[1]):02d}"


def _extract_hour(label):
    try:
        return int(label.split(":")[0])
    except (AttributeError, ValueError, IndexError):
        return None


def _build_slot_datetime(semana_inicio, weekday, time_label):
    if weekday is None or not time_label:
        return now_sp_naive()
    parts = time_label.split(":")
    hour = int(parts[0])
    minute = int(parts[1])
    slot_date = semana_inicio + timedelta(days=weekday - 1)
    return datetime.combine(slot_date, time(hour=hour, minute=minute))


def _dedupe_opcoes_por_slot(opcoes):
    grouped = {}
    for opcao in opcoes:
        key = (opcao.get("slot1_weekday"), opcao.get("slot1_hour"))
        existing = grouped.get(key)
        if not existing:
            grouped[key] = opcao
            continue

        if existing.get("modo") != "BLOCO_2H" and opcao.get("modo") == "BLOCO_2H":
            grouped[key] = opcao
    return list(grouped.values())


@bp.post("/<int:disciplina_id>/votar")
@login_required
def votar(disciplina_id):
    user_id = session.get("user_id")
    role = session.get("papel")
    if role != "ALUNO" or not repository.is_aluno_matriculado(disciplina_id, user_id):
        flash("Você não tem permissão para votar.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    opcao_ids_raw = request.form.getlist("opcao_ids")
    opcao_ids = []
    for raw in opcao_ids_raw:
        try:
            opcao_ids.append(int(raw))
        except (TypeError, ValueError):
            continue

    opcao_ids = list(dict.fromkeys(opcao_ids))
    if not opcao_ids:
        flash("Escolha ao menos um horário válido.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    if len(opcao_ids) > 2:
        flash("Selecione no máximo duas opções de horário.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    now_value = now_sp_naive()
    semana_inicio, semana_fim = week_bounds_sp(now_value)
    votacao = monitoria_service.get_open_votacao(
        disciplina_id,
        semana_inicio,
        semana_fim,
    )
    if not votacao:
        flash("Votação indisponível.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    if monitoria_service.cast_vote(votacao["id"], opcao_ids, user_id):
        flash("Voto registrado com sucesso.", "success")
    else:
        flash("Não foi possível registrar seu voto.", "error")
    return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))


@bp.post("/<int:disciplina_id>/presenca")
@login_required
def presenca(disciplina_id):
    user_id = session.get("user_id")
    role = session.get("papel")
    if role != "ALUNO" or not repository.is_aluno_matriculado(disciplina_id, user_id):
        flash("Você não tem permissão para confirmar presença.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    sessao_id_raw = request.form.get("sessao_id")
    status = request.form.get("status")
    try:
        sessao_id = int(sessao_id_raw)
    except (TypeError, ValueError):
        sessao_id = None

    if not sessao_id or status not in {"CONFIRMADA", "AUSENTE"}:
        flash("Dados inválidos.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    sessao = monitoria_service.get_session_by_id(sessao_id)
    if not sessao or sessao["disciplina_id"] != disciplina_id:
        flash("Sessão não encontrada.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    if hours_until(sessao["data_inicio"], now_sp_naive()) <= 0:
        flash("A sessão já começou.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    monitoria_service.set_presenca(sessao_id, user_id, status)
    flash("Status de presença atualizado.", "success")
    return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))


@bp.post("/<int:disciplina_id>/cancelar")
@login_required
def cancelar_presenca(disciplina_id):
    user_id = session.get("user_id")
    role = session.get("papel")
    if role != "ALUNO" or not repository.is_aluno_matriculado(disciplina_id, user_id):
        flash("Você não tem permissão para cancelar.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    sessao_id_raw = request.form.get("sessao_id")
    try:
        sessao_id = int(sessao_id_raw)
    except (TypeError, ValueError):
        sessao_id = None

    if not sessao_id:
        flash("Sessão inválida.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    sessao = monitoria_service.get_session_by_id(sessao_id)
    if not sessao or sessao["disciplina_id"] != disciplina_id:
        flash("Sessão não encontrada.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    if hours_until(sessao["data_inicio"], now_sp_naive()) <= 6:
        flash("Cancelamento permitido somente com mais de 6 horas de antecedência.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    monitoria_service.set_presenca(sessao_id, user_id, "CANCELADA")
    flash("Presença cancelada.", "success")
    return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))


@bp.get("/<int:disciplina_id>/alunos")
@login_required
def alunos(disciplina_id):
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("disciplinas.index"))

    role = session.get("papel")
    read_only = True
    if role == "ADMIN":
        read_only = False
    elif role == "PROFESSOR":
        if disciplina["professor_id"] != session.get("user_id"):
            flash("Você não tem permissão para acessar esta disciplina.", "error")
            return redirect(url_for("home"))
    else:
        flash("Você não tem permissão para acessar esta disciplina.", "error")
        return redirect(url_for("home"))

    term = request.args.get("q", "").strip()
    alunos, error = service.list_alunos_by_disciplina(disciplina_id, term or None)
    if error:
        flash(error, "error")
        return redirect(url_for("disciplinas.index"))

    return render_template(
        "disciplinas/alunos.html",
        disciplina=disciplina,
        alunos=alunos,
        search_term=term,
        read_only=read_only,
    )


@bp.post("/<int:disciplina_id>/alunos/adicionar")
@login_required
@require_role("ADMIN")
def adicionar_alunos(disciplina_id):
    emails_raw = request.form.get("alunos_emails", "")
    normalized = emails_raw.replace(";", ",").replace("\n", ",")
    emails = [item.strip() for item in normalized.split(",")]

    error, count = service.bulk_add_alunos_to_disciplina(disciplina_id, emails)
    if error:
        flash(error, "error")
    else:
        flash(f"{count} alunos adicionados à disciplina.", "success")
    return redirect(url_for("disciplinas.alunos", disciplina_id=disciplina_id))


@bp.post("/<int:disciplina_id>/alunos/remover")
@login_required
@require_role("ADMIN")
def remover_alunos(disciplina_id):
    aluno_ids_raw = request.form.getlist("alunos_ids")
    try:
        aluno_ids = [int(aluno_id) for aluno_id in aluno_ids_raw]
    except (TypeError, ValueError):
        aluno_ids = []

    if not aluno_ids:
        flash("Selecione ao menos um aluno.", "error")
        return redirect(url_for("disciplinas.alunos", disciplina_id=disciplina_id))

    error, removed = service.bulk_remove_alunos_from_disciplina(disciplina_id, aluno_ids)
    if error:
        flash(error, "error")
    else:
        flash(f"{removed} alunos removidos da disciplina.", "success")
    return redirect(url_for("disciplinas.alunos", disciplina_id=disciplina_id))
