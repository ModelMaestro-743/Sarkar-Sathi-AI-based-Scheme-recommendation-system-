from fastapi import APIRouter, BackgroundTasks, Form
from fastapi.responses import JSONResponse

from app.constants.conversation import (
    COMMAND_ALIASES,
    LANGUAGE_TO_TRANSLATOR,
    QUESTION_FLOW,
    QUESTION_TEXT,
    UI_TEXT,
)
from app.core.session import user_sessions
from app.models.schemas import QueryRequest
from app.services.rag import get_top_schemes, get_top_schemes_with_profile
from app.services.translation import detect_language, translate_from_english, translate_to_english
from app.services.whatsapp import format_scheme_messages, send_whatsapp_reply, twiml_response

router = APIRouter()

_ALLOWED_UPDATE_FIELDS = {
    "preferred_language", "name", "state", "area_type",
    "employment", "income", "education", "interest_sector", "user_query",
}


# ---------------------------------------------------------------------------
# Session / conversation helpers
# ---------------------------------------------------------------------------

def _session_language(session: dict | None) -> str:
    if not session:
        return "en"
    lang = session.get("preferred_language") or session.get("data", {}).get("preferred_language")
    return lang if lang in LANGUAGE_TO_TRANSLATOR else "en"


def _ui(session: dict | None, key: str, **kwargs) -> str:
    lang = _session_language(session)
    template = UI_TEXT.get(lang, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, ""))
    return template.format(**kwargs)


def _question(step: int, session: dict | None = None) -> str:
    field = QUESTION_FLOW[step]
    lang = "en" if field == "preferred_language" else _session_language(session)
    return QUESTION_TEXT[field].get(lang, QUESTION_TEXT[field]["en"])


def _parse_language(value: str) -> str | None:
    normalized = str(value or "").strip().lower()
    language_map = {
        "1": "en", "english": "en", "en": "en", "अंग्रेजी": "en", "इंग्लिश": "en",
        "2": "hi", "hindi": "hi", "hi": "hi", "हिंदी": "hi", "हिन्दी": "hi",
        "3": "mr", "marathi": "mr", "mr": "mr", "मराठी": "mr",
    }
    return language_map.get(normalized) or language_map.get(normalized.replace(" ", ""))


def _parse_command(message: str) -> tuple[str | None, str]:
    normalized = " ".join(str(message or "").strip().lower().split())
    if not normalized:
        return None, ""
    parts = normalized.split(maxsplit=1)
    keyword, payload = parts[0], (parts[1] if len(parts) > 1 else "")
    for canonical, aliases in COMMAND_ALIASES.items():
        if keyword in aliases:
            return canonical, payload
    return None, normalized


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------

