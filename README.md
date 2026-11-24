# pytest-agentest

A pytest plugin for AiEnsured agentest, an Agentic AI Testing platform.

It runs agentest's 165 tests over an agent's recorded OpenTelemetry traces during a pytest session, so you can gate CI on what the agent actually did, not only what it said.

## Install

```
pip install agentest-ai
```

```
pip install pytest-agentest
```

`pytest-agentest` 0.1.0 is published to PyPI on the first GitHub Release, after trusted publishing is connected. Until that release is live, install the plugin from this repository:

```
pip install git+https://github.com/srpadmanabhuni/pytest-agentest.git
```

Once it is on PyPI, the automated pytest plugin list at https://docs.pytest.org/en/stable/reference/plugin_list.html will pick it up from the `pytest-` package name. There is no separate submit form.

## Usage

Call agentest from a test with the `agentest_run` fixture:

```python
def test_recorded_trace(agentest_run):
    result = agentest_run(otlp="traces/run.otlp.jsonl", ids="T1-018", fmt="md")
    assert result.returncode == 0
```

Or pass traces on the command line. With `--agentest-strict`, pytest fails if any check fails:

```
pytest --agentest-otlp traces/run.otlp.jsonl --agentest-ids T1-018 --agentest-strict
```

## Options

- `--agentest-otlp PATH` — OTLP trace file (repeatable)
- `--agentest-ids IDS` — limit to test IDs or classes, comma-separated (for example `T1-018`)
- `--agentest-strict` — fail the pytest session if any agentest check fails

## Links

- PyPI (agentest): https://pypi.org/project/agentest-ai/
- PyPI (this plugin, after the first release): https://pypi.org/project/pytest-agentest/
- Plugin repo: https://github.com/srpadmanabhuni/pytest-agentest
- agentest repo: https://github.com/srpadmanabhuni/agentest
- Docs: https://srpadmanabhuni.github.io/agentest/

Try it on your own agent and tell us what it caught or missed.
