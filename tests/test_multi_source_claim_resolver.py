import json


CONTRACT = "contracts/MultiSourceClaimResolver.py"
STATEMENT = "The Example DAO proposal 42 passed with at least sixty percent support."
URLS = (
    "https://governance.example/proposal-42",
    "https://indexer.example/proposal-42",
    "https://news.example/proposal-42",
)


def _deploy(direct_deploy):
    return direct_deploy(CONTRACT, sdk_version="v0.2.12")


def _create(contract):
    return contract.create_claim(STATEMENT, URLS[0], URLS[1], URLS[2])


def _mock_sources(direct_vm):
    direct_vm.mock_web(
        r"governance\.example/proposal-42",
        {"status": 200, "body": "Official final result: passed with 68% support."},
    )
    direct_vm.mock_web(
        r"indexer\.example/proposal-42",
        {"status": 200, "body": "Proposal 42: 680 yes, 320 no; status executed."},
    )
    direct_vm.mock_web(
        r"news\.example/proposal-42",
        {"status": 200, "body": "Report: proposal 42 passed after a 68% yes vote."},
    )


def test_creation_and_input_guards(direct_vm, direct_deploy, direct_alice):
    direct_vm.check_pickling = True
    direct_vm.sender = direct_alice
    contract = _deploy(direct_deploy)

    claim_id = _create(contract)
    assert claim_id == 0
    assert contract.get_claim(0)["status"] == "PENDING"

    with direct_vm.expect_revert("three distinct"):
        contract.create_claim(STATEMENT, URLS[0], URLS[0], URLS[2])

    with direct_vm.expect_revert("http or https"):
        contract.create_claim(STATEMENT, "ipfs-value", URLS[1], URLS[2])


def test_supported_resolution_and_validator_agreement(
    direct_vm, direct_deploy, direct_alice
):
    direct_vm.sender = direct_alice
    contract = _deploy(direct_deploy)
    _create(contract)
    proposal = {
        "verdict": "SUPPORTED",
        "confidence": "HIGH",
        "support_count": 3,
        "refute_count": 0,
        "source_stances": ["SUPPORT", "SUPPORT", "SUPPORT"],
        "rationale": "All three sources report passage with 68% support.",
    }
    _mock_sources(direct_vm)
    direct_vm.mock_llm(r"Evaluate the factual claim", json.dumps(proposal))
    contract.resolve(0)

    resolved = contract.get_claim(0)
    assert resolved["status"] == "RESOLVED"
    assert resolved["verdict"] == "SUPPORTED"
    assert resolved["support_count"] == 3

    direct_vm.clear_mocks()
    _mock_sources(direct_vm)
    direct_vm.mock_llm(r"Independently audit", '{"accept": true}')
    assert direct_vm.run_validator() is True


def test_validator_rejects_inflated_consensus(
    direct_vm, direct_deploy, direct_alice
):
    direct_vm.sender = direct_alice
    contract = _deploy(direct_deploy)
    _create(contract)
    proposal = {
        "verdict": "SUPPORTED",
        "confidence": "HIGH",
        "support_count": 3,
        "refute_count": 0,
        "source_stances": ["SUPPORT", "SUPPORT", "SUPPORT"],
        "rationale": "All three sources confirm the claim.",
    }
    direct_vm.mock_web(
        r"governance\.example", {"status": 200, "body": "Passed with 68%."}
    )
    direct_vm.mock_web(
        r"indexer\.example", {"status": 200, "body": "Vote result is unavailable."}
    )
    direct_vm.mock_web(
        r"news\.example", {"status": 200, "body": "Proposal 42 was rejected."}
    )
    direct_vm.mock_llm(r"Evaluate the factual claim", json.dumps(proposal))
    contract.resolve(0)

    direct_vm.clear_mocks()
    direct_vm.mock_web(
        r"governance\.example", {"status": 200, "body": "Passed with 68%."}
    )
    direct_vm.mock_web(
        r"indexer\.example", {"status": 200, "body": "Vote result is unavailable."}
    )
    direct_vm.mock_web(
        r"news\.example", {"status": 200, "body": "Proposal 42 was rejected."}
    )
    direct_vm.mock_llm(r"Independently audit", '{"accept": false}')
    assert direct_vm.run_validator() is False


def test_structural_mismatch_is_rejected_without_llm(
    direct_vm, direct_deploy, direct_alice
):
    direct_vm.sender = direct_alice
    contract = _deploy(direct_deploy)
    _create(contract)
    malformed = {
        "verdict": "SUPPORTED",
        "confidence": "HIGH",
        "support_count": 2,
        "refute_count": 0,
        "source_stances": ["SUPPORT", "SUPPORT", "SUPPORT"],
        "rationale": "Counts do not match the stance list.",
    }
    _mock_sources(direct_vm)
    direct_vm.mock_llm(r"Evaluate the factual claim", json.dumps(malformed))
    contract.resolve(0)
    assert direct_vm.run_validator() is False
