def log(action: str, actor: str = "system", **fields) -> int:
    raise NotImplementedError


def query(filters: dict | None = None) -> list[dict]:
    raise NotImplementedError
