import repository.tipo_documento_repository as repo


def listar_activos() -> list[dict]:
    """USR-RF-017."""
    return repo.listar_activos()

