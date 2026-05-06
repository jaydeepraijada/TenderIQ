from pathlib import Path
from core.schemas import Criterion, Evidence


def process_bidder(bidder_id: str, files: list[Path]) -> None:
    raise NotImplementedError


def gather_evidence(bidder_id: str, criterion: Criterion, k: int = 4) -> list[Evidence]:
    raise NotImplementedError
