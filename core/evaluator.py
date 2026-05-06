from core.schemas import Criterion, Verdict


def evaluate(bidder_id: str, criterion: Criterion) -> Verdict:
    raise NotImplementedError


def evaluate_bidder(bidder_id: str, criteria: list[Criterion]) -> list[Verdict]:
    raise NotImplementedError
