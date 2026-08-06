"""P0 smoke test — proves the env (pytest + hypothesis) works. Real tests arrive in P1."""
from hypothesis import given, strategies as st


@given(st.integers(), st.integers())
def test_environment_works(a, b):
    assert a + b == b + a
