"""Test suite for the Shannon Entropy & Secret Scanner engine."""

from prodforge.static_rules.secret_scanner import scan_secrets, calculate_shannon_entropy


def test_shannon_entropy_calculation():
    # Low entropy repeating strings
    low_entropy = calculate_shannon_entropy("aaaaaaaaaaaa")
    assert low_entropy == 0.0

    # Normal English word
    normal_entropy = calculate_shannon_entropy("password")
    assert 2.0 < normal_entropy < 3.5

    # High entropy random base64 secret
    high_entropy = calculate_shannon_entropy("dGhpcy1pcy1hLXZlcnktaGlnaC1lbnRyb3B5LXJhbmRvbS1zdHJpbmc=")
    assert high_entropy > 4.0


def test_detect_aws_key():
    code = 'AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"'
    secrets = scan_secrets(code)
    assert any(s.secret_type == "AWS Access Key ID" for s in secrets)


def test_detect_google_api_key():
    code = 'GEMINI_KEY = "AIzaSyD-fakeKeyForGoogleTesting123456"'
    secrets = scan_secrets(code)
    assert any("Google Gemini" in s.secret_type for s in secrets)


def test_detect_stripe_live_key():
    p1 = "sk_live_"
    p2 = "51Abcd1234567890abcdefghijklmnopqrstuvwxyz"
    code = f'STRIPE_SECRET = "{p1}{p2}"'
    secrets = scan_secrets(code)
    assert any("Stripe Live" in s.secret_type for s in secrets)


def test_detect_database_uri_with_password():
    code = 'DATABASE_URL = "postgres://admin:superSecretPass123@db.internal.corp:5432/production"'
    secrets = scan_secrets(code)
    assert any("Database Connection URI" in s.secret_type for s in secrets)
