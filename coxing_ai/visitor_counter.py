"""No-database visitor counter utilities for CoxingCoachAI.

Production mode stores the cumulative count in ``data/visitor_count.json`` on a
separate GitHub branch (``usage-data`` by default). This avoids a traditional
database and also avoids triggering a Streamlit redeploy on every visit when the
app itself is deployed from ``main``.

A fine-grained GitHub token with repository Contents read/write permission is
required for that persistent mode. Without a token, the app falls back to a local
JSON file. The local fallback survives ordinary Streamlit reruns, but an ephemeral
cloud container can be recreated, so only the GitHub-backed mode is intended for
a never-reset cumulative total.
"""

from __future__ import annotations

import base64
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request

_LOCAL_LOCK = threading.Lock()


@dataclass(frozen=True)
class CounterConfig:
    repo: str = "qxiao2ub/coxing-ai-coach-app"
    path: str = "data/visitor_count.json"
    branch: str = "usage-data"
    source_branch: str = "main"
    token: str | None = None


@dataclass(frozen=True)
class CounterResult:
    count: int
    backend: str
    persistent: bool


def _safe_count(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _github_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "CoxingCoachAI-VisitorCounter",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _api_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 8,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = _github_headers(token)
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def _branch_ref_url(repo: str, branch: str) -> str:
    encoded_branch = parse.quote(branch, safe="")
    return f"https://api.github.com/repos/{repo}/git/ref/heads/{encoded_branch}"


def _ensure_counter_branch(config: CounterConfig) -> None:
    """Create the data-only branch from source_branch if it does not yet exist."""
    try:
        _api_json(_branch_ref_url(config.repo, config.branch), token=config.token)
        return
    except error.HTTPError as exc:
        if exc.code != 404:
            raise

    source = _api_json(
        _branch_ref_url(config.repo, config.source_branch),
        token=config.token,
    )
    sha = source.get("object", {}).get("sha")
    if not sha:
        raise RuntimeError(f"Unable to resolve source branch {config.source_branch!r}.")

    create_url = f"https://api.github.com/repos/{config.repo}/git/refs"
    try:
        _api_json(
            create_url,
            method="POST",
            token=config.token,
            payload={"ref": f"refs/heads/{config.branch}", "sha": sha},
        )
    except error.HTTPError as exc:
        # A simultaneous first visitor may have created the branch already.
        if exc.code not in {409, 422}:
            raise


def _github_content_url(config: CounterConfig) -> str:
    encoded_path = "/".join(parse.quote(part, safe="") for part in config.path.split("/"))
    return f"https://api.github.com/repos/{config.repo}/contents/{encoded_path}"


def _github_read(config: CounterConfig) -> tuple[int, str | None]:
    url = (
        f"{_github_content_url(config)}"
        f"?ref={parse.quote(config.branch, safe='')}"
    )
    try:
        payload = _api_json(url, token=config.token)
    except error.HTTPError as exc:
        if exc.code == 404:
            return 0, None
        raise

    encoded = str(payload.get("content", "")).replace("\n", "")
    decoded = base64.b64decode(encoded).decode("utf-8") if encoded else "{}"
    data = json.loads(decoded)
    return _safe_count(data.get("count")), payload.get("sha")


def _github_write(config: CounterConfig, new_count: int, sha: str | None) -> None:
    content = json.dumps({"count": int(new_count)}, indent=2) + "\n"
    body: dict[str, Any] = {
        "message": f"chore: update visitor count to {new_count}",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": config.branch,
    }
    if sha:
        body["sha"] = sha
    _api_json(
        _github_content_url(config),
        method="PUT",
        token=config.token,
        payload=body,
    )


def increment_github_counter(config: CounterConfig, retries: int = 5) -> CounterResult:
    """Increment the repository-backed counter with conflict retries."""
    if not config.token:
        raise RuntimeError("GitHub counter token is not configured.")

    _ensure_counter_branch(config)
    last_error: Exception | None = None

    for attempt in range(max(1, retries)):
        try:
            current, sha = _github_read(config)
            updated = current + 1
            _github_write(config, updated, sha)
            return CounterResult(updated, "github-branch", True)
        except error.HTTPError as exc:
            last_error = exc
            if exc.code in {409, 422} and attempt + 1 < retries:
                time.sleep(0.18 * (attempt + 1))
                continue
            raise
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(0.18 * (attempt + 1))
                continue
            raise

    raise RuntimeError("Unable to update GitHub visitor counter.") from last_error


def increment_local_counter(local_file: Path) -> CounterResult:
    """Best-effort local fallback for development and token-free deployments."""
    local_file.parent.mkdir(parents=True, exist_ok=True)
    with _LOCAL_LOCK:
        current = 0
        if local_file.exists():
            try:
                data = json.loads(local_file.read_text(encoding="utf-8"))
                current = _safe_count(data.get("count"))
            except Exception:
                current = 0
        updated = current + 1
        local_file.write_text(
            json.dumps({"count": updated}, indent=2) + "\n",
            encoding="utf-8",
        )
    return CounterResult(updated, "local-file", False)


def increment_visitor_counter(config: CounterConfig, local_file: Path) -> CounterResult:
    """Use GitHub persistence when configured, otherwise a local-file fallback."""
    if config.token:
        try:
            return increment_github_counter(config)
        except Exception:
            # Keep the app usable during a transient GitHub/API failure.
            return increment_local_counter(local_file)
    return increment_local_counter(local_file)
