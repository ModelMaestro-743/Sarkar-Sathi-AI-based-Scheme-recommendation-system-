import json
import os

from linkup import LinkupClient

from app.prompts.templates import web_search_prompt

_STRUCTURED_SCHEMA = {
    "type": "object",
    "properties": {
        "structured_output": {
            "type": "object",
            "properties": {
                "scheme_name": {"type": "string"},
                "implementing_authority": {"type": "string"},
                "scheme_type": {"type": "string"},
                "objective": {"type": "string"},
                "eligibility": {
                    "type": "object",
                    "properties": {
                        "beneficiaries": {"type": "string"},
                        "age_limit": {"type": "string"},
                        "income_limit": {"type": "string"},
                        "education_requirement": {"type": "string"},
                        "geographical_scope": {"type": "string"},
                    },
                    "required": ["beneficiaries", "age_limit", "income_limit", "education_requirement", "geographical_scope"],
                },
                "benefits": {
                    "type": "object",
                    "properties": {
                        "financial_assistance": {"type": "string"},
                        "training_support": {"type": "string"},
                        "interest_rate_terms": {"type": "string"},
                        "other_benefits": {"type": "string"},
                        "validity": {"type": "string"},
                    },
                    "required": ["financial_assistance", "training_support", "interest_rate_terms", "other_benefits", "validity"],
                },
                "application": {
                    "type": "object",
                    "properties": {
                        "process": {"type": "string"},
                        "documents_required": {"type": "array", "items": {"type": "string"}},
                        "mode": {"type": "string"},
                        "official_url": {"type": "string"},
                    },
                    "required": ["process", "documents_required", "mode", "official_url"],
                },
                "contact_info": {
                    "type": "object",
                    "properties": {
                        "department": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "grievance_portal": {"type": "string"},
                    },
                    "required": ["department", "email", "phone", "grievance_portal"],
                },
                "recommendation_score": {"type": "string"},
                "why_recommended": {"type": "string"},
                "last_updated": {"type": "string"},
                "source_url": {"type": "string"},
            },
            "required": [
                "scheme_name", "implementing_authority", "scheme_type", "objective",
                "eligibility", "benefits", "application", "contact_info",
                "recommendation_score", "why_recommended", "last_updated", "source_url",
            ],
        },
        "descriptive_summary": {"type": "string"},
    },
    "required": ["structured_output", "descriptive_summary"],
}


def linkup_search_tool(user_data: dict, translated_query: str) -> str:
    """Search for state-specific government schemes via the LinkUp API.

    Args:
        user_data: User profile dict.
        translated_query: User's query already translated to English.

    Returns:
        JSON string with structured scheme results.
    """
    api_key = os.getenv("LINKUP_API_KEY")
    if not api_key:
        raise RuntimeError("LINKUP_API_KEY is not set in environment variables.")
    linkup = LinkupClient(api_key=api_key)
    result = linkup.search(
        query=web_search_prompt(user_data, translated_query),
        depth="standard",
        output_type="structured",
        structured_output_schema=json.dumps(_STRUCTURED_SCHEMA),
        include_images=False,
    )
    return json.dumps(result, indent=2)
