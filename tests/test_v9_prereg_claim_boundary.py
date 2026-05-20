import yaml


def test_v9_prereg_claim_boundary_contract():
    doc = yaml.safe_load(open("prereg/v9_neural_temporal_agent.yaml", "r", encoding="utf-8"))
    assert "candidate agent substrate" in doc["claim"]
    assert "forbidden_claims" in doc
    forbidden = set(doc["forbidden_claims"])
    assert {"intelligence", "cognition", "AGI"}.issubset(forbidden)
    assert doc["negative_result_is_valid"] is True
