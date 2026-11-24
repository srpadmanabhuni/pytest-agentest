"""pytest11 plugin: fixtures and CLI options to run AiEnsured agentest."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Callable

import pytest

from agentest.cli import main as agentest_main


@dataclass
class AgentestRunResult:
    """Outcome of one `agentest std run` invocation."""

    returncode: int
    stdout: str
    stderr: str
    argv: list[str]


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("agentest", "AiEnsured agentest")
    group.addoption(
        "--agentest-otlp",
        action="append",
        default=[],
        dest="agentest_otlp",
        metavar="PATH",
        help="OTLP trace file to judge with agentest (repeatable).",
    )
    group.addoption(
        "--agentest-ids",
        action="store",
        default="",
        dest="agentest_ids",
        metavar="IDS",
        help="Limit to test IDs or classes, comma-separated (for example T1-018).",
    )
    group.addoption(
        "--agentest-strict",
        action="store_true",
        default=False,
        dest="agentest_strict",
        help="Fail the pytest session if any agentest check fails.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "agentest: tests that run AiEnsured agentest on recorded traces",
    )


def run_agentest(
    *,
    otlp: str | list[str] | None = None,
    ids: str | None = None,
    fmt: str = "md",
    extra: list[str] | None = None,
) -> AgentestRunResult:
    """Invoke `agentest std run` in-process and capture stdout/stderr."""
    argv = ["std", "run", "--format", fmt]
    paths = otlp if isinstance(otlp, list) else ([otlp] if otlp else [])
    for path in paths:
        argv.extend(["--otlp", str(path)])
    if ids:
        argv.extend(["--ids", ids])
    if extra:
        argv.extend(extra)

    import contextlib
    import sys

    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = agentest_main(argv)
        except SystemExit as exc:
            code = int(exc.code or 0)
    return AgentestRunResult(
        returncode=int(code or 0),
        stdout=out.getvalue(),
        stderr=err.getvalue(),
        argv=argv,
    )


@pytest.fixture
def agentest_run() -> Callable[..., AgentestRunResult]:
    """Run `agentest std run` from a test. See `run_agentest` for arguments."""
    return run_agentest


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    otlp = list(session.config.getoption("agentest_otlp") or [])
    if not otlp:
        return
    ids = session.config.getoption("agentest_ids") or None
    strict = bool(session.config.getoption("agentest_strict"))
    result = run_agentest(otlp=otlp, ids=ids, fmt="md")
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        reporter.write_line("agentest std run: " + " ".join(result.argv[1:]))
        if result.stdout:
            reporter.write(result.stdout)
        if result.stderr:
            reporter.write(result.stderr)
        reporter.write_line(f"agentest exit code: {result.returncode}")
    if strict and result.returncode != 0:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        # pytest may have already finalized exitstatus; also raise via session
        if exitstatus == 0:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


# silence unused-import look; import pytest already used
