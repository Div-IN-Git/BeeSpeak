# core/pipeline.py
from __future__ import annotations
from rules.rule_engine import check as rule_check
from ml.classifier import predict as ml_predict
from core.decision import decide
from schemas.response_schema import base_response
from core.info_extractor import extract_entities
from language.english import normalize as en_norm
from language.hindi import normalize as hi_norm
from language.tamil import normalize as ta_norm

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
    language = payload.get("metadata", {}).get("language", "English")

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

    if decision["keywords"]:
        response["reasons"] = {
            "matched_keywords": decision["keywords"]
        }
    else:
        response["reasons"] = []

    response["language"] = language
    
    merged_history_text = _merge_conversation_history(payload.get("conversationHistory", []))
    response["extracted_entities"] = extract_entities(text, merged_history_text)

    return response
