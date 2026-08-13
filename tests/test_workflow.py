from paper_agent.workflow import STAGE_ORDER, next_incomplete


def test_stage_order_starts_with_idea():
    assert STAGE_ORDER[0] == "idea"
    assert STAGE_ORDER[-1] == "camera_ready"


def test_next_incomplete():
    assert next_incomplete([]).id == "idea"
    assert next_incomplete(["idea", "venue"]).id == "literature"
    assert next_incomplete(STAGE_ORDER) is None
