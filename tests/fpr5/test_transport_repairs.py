"""FPR5-R1/R2 requirements through the real transport/CLI boundaries, offline."""
import io
import json
from email.message import Message
import socket
import sys
import urllib.request
import urllib.response

import pytest

from tests.fpr3.test_commands import git, settings
from tests.v1.conftest import command, seed
from tools.hosted_dashboard.http_client import UpstreamClient, UpstreamError


@pytest.mark.parametrize("method", ["GET", "HEAD"])
@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("target", [
    "https://not-allowlisted.invalid/stolen",
    "https://raw.githubusercontent.com/other/repo/main/file",
    "http://api.github.com/downgrade",
    "https://api.github.com:8443/another-port",
    "https://api.github.com/another-path",
    "/relative-path",
])
def test_hosted_default_transport_refuses_redirect_before_second_request(monkeypatch, method, status, target):
    calls = []

    class SyntheticHTTP(urllib.request.BaseHandler):
        handler_order = 100

        def https_open(self, request):
            calls.append((request.full_url, request.get_header("Authorization")))
            headers = Message()
            code = status if len(calls) == 1 else 200
            if len(calls) == 1:
                headers["Location"] = target
            response = urllib.response.addinfourl(io.BytesIO(b"{}"), headers, request.full_url, code)
            response.msg = "synthetic response"
            return response

        http_open = https_open

    def no_network(*args, **kwargs):
        raise AssertionError("a synthetic transport must never open a socket")

    monkeypatch.setattr(socket, "create_connection", no_network)
    build = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "_opener", build(SyntheticHTTP()))
    monkeypatch.setattr(urllib.request, "build_opener", lambda *handlers: build(SyntheticHTTP(), *handlers))
    # No injected UpstreamClient transport: the actual production urllib chain runs.
    response = UpstreamClient(token="FAKE-REPAIR-TOKEN").request(method, "https://api.github.com/repos/fixture/bound")
    assert calls == [("https://api.github.com/repos/fixture/bound", "Bearer FAKE-REPAIR-TOKEN")]
    assert response.status == status


def test_hosted_redirect_is_not_a_successful_json_response(monkeypatch):
    from tools.hosted_dashboard.http_client import UpstreamResponse
    client = UpstreamClient(token=None, transport=lambda *args: UpstreamResponse(302, {"location": "/elsewhere"}, b"{}"))
    with pytest.raises(UpstreamError) as error:
        client.get_json("https://api.github.com/repos/fixture/bound")
    assert error.value.status == 302


@pytest.fixture
def pr_fixture(tmp_path):
    root = seed(tmp_path / "bound")
    result = command("-C", root, "init")
    assert result.returncode == 0, result.stderr
    git(root, "remote", "add", "origin", "https://github.com/fixture/bound.git")
    log = tmp_path / "gh-calls.jsonl"
    response = tmp_path / "view.json"
    response.write_text(json.dumps({"number": 7, "state": "OPEN", "url": "https://github.com/fixture/bound/pull/7"}))
    fake = tmp_path / "fake-gh"
    fake.write_text(
        "#!" + sys.executable + "\n"
        "import json, os, pathlib, subprocess, sys\n"
        f"log = pathlib.Path({str(log)!r})\n"
        "with log.open('a') as stream: stream.write(json.dumps({'argv': sys.argv[1:], 'GH_REPO': os.environ.get('GH_REPO'), 'GH_HOST': os.environ.get('GH_HOST')}) + '\\n')\n"
        f"response = pathlib.Path({str(response)!r})\n"
        "if sys.argv[2] == 'view': print(response.read_text())\n"
        "elif sys.argv[2] == 'checks':\n"
        "    print('ci\\tpass\\t0s\\tfixture')\n"
        "    if os.environ.get('FPR5_DRIFT_REMOTE'):\n"
        "        subprocess.run(['/usr/bin/git', 'remote', 'set-url', 'origin', 'https://github.com/foreign/repo.git'], check=True)\n"
    )
    fake.chmod(0o755)

    def invoke(selector="7", *, authorization=True, dry_run=False, env=None):
        argv = ["-C", root, "pr-land", "--pr=" + selector, "--allow-network", "--gh", fake, "--json"]
        if authorization:
            argv += ["--authorized", "disposable fake transport only"]
        if dry_run:
            argv += ["--dry-run"]
        return command(*argv, env=env)

    def calls():
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    return root, response, invoke, calls


