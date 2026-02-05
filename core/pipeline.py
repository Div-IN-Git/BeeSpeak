# core/pipeline.py
from __future__ import annotations

from core.conversation_store import get_full_history, replace_session
from rules.rule_engine import check as rule_check
from ml.classifier import predict as ml_predict
from core.decision import decide
from schemas.response_schema import base_response
from core.info_extractor import extract_entities
from language.normalize import normalize_text
from core.session_storage import store_turn
from core.final_callback import send_final_callback_if_needed

VALID_SENDERS = {"scammer", "user"}


def _validate_payload(payload: dict):
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    if not isinstance(payload.get("sessionId"), str) or not payload["sessionId"].strip():
        raise ValueError("sessionId must be a non-empty string")

    message = payload.get("message")
    _validate_message(message)

    conversation_history = payload.get("conversationHistory")
    if conversation_history is None:
        conversation_history = []
    if not isinstance(conversation_history, list):
        raise ValueError("conversationHistory must be an array")

    for entry in conversation_history:
        _validate_message(entry)


def _validate_message(message):
    if not isinstance(message, dict):
        raise ValueError("message must be an object")

    sender = message.get("sender")
    text = message.get("text")
    timestamp = message.get("timestamp")

    if sender not in VALID_SENDERS:
        raise ValueError("message.sender must be 'scammer' or 'user'")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("message.text must be a non-empty string")
    if not isinstance(timestamp, int):
        raise ValueError("message.timestamp must be an integer")


def _message_key(message):
    return (
        message.get("timestamp"),
        str(message.get("text", "")).strip(),
        str(message.get("sender", "")).strip().lower(),
    )


def _merge_history(stored_history, request_history):
    merged = []
    seen = set()

    for msg in (stored_history or []) + (request_history or []):
        if not isinstance(msg, dict):
            continue

        required = {
            "sender": msg.get("sender"),
            "text": msg.get("text"),
            "timestamp": msg.get("timestamp"),
        }
        try:
            _validate_message(required)
        except ValueError:
            continue

        key = _message_key(required)
        if key in seen:
            continue

        seen.add(key)
        merged.append(required)

    merged.sort(key=lambda item: item["timestamp"])
    return merged


def _build_context_text(full_history):
    return "\n".join(
        f"{entry['sender']}: {entry['text']}" for entry in full_history if entry.get("text")
    )


def _validate_and_extract_metadata(payload: dict) -> dict:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")

    validated: dict[str, str] = {}
    for field_name in ("channel", "language", "locale"):
        value = metadata.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"metadata.{field_name} must be a non-empty string")

        # Preserve exact platform values as provided by the client (e.g. 'WhatsApp').
        validated[field_name] = value

    return validated




def _prepare_rule_text(raw_text: str) -> str:
    if not isinstance(raw_text, str):
        return ""
    return raw_text.strip().lower()


def _prepare_ml_text(raw_text: str) -> str:
    return normalize_text(raw_text)

def _build_agent_note(decision: dict, entities: dict) -> str:
    notes = []
    if decision.get("is_scam"):
        notes.append("Scam intent detected")

    if entities.get("upi_ids"):
        notes.append("UPI ID captured")
    if entities.get("phone_numbers"):
        notes.append("Phone number extracted")
    if entities.get("phishing_links"):
        notes.append("Phishing link observed")
    if entities.get("suspicious_keywords"):
        notes.append("Suspicious language present")

    return "; ".join(notes)


def process_message(payload: dict):
    _validate_payload(payload)

    session_id = payload["sessionId"]
    message = payload["message"]
    text = message["text"]
    metadata = _validate_and_extract_metadata(payload)
    language = metadata["language"]

    stored_history = get_full_history(session_id)
    request_history = payload.get("conversationHistory", [])
    merged_history = _merge_history(stored_history, request_history)

    # Pipeline order:
    # 1) Rule engine on raw incoming message (fast path)
    # 2) If unclear, normalize to English
    # 3) Run English model
    rule_text = _prepare_rule_text(text)
    rule_result = rule_check(rule_text)

    ml_result = None
    if rule_result["status"] == "PASS_TO_ML":
        ml_text = _prepare_ml_text(text)
        ml_result = ml_predict(ml_text, "en")

    decision = decide(rule_result, ml_result)

    context_text = _build_context_text(merged_history)
    entities = extract_entities(text, context_text)
    agent_note = _build_agent_note(decision, entities)

    updated_history = _merge_history(merged_history, [message])
    replace_session(session_id, updated_history)

    stored_session_state = store_turn(
        session_id=session_id,
        message=message,
        metadata=metadata,
        conversation_history=updated_history,
    )

    response = base_response()
    response["sessionId"] = session_id
    response["is_scam"] = decision["is_scam"]
    response["decision_source"] = decision["decision_source"]
    response["confidence_score"] = decision["confidence"]
    response["category"] = decision["category"]

    response["language"] = language
    response["channel"] = metadata["channel"]
    response["locale"] = metadata["locale"]

    response["session_context"] = {
        "channel": stored_session_state["channel"],
        "language": stored_session_state["language"],
        "locale": stored_session_state["locale"],
    }
    response["agent_notes"] = agent_note
    response["extracted_entities"] = entities

    send_final_callback_if_needed(
        session_id=session_id,
        is_scam=decision["is_scam"],
        extracted_entities=entities,
        agent_notes=agent_note,
        total_messages_exchanged=len(updated_history),
    )

    return response
