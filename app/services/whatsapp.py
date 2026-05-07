from fastapi.responses import Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from app.core.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    TWILIO_MAX_BODY_LEN,
)


def _clean_text(value) -> str:
    return " ".join(str(value or "").split()).strip()


def twiml_response(text: str) -> Response:
    mr = MessagingResponse()
    mr.message(text)
    body = str(mr).encode("utf-8")
    print(f"[webhook] outgoing_reply={text}")
    return Response(
        content=body,
        media_type="application/xml; charset=utf-8",
        headers={"Content-Length": str(len(body))},
    )


def _split_for_twilio(body: str, limit: int = TWILIO_MAX_BODY_LEN) -> list[str]:
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
        numbered.append(prefix + part[: limit - len(prefix)])
    return numbered


def send_whatsapp_reply(to: str, body: str):
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set.")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for chunk in _split_for_twilio(body):
        msg = client.messages.create(from_=TWILIO_WHATSAPP_FROM, to=to, body=chunk)
        print(f"[twilio] to={to} sid={msg.sid} status={msg.status}")


def format_scheme_messages(result: dict, max_schemes: int = 3) -> list[str]:
    summary = _clean_text(result.get("user_profile_summary", ""))
    schemes = result.get("recommended_schemes", [])
    total = len(schemes)
    shown = min(max_schemes, total)

    messages: list[str] = []
    intro = ["Top relevant schemes for you:"]
    if summary:
        intro.append(f"Profile: {summary}")
    if total > 0:
        intro.append(f"Sending {shown} scheme(s), one message per scheme.")
    messages.append("\n".join(intro))

    if not schemes:
        messages.append("No schemes found for the provided details.")
        return messages

    for idx, scheme in enumerate(schemes[:max_schemes], start=1):
        lines = [
            f"Scheme {idx}/{shown} (Rank {scheme.get('rank', idx)})",
            f"Name: {_clean_text(scheme.get('scheme_name', 'N/A'))}",
        ]
        if v := _clean_text(scheme.get("relevance_reason", "")):
            lines.append(f"Why relevant: {v}")
        if v := _clean_text(scheme.get("benefits", "")):
            lines.append(f"Benefits: {v}")
        if v := _clean_text(scheme.get("eligibility_summary", "")):
            lines.append(f"Eligibility: {v}")
        if v := _clean_text(scheme.get("required_documents", "")):
            lines.append(f"Required documents: {v}")
        if v := _clean_text(scheme.get("application_process", "")):
            lines.append(f"How to apply: {v}")
        if v := _clean_text(scheme.get("official_link", "") or scheme.get("application_link", "")):
            lines.append(f"Official link: {v}")
        messages.append("\n".join(lines))

    if total > max_schemes:
        messages.append(f"Showing top {max_schemes} of {total} matches.")
    return messages