def process_and_reply(phone: str, data: dict):
    try:
        preferred_language = data.get("preferred_language", "en")
        if preferred_language not in LANGUAGE_TO_TRANSLATOR:
            preferred_language = "en"
        user_language = LANGUAGE_TO_TRANSLATOR[preferred_language]

        english_query = translate_to_english(data.get("user_query", ""), user_language)
        profile = {
            "preferred_language": user_language,
            "name": data.get("name", ""),
            "state": data.get("state", ""),
            "area_type": data.get("area_type", ""),
            "employment": data.get("employment", ""),
            "income": data.get("income", ""),
            "education": data.get("education", ""),
            "interest_sector": data.get("interest_sector", ""),
            "user_query": english_query,
        }
        result = get_top_schemes_with_profile(profile)
        messages_en = format_scheme_messages(result)

        session = user_sessions.get(phone, {})
        session.update({
            "completed": True,
            "paused": False,
            "awaiting_more_query": False,
            "preferred_language": preferred_language,
        })
        user_sessions[phone] = session

        for msg in messages_en:
            send_whatsapp_reply(phone, translate_from_english(msg, user_language))
        send_whatsapp_reply(phone, _ui(session, "completed_help"))
        print(f"[bg] sent {len(messages_en)} message(s) to {phone}")

    except Exception as exc:
        print(f"[bg] error={exc}")
        session = user_sessions.get(phone, {})
        session.update({"completed": True, "paused": False, "awaiting_more_query": False})
        if "preferred_language" not in session and data.get("preferred_language") in LANGUAGE_TO_TRANSLATOR:
            session["preferred_language"] = data["preferred_language"]
        user_sessions[phone] = session
        try:
            send_whatsapp_reply(phone, _ui(session, "fetch_error"))
        except Exception as send_exc:
            print(f"[bg] error reply failed: {send_exc}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
def root():
    return {
        "message": "Sarkar Sathi API is running",
        "endpoints": {"process_query": "POST /process_query", "docs": "/docs"},
    }


@router.get("/favicon.ico")
def favicon():
    return JSONResponse(status_code=204, content=None)


@router.post("/process_query")
def process_query(payload: QueryRequest):
    try:
        language = detect_language(payload.query)
        english_query = translate_to_english(payload.query, language)
        return get_top_schemes(english_query)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.post("/webhook")
async def webhook(background_tasks: BackgroundTasks, Body: str = Form(...), From: str = Form(...)):
    try:
        phone = str(From).strip()
        message = str(Body).strip()
        print(f"[webhook] from={phone} body={message}")

        if not phone:
            return twiml_response(_ui(None, "missing_phone"))

        session = user_sessions.get(phone)
        if session:
            session.pop("pending_reply", None)

        # New user — start conversation
        if session is None:
            user_sessions[phone] = {
                "step": 0, "data": {}, "completed": False,
                "paused": False, "awaiting_more_query": False,
            }
            return twiml_response(_question(0))

        command, command_payload = _parse_command(message)

        # Stop command — works at any point
        if command == "stop":
            session["paused"] = True
            return twiml_response(_ui(session, "paused"))

        # Paused state
        if session.get("paused"):
            if command == "resume":
                session["paused"] = False
                if session.get("completed"):
                    return twiml_response(_ui(session, "welcome_back_completed"))
                return twiml_response(_ui(session, "welcome_back_active", question=_question(session["step"], session)))
            return twiml_response(_ui(session, "paused_wait"))

        # Completed state — handle follow-up commands
        if session.get("completed"):
            if command == "yes":
                user_sessions[phone] = {
                    "step": 0, "data": {}, "completed": False,
                    "paused": False, "awaiting_more_query": False,
                }
                return twiml_response(_ui(user_sessions[phone], "restart_start", question=_question(0)))

            if command == "more":
                session["awaiting_more_query"] = True
                return twiml_response(_ui(session, "ask_new_query"))

            if session.get("awaiting_more_query"):
                session["data"]["user_query"] = message
                session["awaiting_more_query"] = False
                background_tasks.add_task(process_and_reply, phone, session["data"].copy())
                return twiml_response(_ui(session, "wait_more"))

            if command == "update":
                if ":" not in command_payload:
                    return twiml_response(_ui(session, "update_format_error"))
                field, value = command_payload.split(":", 1)
                field, value = field.strip().lower(), value.strip()
                if field not in _ALLOWED_UPDATE_FIELDS:
                    return twiml_response(_ui(session, "allowed_fields"))
                if field == "preferred_language":
                    parsed = _parse_language(value)
                    if not parsed:
                        return twiml_response(_ui(session, "invalid_language"))
                    session["preferred_language"] = parsed
                    session["data"][field] = parsed
                else:
                    session["data"][field] = value
                return twiml_response(_ui(session, "updated_field", field=field))

            return twiml_response(_ui(session, "completed_help"))

        # Active Q&A — collect next answer
        step = session["step"]
        if step < len(QUESTION_FLOW):
            field_name = QUESTION_FLOW[step]
            if field_name == "preferred_language":
                parsed = _parse_language(message)
                if not parsed:
                    return twiml_response(_ui(None, "invalid_language"))
                session["preferred_language"] = parsed
                session["data"][field_name] = parsed
            else:
                session["data"][field_name] = message
            session["step"] += 1
            print(f"[webhook] captured field={field_name}")

        if session["step"] < len(QUESTION_FLOW):
            return twiml_response(_question(session["step"], session))

        # All questions answered — kick off background search
        data = session["data"].copy()
        session["completed"] = True
        session["awaiting_more_query"] = False
        background_tasks.add_task(process_and_reply, phone, data)
        return twiml_response(_ui(session, "wait_best"))

    except Exception as exc:
        print(f"[webhook] error={exc}")
        return twiml_response(f"Error: {exc}")
