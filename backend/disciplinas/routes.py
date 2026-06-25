from datetime import datetime, time, timedelta

from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required, require_role
from agenda import service as agenda_service
from disciplinas import bp, repository, service
from monitorias import service as monitoria_service
from usuarios import repository as usuarios_repository
from utils.time import hours_until, now_sp_naive, week_bounds_for_votacao, week_bounds_sp


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

    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "ATIVA")
    professor_id_filter = request.args.get("professor_id", "")
    aluno_id_filter = request.args.get("aluno_id", "")
    min_hours_filter = request.args.get("min_hours", "")

    try:
        professor_id_filter_int = int(professor_id_filter) if professor_id_filter else None
    except (TypeError, ValueError):
        professor_id_filter_int = None

    try:
        aluno_id_filter_int = int(aluno_id_filter) if aluno_id_filter else None
    except (TypeError, ValueError):
        aluno_id_filter_int = None

    if status_filter not in {"ATIVA", "INATIVA", "TODAS"}:
        status_filter = "ATIVA"

    professores = usuarios_repository.list_active_professors()
    alunos = usuarios_repository.list_active_students()
    disciplinas_admin = service.list_disciplinas_admin_filtered(
        q or None,
        status_filter,
        professor_id_filter_int,
        aluno_id_filter_int,
        min_hours_filter or None,
    )
    return render_template(
        "disciplinas/index.html",
        disciplinas_admin=disciplinas_admin,
        professores=professores,
        alunos=alunos,
        q=q,
        status_filter=status_filter,
        professor_id_filter=professor_id_filter,
        aluno_id_filter=aluno_id_filter,
        min_hours_filter=min_hours_filter,
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

    is_professor_responsavel = role == "PROFESSOR" and disciplina["professor_id"] == user_id
    is_admin = role == "ADMIN"

    if not (is_aluno or is_monitor_for_disciplina or is_professor_responsavel or is_admin):
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

    votacao = None
    opcoes = []
    opcoes_display = []
    votacao_weekdays = []
    votacao_hours = []
    voto_atual = []
    voto_ids = set()
    votacao_votos = {}
    votacao_slot_duration = 1
    votacao_max_select = 1
    votacao_semana_inicio, votacao_semana_fim = week_bounds_for_votacao(now_value)
    sessoes_votacao_semana = monitoria_service.get_weekly_sessions(
        disciplina_id,
        votacao_semana_inicio,
        votacao_semana_fim,
    )
    sessoes_votacao_futuras = [
        sessao for sessao in sessoes_votacao_semana if sessao["data_inicio"] >= now_value
    ]
    show_votacao = not sessoes_votacao_futuras and monitor is not None and is_aluno
    if show_votacao:
        votacao = monitoria_service.get_open_or_create_votacao(
            disciplina_id,
            votacao_semana_inicio,
            votacao_semana_fim,
            monitor["monitor_id"],
        )
        if votacao:
            weekly_hours, split_mode = monitoria_service.get_votacao_config(votacao)
            votacao_slot_duration = 2 if weekly_hours == 2 and split_mode == "CONSECUTIVAS" else 1
            votacao_max_select = 1 if weekly_hours == 1 or split_mode == "CONSECUTIVAS" else 2
            opcoes = monitoria_service.list_votacao_opcoes(votacao["id"])
            resultados = monitoria_service.list_votacao_resultados(votacao["id"])
            for opcao in resultados:
                modo = opcao.get("modo")
                if modo != "SLOT_1H" and modo != "BLOCO_2H":
                    continue

                slot1_hour = int(str(opcao["slot1_hora_inicio"]).split(":")[0])
                key1 = (opcao["slot1_weekday"], slot1_hour)
                votacao_votos[key1] = max(votacao_votos.get(key1, 0), opcao["votos"])
            opcoes_display = _build_opcoes_display(
                opcoes,
                votacao_semana_inicio,
                weekly_hours,
                split_mode,
            )
            opcoes_display = [
                opcao for opcao in opcoes_display if opcao["slot_datetime"] >= now_value
            ]
            votacao_weekdays = sorted({item["weekday"] for item in opcoes_display})
            votacao_hours = sorted(
                {item["hour"] for item in opcoes_display if item["hour"] is not None}
            )
            if is_aluno:
                voto_atual = monitoria_service.get_voto_by_aluno(votacao["id"], user_id)
                voto_ids = {item["opcao_id"] for item in voto_atual}

    presenca_map = {}
    can_cancel_map = {}
    past_sessions_aluno = []
    if is_aluno and sessoes_semana:
        sessao_ids = [sessao["id"] for sessao in sessoes_semana]
        presencas = monitoria_service.list_presencas_for_aluno(user_id, sessao_ids)
        presenca_map = {item["sessao_id"]: item["status"] for item in presencas}

    if is_aluno:
        past_sessions_aluno = agenda_service.list_past_sessions_for_aluno_in_disciplina(user_id, disciplina_id)

    for sessao in sessoes_futuras:
        can_cancel_map[sessao["id"]] = hours_until(sessao["data_inicio"], now_value) > 6

    title = f"Disciplina: {disciplina['codigo']} - {disciplina['nome']}"
    return render_template(
        "disciplinas/detalhe.html",
        section_title=title,
        disciplina=disciplina,
        monitor=monitor,
        sessoes_semana=sessoes_semana,
        sessoes_futuras=sessoes_futuras,
        sessoes_passadas=sessoes_passadas,
        past_sessions_aluno=past_sessions_aluno,
        can_cancel_map=can_cancel_map,
        presenca_map=presenca_map,
        votacao=votacao,
        opcoes=opcoes_display,
        voto_atual=voto_atual,
        voto_ids=voto_ids,
        show_votacao=show_votacao,
        votacao_weekdays=votacao_weekdays,
        votacao_hours=votacao_hours,
        votacao_slot_duration=votacao_slot_duration,
        votacao_max_select=votacao_max_select,
        votacao_votos=votacao_votos,
        is_aluno=is_aluno,
        is_monitor=is_monitor_for_disciplina,
    )


def _build_opcoes_display(opcoes, semana_inicio, weekly_hours, split_mode):
    allowed_modes = {"SLOT_1H", "BLOCO_2H"}

    display = []
    for opcao in opcoes:
        if opcao.get("modo") not in allowed_modes:
            continue
        display.extend(_expand_opcao_display(opcao, semana_inicio))
    return _dedupe_slots(display)


def _expand_opcao_display(opcao, semana_inicio):
    modo = opcao.get("modo")
    slot1_label = _format_time_value(opcao.get("slot1_hora_inicio"))
    slot1_hour = _extract_hour(slot1_label)
    slot1_datetime = _build_slot_datetime(semana_inicio, opcao.get("slot1_weekday"), slot1_label)

    entries = [
        {
            "id": opcao.get("id"),
            "modo": modo,
            "weekday": opcao.get("slot1_weekday"),
            "hour": slot1_hour,
            "slot_datetime": slot1_datetime,
            "duration": 2 if modo == "BLOCO_2H" else 1,
        }
    ]
    return entries


def _dedupe_slots(opcoes):
    seen = set()
    filtered = []
    for opcao in opcoes:
        key = (opcao.get("weekday"), opcao.get("hour"))
        if key in seen:
            continue
        seen.add(key)
        filtered.append(opcao)
    return filtered


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
    semana_inicio, semana_fim = week_bounds_for_votacao(now_value)
    votacao = monitoria_service.get_open_votacao(
        disciplina_id,
        semana_inicio,
        semana_fim,
    )
    if not votacao:
        flash("Votação indisponível.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    weekly_hours, split_mode = monitoria_service.get_votacao_config(votacao)
    max_select = 1 if weekly_hours == 1 or split_mode == "CONSECUTIVAS" else 2
    if len(opcao_ids) > max_select:
        message = "Selecione apenas 1 opção de horário." if max_select == 1 else "Selecione no máximo duas opções de horário."
        flash(message, "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    valid_opcao_ids = {opcao["id"] for opcao in monitoria_service.list_votacao_opcoes(votacao["id"])}
    if not all(oid in valid_opcao_ids for oid in opcao_ids):
        flash("Opção de horário inválida.", "error")
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
        flash("Cancelamento não permitido com menos de 6 horas de antecedência", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    presenca = monitoria_service.get_presenca(sessao_id, user_id)
    if not presenca or presenca.get("status") != "CONFIRMADA":
        flash("Somente presenças confirmadas podem ser canceladas.", "error")
        return redirect(url_for("disciplinas.detalhe", disciplina_id=disciplina_id))

    monitoria_service.set_presenca(sessao_id, user_id, "AUSENTE")
    flash("Ausência confirmada.", "success")
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


@bp.get("/<int:disciplina_id>/historico")
@login_required
def historico(disciplina_id):
    user_id = session.get("user_id")
    role = session.get("papel")
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("home"))

    if role == "PROFESSOR":
        if disciplina["professor_id"] != user_id:
            flash("Você não tem permissão para acessar o histórico desta disciplina.", "error")
            return redirect(url_for("home"))
    elif role != "ADMIN":
        flash("Você não tem permissão para acessar o histórico desta disciplina.", "error")
        return redirect(url_for("home"))

    registros, error = service.get_historico_atendimentos(disciplina_id, user_id if role == "PROFESSOR" else None)
    if error:
        flash(error, "error")
        return redirect(url_for("home"))

    title = f"Histórico de atendimentos — {disciplina['codigo']} - {disciplina['nome']}"
    return render_template(
        "disciplinas/historico.html",
        section_title=title,
        disciplina=disciplina,
        registros=registros,
    )


@bp.get("/<int:disciplina_id>/monitoria")
@login_required
def monitoria_detalhe(disciplina_id):
    user_id = session.get("user_id")
    role = session.get("papel")
    disciplina = service.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        flash("Disciplina não encontrada.", "error")
        return redirect(url_for("home"))

    is_admin = role == "ADMIN"
    is_professor_responsavel = (
        role == "PROFESSOR" and disciplina["professor_id"] == user_id
    )
    monitor = monitoria_service.get_active_monitor_for_disciplina(disciplina_id)
    is_monitor_for_this = bool(monitor and monitor.get("monitor_id") == user_id)

    if not is_admin and not is_professor_responsavel and not is_monitor_for_this:
        flash("Você não tem permissão para acessar esta página.", "error")
        return redirect(url_for("home"))

    now_value = now_sp_naive()
    pode_adicionar = is_admin
    alunos = service.list_alunos_com_presencas(disciplina_id)
    total_horas = service.get_total_horas_concluidas(disciplina_id)
    sessoes = service.list_sessoes_resumo(disciplina_id)
    proxima_sessao = monitoria_service.get_next_session(disciplina_id, now_value)
    sessoes_pendentes = monitoria_service.list_sessoes_pendentes_disciplina(disciplina_id)

    session_alunos_map = {}
    if is_monitor_for_this:
        for s in sessoes_pendentes:
            session_alunos_map[s["id"]] = monitoria_service.list_alunos_for_sessao(disciplina_id, s["id"])

    return render_template(
        "disciplinas/monitoria_detalhe.html",
        disciplina=disciplina,
        monitor=monitor,
        alunos=alunos,
        total_horas=total_horas,
        sessoes=sessoes,
        proxima_sessao=proxima_sessao,
        sessoes_pendentes=sessoes_pendentes,
        pode_adicionar=pode_adicionar,
        is_monitor=is_monitor_for_this,
        session_alunos_map=session_alunos_map,
        now_value=now_value,
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
