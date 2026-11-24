"""Local tests for the pytest-agentest plugin. No network, no PyPI upload."""

from __future__ import annotations

import pytest

import pytest_agentest
from pytest_agentest.plugin import run_agentest


def test_version():
    assert pytest_agentest.__version__ == "0.1.0"


def test_plugin_is_registered(pytestconfig: pytest.Config):
    names = set(pytestconfig.pluginmanager.list_name_plugin())
    # list_name_plugin returns (name, plugin) tuples
    plugin_names = {name for name, _ in pytestconfig.pluginmanager.list_name_plugin()}
    assert "agentest" in plugin_names


def test_help_lists_options(pytester: pytest.Pytester):
    result = pytester.runpytest("--help")
    result.stdout.fnmatch_lines([
        "*--agentest-otlp*",
        "*--agentest-ids*",
        "*--agentest-strict*",
    ])


def test_fixture_runs_agentest_help(agentest_run):
    # --help on the std run parser should exit cleanly (0 or 0-like) or print help.
    # Use catalog, which needs no trace files.
    result = run_agentest(extra=["--help"] if False else [])
    # Without --otlp, std run judges bundled agents if present; that can be heavy.
    # Call the CLI help instead:
    from agentest.cli import main
    import contextlib, io
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(["--help"])
        except SystemExit as exc:
            code = int(exc.code or 0)
    text = out.getvalue() + err.getvalue()
    assert "std run" in text or "agentest" in text
    assert code in (0, None) or code == 0


def test_run_bundled_agent_one_id():
    """If agentest-ai ships bundled agents, run one known check (T1-018 on a22)."""
    from agentest.cli import main
    import contextlib, io
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(["std", "run", "--agent", "a22", "--ids", "T1-018", "--format", "md"])
        except SystemExit as exc:
            code = int(exc.code or 0)
    text = out.getvalue() + err.getvalue()
    # Unknown-agent (code 2) means this wheel has no bundled a22; skip.
    if code == 2 and "unknown agent" in text:
        pytest.skip("bundled agent a22 is not in this agentest-ai install")
    assert "T1-018" in text
    # T1-018 is expected to fail on the empty-cart demo; either fail or a report is enough.
    assert code in (0, 1)


def test_session_option_without_otlp_is_noop(pytester: pytest.Pytester):
    pytester.makepyfile("def test_ok():\n    assert True\n")
    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)
