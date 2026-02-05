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
            "finalCallback": {
                "sent": False,
                "sentAt": None,
                "idempotencyKey": None,
                "lastAttemptAt": None,
                "lastStatus": None,
            },
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


def get_callback_status(session_id: str) -> dict:
    session_state = _SESSIONS.setdefault(
        session_id,
        {
            "sessionId": session_id,
            "channel": "",
            "language": "",
            "locale": "",
            "createdAt": _utc_now_iso(),
            "updatedAt": _utc_now_iso(),
            "turns": [],
            "finalCallback": {
                "sent": False,
                "sentAt": None,
                "idempotencyKey": None,
                "lastAttemptAt": None,
                "lastStatus": None,
            },
        },
    )
    callback = session_state.setdefault(
        "finalCallback",
        {
            "sent": False,
            "sentAt": None,
            "idempotencyKey": None,
            "lastAttemptAt": None,
            "lastStatus": None,
        },
    )
    return deepcopy(callback)


def update_callback_status(session_id: str, **kwargs) -> dict:
    session_state = _SESSIONS.setdefault(
        session_id,
        {
            "sessionId": session_id,
            "channel": "",
            "language": "",
            "locale": "",
            "createdAt": _utc_now_iso(),
            "updatedAt": _utc_now_iso(),
            "turns": [],
            "finalCallback": {
                "sent": False,
                "sentAt": None,
                "idempotencyKey": None,
                "lastAttemptAt": None,
                "lastStatus": None,
            },
        },
    )
    callback = session_state.setdefault(
        "finalCallback",
        {
            "sent": False,
            "sentAt": None,
            "idempotencyKey": None,
            "lastAttemptAt": None,
            "lastStatus": None,
        },
    )

    callback.update(kwargs)
    session_state["updatedAt"] = _utc_now_iso()
    return deepcopy(callback)


def get_session_state(session_id: str) -> dict | None:
    state = _SESSIONS.get(session_id)
    if state is None:
        return None
    return deepcopy(state)
