# core/pipeline.py
from __future__ import annotations
from core.conversation_store import append_message, get_full_history, replace_session
from rules.rule_engine import check as rule_check
from ml.classifier import predict as ml_predict
from core.decision import decide
from schemas.response_schema import base_response
from core.info_extractor import extract_entities
from language.english import normalize as en_norm
from language.hindi import normalize as hi_norm
from language.tamil import normalize as ta_norm
from core.session_storage import store_turn

VALID_SENDERS = {"scammer", "user"}


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

def _merge_conversation_history(conversation_history: list) -> str:
    messages = []
    for item in conversation_history or []:
        if isinstance(item, dict):
            message_text = item.get("text")
            if isinstance(message_text, str) and message_text.strip():
                messages.append(message_text)
        elif isinstance(item, str) and item.strip():
            messages.append(item)
    return "\n".join(messages)

def process_message(payload: dict):
    text = payload["message"]["text"]
    metadata = _validate_and_extract_metadata(payload)
    language = metadata["language"]

    if language.lower().startswith("hi"):
        normalized = hi_norm(text)
        lang_code = "hi"
    elif language.lower().startswith("ta"):
        normalized = ta_norm(text)
        lang_code = "ta"
    else:
        normalized = en_norm(text)
        lang_code = "en"

    rule_result = rule_check(normalized)

    ml_result = None
    if rule_result["status"] == "PASS_TO_ML":
        ml_result = ml_predict(normalized, lang_code)

    decision = decide(rule_result, ml_result)

    response = base_response()
    response["sessionId"] = payload["sessionId"]
    response["is_scam"] = decision["is_scam"]
    response["decision_source"] = decision["decision_source"]
    response["confidence_score"] = decision["confidence"]
    response["category"] = decision["category"]

    response["language"] = language
    response["channel"] = metadata["channel"]
    response["locale"] = metadata["locale"]

    stored_session_state = store_turn(
        session_id=payload["sessionId"],
        message=payload.get("message", {}),
        metadata=metadata,
        conversation_history=payload.get("conversationHistory", []),
    )
    response["session_context"] = {
        "channel": stored_session_state["channel"],
        "language": stored_session_state["language"],
        "locale": stored_session_state["locale"],
    }
    
    merged_history_text = _merge_conversation_history(payload.get("conversationHistory", []))
    response["extracted_entities"] = extract_entities(text, merged_history_text)

    return response
