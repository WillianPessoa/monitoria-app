from monitorias import repository


def list_pending_monitorias():
    return repository.list_pending_monitorias()


def approve_monitoria(monitoria_id):
    return repository.approve_monitoria(monitoria_id)


def reject_monitoria(monitoria_id, motivo=None):
    return repository.reject_monitoria(monitoria_id, motivo)


def list_active_monitorias():
    return repository.list_active_monitorias()


def create_indicacao(disciplina_id, professor_id, aluno_id):
    return repository.create_indicacao(disciplina_id, professor_id, aluno_id)


def has_active_monitoria(aluno_id):
    return repository.has_active_monitoria(aluno_id)


def list_by_professor(professor_id):
    return repository.list_by_professor(professor_id)


def get_active_by_aluno(aluno_id):
    return repository.get_active_by_aluno(aluno_id)


def deactivate_monitorias_by_disciplina(disciplina_id, motivo):
    return repository.deactivate_monitorias_by_disciplina(disciplina_id, motivo)


def deactivate_monitoria(disciplina_id, aluno_id, motivo):
    return repository.deactivate_monitoria(disciplina_id, aluno_id, motivo)


def set_monitor_for_disciplina(disciplina_id, professor_id, aluno_id):
    return repository.set_monitor_for_disciplina(disciplina_id, professor_id, aluno_id)
