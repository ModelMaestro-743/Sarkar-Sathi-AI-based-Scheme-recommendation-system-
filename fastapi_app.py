import os

from fastapi import BackgroundTasks, FastAPI, Form
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Update this import to match where your workflow function lives.
from main import (
    detect_language,
    get_top_schemes,
    translate_from_english,
    translate_to_english,
)


app = FastAPI()
user_sessions = {}
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_MAX_BODY_LEN = 1600

QUESTION_FLOW = [
    (
        "name",
        "Hi! I am your Government Schemes Assistant. I will ask a few simple questions and then suggest the most relevant schemes for you. To get started, what is your name?",
    ),
    ("state", "Which state do you live in?"),
    ("area_type", "Is your area Urban or Rural?"),
    ("employment", "What is your employment type? (Student/Unemployed/Self-employed/Private/Government)"),
    ("income", "What is your monthly income?"),
    ("education", "What is your highest education level?"),
    ("interest_sector", "Which sector are you interested in?"),
    ("user_query", "Great. What would you like help with?"),
]


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {
        "message": "Gov Scheme API is running",
        "endpoints": {
            "process_query": "POST /process_query",
            "docs": "/docs",
        },
    }


@app.get("/favicon.ico")
def favicon():
    return JSONResponse(status_code=204, content=None)


@app.post("/process_query")
def process_query(payload: QueryRequest):
    try:
        language = detect_language(payload.query)
        english_query = translate_to_english(payload.query, language)
        result = get_top_schemes(english_query)
        return result
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


def _twiml_message(text: str) -> Response:
    response = MessagingResponse()
    response.message(text)
    twiml = str(response)
    print(f"[webhook] outgoing_reply={text}")
    print(f"[webhook] outgoing_twiml={twiml}")
    return Response(content=twiml, media_type="text/xml")


def _format_whatsapp_response(result: dict) -> str:
    summary = str(result.get("user_profile_summary", "")).strip()
    schemes = result.get("recommended_schemes", [])

    lines = []
    lines.append("Here are your detailed scheme recommendations:")

    if summary:
        lines.append("")
        lines.append("User profile summary:")
        lines.append(summary)

    if not schemes:
        lines.append("")
        lines.append("No schemes found for the provided details.")
        return "\n".join(lines).strip()

    lines.append("")
    lines.append("Recommended schemes:")

    for idx, scheme in enumerate(schemes, start=1):
        rank = scheme.get("rank", idx)
        scheme_name = scheme.get("scheme_name", "N/A")
        relevance_reason = scheme.get("relevance_reason", "N/A")
        benefits = scheme.get("benefits", "N/A")
        eligibility_summary = scheme.get("eligibility_summary", "N/A")
        application_process = scheme.get("application_process", "N/A")
        required_documents = scheme.get("required_documents", "N/A")
        level = scheme.get("level", "N/A")
        category = scheme.get("category", "N/A")

        lines.append("")
        lines.append(f"Scheme {rank}: {scheme_name}")
        lines.append(f"Category: {category}")
        lines.append(f"Level: {level}")
        lines.append(f"Why recommended: {relevance_reason}")
        lines.append(f"Benefits: {benefits}")
        lines.append(f"Eligibility: {eligibility_summary}")
        lines.append(f"Application process: {application_process}")
        lines.append(f"Required documents: {required_documents}")

    return "\n".join(lines).strip()


def _split_for_twilio(body: str, limit: int = TWILIO_MAX_BODY_LEN):
    text = (body or "").strip()
    if not text:
        return [""]
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""

    for line in text.splitlines():
        candidate = f"{current}\n{line}".strip() if current else line
        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        while len(line) > limit:
            chunks.append(line[:limit])
            line = line[limit:]
        current = line

    if current:
        chunks.append(current)

    total = len(chunks)
    if total == 1:
        return chunks

    numbered = []
    for i, part in enumerate(chunks, start=1):
        prefix = f"({i}/{total}) "
        allowed = limit - len(prefix)
        numbered.append(prefix + part[:allowed])
    return numbered


def send_whatsapp_reply(to: str, body: str):
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment variables.")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for chunk in _split_for_twilio(body):
        client.messages.create(from_=TWILIO_WHATSAPP_FROM, to=to, body=chunk)


