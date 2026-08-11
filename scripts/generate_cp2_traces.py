from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from structlog.contextvars import bind_contextvars, clear_contextvars


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CP2 Langfuse traces for a prompt label")
    parser.add_argument("--label", choices=("baseline", "candidate", "production"), required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    os.environ["LANGFUSE_PROMPT_LABEL"] = args.label

    # Import after loading .env and selecting the prompt label so the SDK and
    # @observe decorators are initialized with the intended configuration.
    from app.agent import LabAgent
    from app.tracing import get_langfuse_client, tracing_enabled

    if not tracing_enabled():
        print("Langfuse tracing is not configured")
        return 1

    queries = [
        json.loads(line)
        for line in (REPO_ROOT / "data" / "sample_queries.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][: args.limit]
    agent = LabAgent()
    for query in queries:
        clear_contextvars()
        correlation_id = f"req-{uuid.uuid4().hex[:8]}"
        bind_contextvars(correlation_id=correlation_id)
        agent.run(
            user_id=query["user_id"],
            feature=query["feature"],
            session_id=query["session_id"],
            message=query["message"],
        )
        print(f"{args.label}: {correlation_id}")

    get_langfuse_client().flush()
    print(f"Flushed {len(queries)} trace(s) for label '{args.label}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
