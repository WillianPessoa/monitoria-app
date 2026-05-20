from monitorias import repository


def list_pending_monitorias():
    return repository.list_pending_monitorias()


def approve_monitoria(monitoria_id):
    return repository.approve_monitoria(monitoria_id)


def reject_monitoria(monitoria_id, motivo=None):
    return repository.reject_monitoria(monitoria_id, motivo)