def process_and_reply(phone: str, data: dict):
    try:
        user_input_text = data.get("user_query", "")
        user_language = detect_language(user_input_text)

        combined_query = (
            f"I am a {data.get('employment', '')} from {data.get('state', '')} ({data.get('area_type', '')}), "
            f"with income {data.get('income', '')}, education {data.get('education', '')}, "
            f"interested in {data.get('interest_sector', '')}. "
            f"Query: {data.get('user_query', '')}"
        )
        english_query = translate_to_english(combined_query, user_language)
        result = get_top_schemes(english_query)
        reply_in_english = _format_whatsapp_response(result)
        localized_reply = translate_from_english(reply_in_english, user_language)
        send_whatsapp_reply(phone, localized_reply)
        send_whatsapp_reply(
            phone,
            "Would you like to search for more schemes? Reply 'more' for a new query, 'update field: value' to edit details, 'yes' to restart full form, or 'stop' to pause.",
        )
        print(f"[webhook-bg] reply_sent to={phone}")
    except Exception as exc:
        print(f"[webhook-bg] error={exc}")
        try:
            send_whatsapp_reply(phone, "Sorry, something went wrong while fetching your schemes.")
        except Exception as send_exc:
            print(f"[webhook-bg] send_error={send_exc}")


@app.post("/webhook")
async def webhook(background_tasks: BackgroundTasks, Body: str = Form(...), From: str = Form(...)):
    try:
        phone = str(From).strip()
        message = str(Body).strip()
        print(f"[webhook] incoming message from={phone} body={message}")

        if not phone:
            return _twiml_message("Missing sender phone number.")

        session = user_sessions.get(phone)
        print(f"[webhook] session_before={session}")

        if session is None:
            user_sessions[phone] = {
                "step": 0,
                "data": {},
                "completed": False,
                "paused": False,
                "awaiting_more_query": False,
            }
            print(f"[webhook] session_after={user_sessions[phone]}")
            return _twiml_message(QUESTION_FLOW[0][1])

        normalized = message.lower()

        if normalized == "stop":
            session["paused"] = True
            print(f"[webhook] session_paused for={phone}")
            return _twiml_message("Paused. Reply 'resume' anytime to continue.")

        if session.get("paused"):
            if normalized == "resume":
                session["paused"] = False
                if session.get("completed"):
                    return _twiml_message(
                        "Welcome back. Reply 'more' for a new query, 'update field: value' to edit details, or 'yes' to restart full form."
                    )
                return _twiml_message("Welcome back. " + QUESTION_FLOW[session["step"]][1])
            return _twiml_message("Your session is paused. Reply 'resume' to continue.")

        if session.get("completed"):
            if normalized == "yes":
                user_sessions[phone] = {
                    "step": 0,
                    "data": {},
                    "completed": False,
                    "paused": False,
                    "awaiting_more_query": False,
                }
                print(f"[webhook] restarted session={user_sessions[phone]}")
                return _twiml_message("Great, let's start again. " + QUESTION_FLOW[0][1])

            if normalized == "more":
                session["awaiting_more_query"] = True
                return _twiml_message("Sure. Please send your new query.")

            if session.get("awaiting_more_query"):
                session["data"]["user_query"] = message
                session["awaiting_more_query"] = False
                data = session["data"].copy()
                background_tasks.add_task(process_and_reply, phone, data)
                print(f"[webhook] queued follow-up query for={phone}")
                return _twiml_message("Please wait, finding more schemes for your new query...")

            if normalized.startswith("update "):
                update_payload = message[7:].strip()
                if ":" not in update_payload:
                    return _twiml_message(
                        "Use this format: update field: value. Example: update income: 30000"
                    )
                field, value = update_payload.split(":", 1)
                field = field.strip().lower()
                value = value.strip()
                allowed_fields = {
                    "name",
                    "state",
                    "area_type",
                    "employment",
                    "income",
                    "education",
                    "interest_sector",
                    "user_query",
                }
                if field not in allowed_fields:
                    return _twiml_message(
                        "Allowed fields: name, state, area_type, employment, income, education, interest_sector, user_query."
                    )
                session["data"][field] = value
                return _twiml_message(
                    f"Updated {field}. Reply 'more' to send a new query, or update another field."
                )

            return _twiml_message(
                "Reply 'more' for a new query, 'update field: value' to edit details, 'yes' to restart full form, or 'stop' to pause."
            )

        step = session["step"]
        if step < len(QUESTION_FLOW):
            field_name, _ = QUESTION_FLOW[step]
            session["data"][field_name] = message
            session["step"] += 1
            print(f"[webhook] captured field={field_name} value={message}")
            print(f"[webhook] session_after={session}")

        if session["step"] < len(QUESTION_FLOW):
            return _twiml_message(QUESTION_FLOW[session["step"]][1])

        data = session["data"].copy()
        session["completed"] = True
        session["awaiting_more_query"] = False
        background_tasks.add_task(process_and_reply, phone, data)
        print("[webhook] background task queued and session marked completed")
        return _twiml_message("Please wait, finding the best schemes for you...")
    except Exception as exc:
        print(f"[webhook] error={exc}")
        return _twiml_message(f"Error: {exc}")
