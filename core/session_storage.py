from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


_SESSIONS: dict[str, dict] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def store_turn(
    session_id: str,
    message: dict,
    metadata: dict,
    conversation_history: list | None = None,
) -> dict:
    """Persist/update session state and append a turn record."""
    session_state = _SESSIONS.setdefault(
        session_id,
        {
            "sessionId": session_id,
            "channel": metadata["channel"],
            "language": metadata["language"],
            "locale": metadata["locale"],
            "createdAt": _utc_now_iso(),
            "updatedAt": _utc_now_iso(),
            "turns": [],
        },
    )

    session_state["channel"] = metadata["channel"]
    session_state["language"] = metadata["language"]
    session_state["locale"] = metadata["locale"]
    session_state["updatedAt"] = _utc_now_iso()

    turn_record = {
        "timestamp": _utc_now_iso(),
        "message": deepcopy(message),
        "metadata": {
            "channel": metadata["channel"],
            "language": metadata["language"],
            "locale": metadata["locale"],
        },
        "conversationHistory": deepcopy(conversation_history or []),
    }
    session_state["turns"].append(turn_record)

    return deepcopy(session_state)


def get_session_state(session_id: str) -> dict | None:
    state = _SESSIONS.get(session_id)
    if state is None:
        return None
    return deepcopy(state)