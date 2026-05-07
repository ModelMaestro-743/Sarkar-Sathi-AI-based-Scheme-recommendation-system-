import json
import os

import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from app.core.config import (
    DATASET_PATH,
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    LLM_MODEL,
    OPENAI_API_KEY,
)
from app.prompts.templates import scheme_advisor_prompt

client = OpenAI(api_key=OPENAI_API_KEY)

_df = None
_vectorstore = None


def _require_openai_key():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in your .env file.")


def _load_dataframe():
    global _df
    if _df is None:
        df = pd.read_csv(DATASET_PATH)
        df = df.drop(columns=["Unnamed: 9"], errors="ignore")
        df = df.fillna("")
        _df = df
    return _df


def _build_documents(df):
    documents = []
    for _, row in df.iterrows():
        content = f"""
        Scheme Name: {row['scheme_name']}

        Description:
        {row['details']}

        Benefits:
        {row['benefits']}

        Eligibility:
        {row['eligibility']}

        Application Process:
        {row['application']}

        Required Documents:
        {row['documents']}

        Category:
        {row['schemeCategory']}

        Level:
        {row['level']}

        Tags:
        {row['tags']}
        """
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "scheme_name": row["scheme_name"],
                    "level": row["level"],
                    "category": row["schemeCategory"],
                    "slug": row["slug"],
                },
            )
        )
    return documents


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore
    _require_openai_key()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
    if os.path.isdir(FAISS_INDEX_PATH):
        _vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
    else:
        df = _load_dataframe()
        _vectorstore = FAISS.from_documents(_build_documents(df), embeddings)
        _vectorstore.save_local(FAISS_INDEX_PATH)
    return _vectorstore


def build_enriched_query(user_data: dict) -> str:
    return f"""
    User Profile Information:

    Name: {user_data.get('name')}
    Age: {user_data.get('age')}
    Gender: {user_data.get('gender')}
    Marital Status: {user_data.get('marital_status')}
    Caste: {user_data.get('caste')}

    Location:
    City: {user_data.get('city')}
    State: {user_data.get('state')}
    Area Type: {user_data.get('area_type')}

    Education & Employment:
    Education Level: {user_data.get('education')}
    Employment Type: {user_data.get('employment')}
    Monthly Income: {user_data.get('income')}

    Sector of Interest:
    {user_data.get('interest_sector')}

    User Query:
    {user_data.get('user_query')}

    Based on this profile, suggest government schemes where this person is eligible.
    """


def recommend_schemes(user_data: dict, k: int = 6) -> list[str]:
    vectorstore = _get_vectorstore()
    results = vectorstore.max_marginal_relevance_search(
        build_enriched_query(user_data), k=k, fetch_k=20
    )
    return [doc.metadata["slug"] for doc in results]


def get_complete_scheme_details(slugs: list[str], df):
    return df[df["slug"].isin(slugs)]


def prepare_llm_context(df_filtered) -> str:
    blocks = []
    for _, row in df_filtered.iterrows():
        blocks.append(f"""
        Scheme Name: {row['scheme_name']}
        Category: {row['schemeCategory']}
        Level: {row['level']}

        Description:
        {row['details']}

        Benefits:
        {row['benefits']}

        Eligibility:
        {row['eligibility']}

        Application Process:
        {row['application']}

        Required Documents:
        {row['documents']}

        Tags:
        {row['tags']}
        """)
    return "\n\n".join(blocks)


def generate_structured_json(user_data: dict, scheme_context: str) -> dict:
    _require_openai_key()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "Return only valid JSON. Do not wrap in markdown code fences."},
            {"role": "user", "content": scheme_advisor_prompt(user_data, scheme_context)},
        ],
    )
    output_text = (response.choices[0].message.content or "").strip()
    if output_text.startswith("```"):
        lines = output_text.splitlines()
        output_text = "\n".join(
            lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        ).strip()
    try:
        return json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}. Raw: {output_text[:300]}")


def _format_linkup_result(linkup_json_str: str) -> str:
    """Convert a LinkUp result JSON string into scheme context text for the LLM."""
    try:
        data = json.loads(linkup_json_str)
        s = data.get("structured_output", {})
        if not s.get("scheme_name"):
            return ""
        eligibility = s.get("eligibility", {})
        benefits = s.get("benefits", {})
        application = s.get("application", {})
        return "\n".join([
            f"Scheme Name: {s.get('scheme_name', '')}",
            f"Category: {s.get('scheme_type', '')}",
            "Level: State (live web search result)",
            f"\nDescription:\n{s.get('objective', '')}",
            f"\nBenefits:\n{benefits.get('financial_assistance', '')} {benefits.get('other_benefits', '')}".strip(),
            f"\nEligibility:\nBeneficiaries: {eligibility.get('beneficiaries', '')} | Age: {eligibility.get('age_limit', '')} | Income: {eligibility.get('income_limit', '')}",
            f"\nApplication Process:\n{application.get('process', '')}",
            f"\nRequired Documents:\n{', '.join(application.get('documents_required', []))}",
            f"\nSource: {s.get('source_url', '')}",
        ])
    except Exception:
        return ""


def get_top_schemes_with_profile(user_data: dict) -> dict:
    """Run the full RAG pipeline with the collected user profile."""
    profile = {
        "preferred_language": user_data.get("preferred_language", "English"),
        "name": user_data.get("name", ""),
        "age": user_data.get("age", ""),
        "gender": user_data.get("gender", ""),
        "marital_status": user_data.get("marital_status", ""),
        "caste": user_data.get("caste", ""),
        "city": user_data.get("city", ""),
        "state": user_data.get("state", ""),
        "area_type": user_data.get("area_type", ""),
        "education": user_data.get("education", ""),
        "employment": user_data.get("employment", ""),
        "income": user_data.get("income", ""),
        "interest_sector": user_data.get("interest_sector", ""),
        "user_query": user_data.get("user_query", ""),
    }
    slugs = recommend_schemes(profile)
    full_info = get_complete_scheme_details(slugs, _load_dataframe())
    scheme_context = prepare_llm_context(full_info)

    # Augment FAISS results with live web search when state is known
    if profile.get("state") and os.getenv("LINKUP_API_KEY"):
        try:
            from app.services.web_search import linkup_search_tool
            extra_context = _format_linkup_result(
                linkup_search_tool(profile, profile["user_query"])
            )
            if extra_context:
                scheme_context = scheme_context + "\n\n" + extra_context
        except Exception as exc:
            print(f"[linkup] web search skipped: {exc}")

    return generate_structured_json(profile, scheme_context)


def get_top_schemes(query: str) -> dict:
    """Lightweight entry point for the /process_query endpoint (no profile)."""
    if not query or not query.strip():
        raise ValueError("Query is required.")
    return get_top_schemes_with_profile({"user_query": query.strip()})
