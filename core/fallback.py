from core.schemas import Criterion, Verdict


def load_criteria() -> list[Criterion]:
    raise NotImplementedError


def load_evaluation(bidder_id: str, criterion_id: str) -> Verdict:
    raise NotImplementedError
