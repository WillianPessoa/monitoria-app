from flask import flash, redirect, render_template, request, session, url_for

from auth.decorators import login_required, require_role
from monitorias import service as monitoria_service
from usuarios import bp, repository, service


@bp.route("/", methods=["GET", "POST"])
@login_required
@require_role("ADMIN")
def index():
    generated_password = None

    if request.method == "POST":
        nome = request.form.get("nome", "")
        email = request.form.get("email", "")
        papel = request.form.get("papel", "")

        _, generated_password, error = service.create_user(nome, email, papel)
        if error:
            flash(error, "error")
        else:
            flash("Usuário criado com status PENDENTE.", "success")

    users = repository.list_users()
    return render_template(
        "usuarios/index.html",
        users=users,
        generated_password=generated_password,
    )


@bp.post("/<int:user_id>/desativar")
@login_required
@require_role("ADMIN")
def deactivate(user_id):
    if user_id == session.get("user_id"):
        flash("Você não pode desativar o próprio usuário.", "error")
        return redirect(url_for("usuarios.index"))

    if service.deactivate_user(user_id):
        flash("Usuário desativado com sucesso.", "success")
    else:
        flash("Usuário não encontrado.", "error")
    return redirect(url_for("usuarios.index"))


@bp.post("/<int:user_id>/reativar")
@login_required
@require_role("ADMIN")
def reactivate(user_id):
    if service.reactivate_user(user_id):
        flash("Usuário reativado com sucesso.", "success")
    else:
        flash("Usuário não encontrado.", "error")
    return redirect(url_for("usuarios.index"))


@bp.post("/<int:user_id>/resetar-senha")
@login_required
@require_role("ADMIN")
def reset_password(user_id):
    if user_id == session.get("user_id"):
        flash("Você não pode resetar a própria senha por esta tela.", "error")
        return redirect(url_for("usuarios.index"))

    temporary_password = service.reset_user_password(user_id)
    if temporary_password:
        flash(
            f"Senha redefinida. Nova senha temporária: {temporary_password}",
            "success",
        )
    else:
        flash("Usuário não encontrado.", "error")

    return redirect(url_for("usuarios.index"))


@bp.route("/meu-perfil", methods=["GET", "POST"])
@login_required
def my_profile():
    user_id = session.get("user_id")
    user = repository.get_user_by_id(user_id)

    role = session.get("papel")
    is_monitor = role == "MONITOR" or (
        role == "ALUNO" and monitoria_service.has_active_monitoria(user_id)
    )
    if not is_monitor:
        flash("Você não tem permissão para acessar esta página.", "error")
        return redirect(url_for("home"))

    disponibilidade_slots = repository.list_monitor_disponibilidade(user_id)
    selected_keys = set()
    selected_block_keys = set()
    weekday_hours = {}

    for slot in disponibilidade_slots:
        hora_inicio = slot.get("hora_inicio")
        if hasattr(hora_inicio, "seconds"):
            hour_value = int(hora_inicio.seconds / 3600)
        else:
            hour_value = int(str(hora_inicio).split(":")[0])
        weekday = slot["weekday"]
        selected_keys.add(f"{weekday}|{hour_value}")
        weekday_hours.setdefault(weekday, []).append(hour_value)

    for weekday, hours in weekday_hours.items():
        hours_set = set(hours)
        for hour in sorted(hours):
            if hour in hours_set and (hour + 1) in hours_set:
                selected_block_keys.add(f"{weekday}|{hour}")
                hours_set.remove(hour)
                hours_set.remove(hour + 1)

    if request.method == "POST":
        contato_tipo = request.form.get("contato_tipo", "").strip()
        contato_valor = request.form.get("contato_valor", "").strip()
        slots_raw = request.form.getlist("slots")
        carga_raw = request.form.get("carga_horaria", "1")
        modo_2h = request.form.get("modo_2h", "CONSECUTIVAS").upper()

        try:
            carga_horaria = int(carga_raw)
        except (TypeError, ValueError):
            carga_horaria = 1

        slots_payload = []
        intervals_by_weekday = {}
        slot_keys = set()

        def has_overlap(weekday, start, end):
            for existing_start, existing_end in intervals_by_weekday.get(weekday, []):
                if start < existing_end and existing_start < end:
                    return True
            return False

        for raw in slots_raw:
            try:
                parts = raw.split("|")
                weekday_str = parts[0]
                hour_str = parts[1]
                duration_str = parts[2] if len(parts) > 2 else "1"
                weekday = int(weekday_str)
                hour = int(hour_str)
                duration = int(duration_str)
            except (ValueError, TypeError):
                continue

            start = hour
            end = hour + (2 if duration == 2 else 1)
            if has_overlap(weekday, start, end):
                flash("Selecione horários sem sobreposição.", "error")
                return redirect(url_for("usuarios.my_profile"))

            intervals_by_weekday.setdefault(weekday, []).append((start, end))
            for h in range(start, end):
                slot_key = (weekday, h)
                if slot_key in slot_keys:
                    flash("Selecione horários sem sobreposição.", "error")
                    return redirect(url_for("usuarios.my_profile"))
                slot_keys.add(slot_key)
                slots_payload.append({"weekday": weekday, "hora_inicio": f"{h:02d}:00:00"})

        ok, error_msg = service.update_monitor_profile(
            user_id,
            contato_tipo,
            contato_valor,
            slots_payload,
            carga_horaria,
            modo_2h,
        )
        if ok:
            flash("Perfil atualizado com sucesso.", "success")
            return redirect(url_for("usuarios.my_profile"))

        flash(error_msg, "error")

    contato_tipo = ""
    contato_valor = user.get("contato") or ""
    if "@" in contato_valor:
        contato_tipo = "email"
    elif contato_valor:
        contato_tipo = "celular"

    carga_horaria = user.get("carga_horaria_semanal") or 1
    modo_2h = user.get("modo_2h") or "CONSECUTIVAS"

    return render_template(
        "usuarios/my_profile.html",
        user=user,
        disponibilidade_slots=disponibilidade_slots,
        selected_keys=selected_keys,
        selected_block_keys=selected_block_keys,
        contato_tipo=contato_tipo,
        contato_valor=contato_valor,
        carga_horaria=carga_horaria,
        modo_2h=modo_2h,
    )


