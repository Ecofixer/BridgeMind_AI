from pathlib import Path

from scripts.scan_secrets import scan


def test_lowercase_python_field_is_not_a_secret_assignment() -> None:
    findings = scan(
        Path("founder_company_ai/config.py"),
        "openai_api_key: str | None\n",
    )

    assert findings == []


def test_empty_uppercase_api_key_placeholder_is_allowed() -> None:
    findings = scan(Path(".env.example"), "OPENAI_API_KEY=\n")

    assert findings == []


def test_non_empty_uppercase_api_key_assignment_is_flagged() -> None:
    findings = scan(Path("unsafe.env"), "OPENAI_API_KEY=not-a-placeholder-value\n")

    assert findings == ["non-empty sensitive assignment: OPENAI_API_KEY"]


def test_environment_expression_is_allowed() -> None:
    findings = scan(Path("workflow.yml"), "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}\n")

    assert findings == []