@pytest.mark.parametrize("selector", [
    "https://github.com/foreign/repo/pull/7", "https://foreign.invalid/fixture/bound/pull/7",
    "--repo=foreign/repo", "-Rforeign/repo", "--help", "",
    "https://github.com/fixture/bound/issues/7", "https://github.com/fixture/bound/pull/7?other=1",
    "https://github.com/fixture/bound/pull/7#other", "http://github.com/fixture/bound/pull/7",
    "https://user@github.com/fixture/bound/pull/7", "https://github.com:8443/fixture/bound/pull/7",
    "https://github.com/fixture/bound/pull/0", "feature branch", "feature\nbranch", "../other",
])
def test_pr_invalid_or_foreign_selector_refuses_before_transport(pr_fixture, selector):
    _, _, invoke, calls = pr_fixture
    result = invoke(selector)
    assert result.returncode != 0, result.stdout
    assert calls() == []


@pytest.mark.parametrize("state", [
    {"state": "OPEN"},
    {"number": 7, "state": "OPEN", "url": "https://github.com/foreign/repo/pull/7"},
    {"number": 7, "state": "OPEN", "url": "https://foreign.invalid/fixture/bound/pull/7"},
    {"number": 7, "state": "OPEN", "url": "http://github.com/fixture/bound/pull/7"},
    {"number": 7, "state": "OPEN", "url": "https://user@github.com/fixture/bound/pull/7"},
    {"number": 7, "state": "OPEN", "url": "https://github.com/fixture/bound/pull/7?wrong=1"},
    {"number": 8, "state": "OPEN", "url": "https://github.com/fixture/bound/pull/8"},
    {"number": 8, "state": "OPEN", "url": "https://github.com/fixture/bound/pull/7"},
    {"number": "7", "state": "OPEN", "url": "https://github.com/fixture/bound/pull/7"},
    [], None,
])
def test_pr_missing_foreign_or_drifted_resolution_never_checks_or_merges(pr_fixture, state):
    _, response, invoke, calls = pr_fixture
    response.write_text(json.dumps(state))
    result = invoke()
    assert result.returncode != 0, result.stdout
    assert [row["argv"][:2] for row in calls()] == [["pr", "view"]]


@pytest.mark.parametrize("selector", ["7", "https://github.com/fixture/bound/pull/7", "feature/topic",
                                      pytest.param("٧", id="unicode-digit-branch"),
                                      pytest.param("feature./topic", id="interior-dot-branch"),
                                      pytest.param("@", id="at-branch")])
def test_pr_matching_identity_pins_every_transport_and_ignores_ambient_target(pr_fixture, selector):
    root, _, invoke, calls = pr_fixture
    before = (root / "docs/NEXT.md").read_bytes()
    result = invoke(selector, env={"GH_REPO": "foreign/repo", "GH_HOST": "foreign.invalid"})
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["merged"] is True
    rows = calls()
    assert [row["argv"][:2] for row in rows] == [["pr", "view"], ["pr", "checks"], ["pr", "merge"]]
    for row in rows:
        assert row["GH_REPO"] == "github.com/fixture/bound"
        assert row["GH_HOST"] == "github.com"
        assert row["argv"][-2:] == ["--repo", "github.com/fixture/bound"]
    assert rows[1]["argv"][2] == rows[2]["argv"][2] == "7"
    assert (root / "docs/NEXT.md").read_bytes() == before


def test_pr_configured_remote_drift_prevents_merge(pr_fixture):
    _, _, invoke, calls = pr_fixture
    result = invoke(env={"FPR5_DRIFT_REMOTE": "1"})
    assert result.returncode != 0, result.stdout
    assert all(row["argv"][:2] != ["pr", "merge"] for row in calls())


def test_pr_authorization_still_required_before_transport(pr_fixture):
    _, _, invoke, calls = pr_fixture
    result = invoke(authorization=False)
    assert result.returncode != 0
    assert calls() == []


def test_pr_dry_run_never_merges_or_performs_configured_sync(pr_fixture):
    root, _, invoke, calls = pr_fixture
    settings(root, close_ritual={"post_land_sync": {"enabled": True}})
    result = invoke(dry_run=True)
    assert result.returncode == 0, result.stdout + result.stderr
    value = json.loads(result.stdout)
    assert value["merged"] is False
    assert value["post_land_sync"]["status"] == "requires_explicit_post_land_sync"
    assert [row["argv"][:2] for row in calls()] == [["pr", "view"], ["pr", "checks"]]
