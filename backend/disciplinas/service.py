from disciplinas import repository
from monitorias import service as monitoria_service
from usuarios import repository as usuarios_repository


def list_disciplinas():
    return repository.list_disciplinas()


def list_by_professor(professor_id):
    return repository.list_by_professor(professor_id)


def list_by_professor_with_stats(professor_id):
    disciplinas = repository.list_by_professor_with_stats(professor_id)
    for disciplina in disciplinas:
        disciplina["alunos"] = repository.list_alunos_by_disciplina(disciplina["id"])
        disciplina["alunos_nao_matriculados"] = repository.list_alunos_nao_matriculados(
            disciplina["id"]
        )
    return disciplinas


def get_disciplina_by_id(disciplina_id):
    return repository.get_disciplina_by_id(disciplina_id)


def list_disciplinas_admin():
    disciplinas = repository.list_disciplinas_admin()
    for disciplina in disciplinas:
        disciplina["alunos"] = repository.list_alunos_by_disciplina(disciplina["id"])
    return disciplinas


def list_alunos_by_disciplina(disciplina_id, term=None):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return None, "Disciplina não encontrada."

    if term:
        alunos = repository.list_alunos_by_disciplina_filtered(disciplina_id, term)
    else:
        alunos = repository.list_alunos_by_disciplina(disciplina_id)
    return alunos, None


def create_disciplina(codigo, nome, professor_id):
    normalized_codigo = (codigo or "").strip().upper()
    nome = (nome or "").strip()

    if not normalized_codigo or not nome:
        return None, "Código e nome são obrigatórios."

    professor = usuarios_repository.get_user_by_id(professor_id)
    if not professor or professor["papel"] != "PROFESSOR" or professor["status"] != "ATIVO":
        return None, "Professor inválido."

    if repository.get_disciplina_by_codigo(normalized_codigo):
        return None, "Código já cadastrado."

    disciplina_id = repository.create_disciplina(normalized_codigo, nome, professor_id)
    return disciplina_id, None


def update_disciplina(disciplina_id, codigo, nome, professor_id, monitor_id):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return "Disciplina não encontrada."

    normalized_codigo = (codigo or "").strip().upper()
    nome = (nome or "").strip()

    if not normalized_codigo or not nome:
        return "Código e nome são obrigatórios."

    professor = usuarios_repository.get_user_by_id(professor_id)
    if not professor or professor["papel"] != "PROFESSOR" or professor["status"] != "ATIVO":
        return "Professor inválido."

    existing = repository.get_disciplina_by_codigo(normalized_codigo)
    if existing and existing["id"] != disciplina_id:
        return "Código já cadastrado."

    repository.update_disciplina(disciplina_id, normalized_codigo, nome, professor_id)

    if monitor_id is not None:
        aluno = usuarios_repository.get_user_by_id(monitor_id)
        if not aluno or aluno["papel"] != "ALUNO" or aluno["status"] != "ATIVO":
            return "Aluno inválido."

        if repository.is_aluno_matriculado(disciplina_id, monitor_id):
            repository.remove_aluno_from_disciplina(disciplina_id, monitor_id)

    success, error = monitoria_service.set_monitor_for_disciplina(
        disciplina_id,
        professor_id,
        monitor_id,
    )
    if not success:
        return error

    return None


def set_disciplina_status(disciplina_id, status):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return "Disciplina não encontrada."

    if status not in {"ATIVA", "INATIVA"}:
        return "Status inválido."

    if not repository.set_disciplina_status(disciplina_id, status):
        return "Não foi possível atualizar a disciplina."

    if status == "INATIVA":
        monitoria_service.deactivate_monitorias_by_disciplina(
            disciplina_id,
            "Disciplina desativada pelo admin.",
        )

    return None


def add_aluno_to_disciplina(disciplina_id, aluno_id):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return "Disciplina não encontrada."

    aluno = usuarios_repository.get_user_by_id(aluno_id)
    if not aluno or aluno["papel"] != "ALUNO" or aluno["status"] != "ATIVO":
        return "Aluno inválido."

    monitoria = monitoria_service.get_active_by_aluno(aluno_id)
    if monitoria and monitoria["disciplina_id"] == disciplina_id:
        return "Aluno já é monitor desta disciplina."

    repository.add_aluno_to_disciplina(disciplina_id, aluno_id)
    return None


def bulk_add_alunos_to_disciplina(disciplina_id, emails):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return "Disciplina não encontrada.", 0

    normalized = sorted({email.strip().lower() for email in emails if email.strip()})
    if not normalized:
        return "Nenhum e-mail válido informado.", 0

    alunos = usuarios_repository.list_active_students_by_emails(normalized)
    alunos_by_email = {aluno["email"].lower(): aluno for aluno in alunos}

    missing = [email for email in normalized if email not in alunos_by_email]
    if missing:
        return "E-mails não encontrados ou inativos: " + ", ".join(missing), 0

    for aluno in alunos:
        monitoria = monitoria_service.get_active_by_aluno(aluno["id"])
        if monitoria and monitoria["disciplina_id"] == disciplina_id:
            return f"{aluno['nome']} já é monitor desta disciplina.", 0

    for aluno in alunos:
        repository.add_aluno_to_disciplina(disciplina_id, aluno["id"])

    return None, len(alunos)


def remove_aluno_from_disciplina(disciplina_id, aluno_id):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return "Disciplina nao encontrada."

    removed = repository.remove_aluno_from_disciplina(disciplina_id, aluno_id)
    if removed:
        monitoria_service.deactivate_monitoria(
            disciplina_id,
            aluno_id,
            "Aluno removido da disciplina pelo admin.",
        )
    return None


def bulk_remove_alunos_from_disciplina(disciplina_id, aluno_ids):
    disciplina = repository.get_disciplina_by_id(disciplina_id)
    if not disciplina:
        return "Disciplina não encontrada.", 0

    removed = repository.remove_alunos_from_disciplina(disciplina_id, aluno_ids)
    for aluno_id in aluno_ids:
        monitoria_service.deactivate_monitoria(
            disciplina_id,
            aluno_id,
            "Aluno removido da disciplina pelo admin.",
        )
    return None, removed


def list_disciplinas_by_aluno(aluno_id):
    return repository.list_disciplinas_by_aluno(aluno_id)


def count_alunos_disciplina(disciplina_id):
    return repository.count_alunos_disciplina(disciplina_id)
