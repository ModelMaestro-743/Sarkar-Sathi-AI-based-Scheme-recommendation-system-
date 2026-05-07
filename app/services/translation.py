from openai import OpenAI
from app.core.config import OPENAI_API_KEY, LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "English"
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Identify the language of the user text. Return only the language name, like English, Hindi, Marathi, Tamil.",
            },
            {"role": "user", "content": text},
        ],
    )
    return (response.choices[0].message.content or "").strip() or "English"


def translate_to_english(text: str, source_language: str | None = None) -> str:
    if not text or not text.strip():
        return ""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Translate the text to natural English. Preserve all details. Return only translated text.",
            },
            {
                "role": "user",
                "content": f"Source language hint: {source_language or 'auto-detect'}\n\nText:\n{text}",
            },
        ],
    )
    return (response.choices[0].message.content or "").strip() or text


def translate_from_english(text: str, target_language: str) -> str:
    if not text or not text.strip():
        return ""
    if (target_language or "").strip().lower() == "english":
        return text
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Translate the English text into the target language exactly. Preserve all details and formatting. Return only translated text.",
            },
            {
                "role": "user",
                "content": f"Target language: {target_language}\n\nEnglish text:\n{text}",
            },
        ],
    )
    return (response.choices[0].message.content or "").strip() or text
