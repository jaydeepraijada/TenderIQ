def get_client():
    raise NotImplementedError


def get_collection(name: str):
    raise NotImplementedError


def add_chunks(collection, chunks: list[dict], metadatas: list[dict]) -> None:
    raise NotImplementedError


def query(
    collection, text: str, k: int = 4, where: dict | None = None
) -> list[dict]:
    raise NotImplementedError
