import os
import json
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import pandas as pd
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")
DATASET_PATH = "Scrapped Gov Schemes Dataset.csv"
FAISS_INDEX_PATH = "scheme_faiss_index"
EMBEDDING_MODEL = "text-embedding-3-large"

_df = None
_vectorstore = None

        
# Model Configurations
model_client = OpenAIChatCompletionClient(
    model = 'gpt-4o-mini',
    api_key=openai_api_key
    )

def _require_openai_key():
    if not openai_api_key:
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
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=openai_api_key)

    if os.path.isdir(FAISS_INDEX_PATH):
        _vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        df = _load_dataframe()
        documents = _build_documents(df)
        _vectorstore = FAISS.from_documents(documents, embeddings)
        _vectorstore.save_local(FAISS_INDEX_PATH)

    return _vectorstore


def get_user_details():
   print("Please provide the following details:\n")
   
   user_data = {}
   
   # Basic Details
   user_data["preferred_language"] = input("Preferred Language (e.g., Hindi, English, Marathi): ").strip()
   user_data["name"] = input("Full Name: ").strip()
   user_data["age"] = input("Age: ").strip()
   user_data["gender"] = input("Gender (Male/Female/Other): ").strip()
   user_data["marital_status"] = input("Marital Status (Single/Married/Other): ").strip()
   user_data["caste"] = input("Caste (Optional, press Enter to skip): ").strip()
   # Location Details
   print("\n--- Location Details ---")
   user_data["city"] = input("City/Town/Village: ").strip()
   user_data["state"] = input("State: ").strip()
   user_data["area_type"] = input("Area Type (Urban/Rural): ").strip()
   # Education and Employment
   print("\n--- Education & Employment ---")
   user_data["education"] = input("Highest Education Level: ").strip()
   user_data["employment"] = input("Employment Type (Student/Unemployed/Self-employed/Private/Government): ").strip()
   user_data["income"] = input("Monthly Income (in ₹ or 'N/A'): ").strip()
   # Interest and Query
   print("\n--- Additional Information ---")
   user_data["interest_sector"] = input("Interest Sector (e.g., Agriculture, Business, Education, Health): ").strip()
   user_data["user_query"] = input(f"Please enter your query in your preferred language ({user_data['preferred_language']}): ").strip()
   print("\n✅ All details collected successfully!\n")

   return user_data

def build_enriched_query(user_data):
    
    enriched_query = f"""
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
    
    return enriched_query

def recommend_schemes(user_data, k=6):
    vectorstore = _get_vectorstore()
    enriched_query = build_enriched_query(user_data)

    results = vectorstore.max_marginal_relevance_search(
        enriched_query,
        k=k,
        fetch_k=20
    )
    
    # Extract slugs
    recommended_slugs = [doc.metadata["slug"] for doc in results]
    
    return recommended_slugs

def get_complete_scheme_details(slugs, df):
    
    complete_info = df[df["slug"].isin(slugs)]
    
    return complete_info

def prepare_llm_context(df_filtered):
    
    scheme_blocks = []
    
    for _, row in df_filtered.iterrows():
        
        scheme_text = f"""
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
        """
        
        scheme_blocks.append(scheme_text)
    
    return "\n\n".join(scheme_blocks)

def generate_structured_json(user_data, scheme_context):
    _require_openai_key()
    prompt = f"""
    You are an AI Government Scheme Advisor.
    
    User Profile:
    {json.dumps(user_data, indent=2)}
    
    Below are the retrieved government schemes:
    
    {scheme_context}
    
    Your task:
    1. Rank the schemes based on relevance to the user.
    2. Generate a structured JSON response.
    3. Do NOT add any information not present in the schemes.
    4. Only return valid JSON.
    
    Required JSON Format:
    
    {{
      "user_profile_summary": "...",
      "recommended_schemes": [
        {{
          "rank": 1,
          "scheme_name": "...",
          "relevance_reason": "...",
          "benefits": "...",
          "eligibility_summary": "...",
          "application_process": "...",
          "required_documents": "...",
          "level": "...",
          "category": "..."
        }}
      ]
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    
    output_text = response.choices[0].message.content
    
    return json.loads(output_text)


def detect_language(text: str) -> str:
    """Detect natural language name from text (e.g., English, Hindi, Marathi)."""
    if not text or not text.strip():
        return "English"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Identify the language of the user text. Return only the language name, like English, Hindi, Marathi, Tamil.",
            },
            {"role": "user", "content": text},
        ],
    )
    language = (response.choices[0].message.content or "").strip()
    return language or "English"


def translate_to_english(text: str, source_language: str | None = None) -> str:
    """Translate text to English while preserving intent and details."""
    if not text or not text.strip():
        return ""

    source_hint = source_language or "auto-detect"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Translate the text to natural English. Preserve all details. Return only translated text.",
            },
            {
                "role": "user",
                "content": f"Source language hint: {source_hint}\n\nText:\n{text}",
            },
        ],
    )
    translated = (response.choices[0].message.content or "").strip()
    return translated or text


def translate_from_english(text: str, target_language: str) -> str:
    """Translate English text into the target language while preserving all details."""
    if not text or not text.strip():
        return ""

    if (target_language or "").strip().lower() == "english":
        return text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
    translated = (response.choices[0].message.content or "").strip()
    return translated or text


def get_top_schemes(query: str):
    if not query or not query.strip():
        raise ValueError("Query is required.")

    user_data = {
        "preferred_language": "English",
        "name": "User",
        "age": "",
        "gender": "",
        "marital_status": "",
        "caste": "",
        "city": "",
        "state": "",
        "area_type": "",
        "education": "",
        "employment": "",
        "income": "",
        "interest_sector": "",
        "user_query": query.strip(),
    }

    slugs = recommend_schemes(user_data)
    full_info = get_complete_scheme_details(slugs, _load_dataframe())
    scheme_context = prepare_llm_context(full_info)
    return generate_structured_json(user_data, scheme_context)

async def main():

   user_data = get_user_details()

   agent_1_prompt = f"""
   You are a multilingual translation agent specialized in converting user queries into fluent English.
   
   ### Objective:
   Translate the user's query from their known preferred language into clear, natural English while fully preserving its meaning and context.
   
   ### Inputs:
   - user_preferred_language: {user_data['preferred_language']}
   - user_query: {user_data['user_query']}
   
   ### Instructions:
   - Translate the query **only** from the specified user_preferred_language to English.
   - Maintain tone, politeness, and intent (e.g., question, request, or statement).
   - Avoid literal word-by-word translation — ensure it sounds natural.
   - Do not add any explanations or commentary.
   
   ### Output Format:
   {{
     "english_query": "translated query in English"
   }}
   """
   agent_1= AssistantAgent(name="eng_translator", model_client=model_client, system_message=agent_1_prompt)
   
   max_messages_termination = MaxMessageTermination(2)
   team = RoundRobinGroupChat(
       participants=[agent_1],
       termination_condition=max_messages_termination
   )
   result = await team.run(task="Convert the user query from preferred language to English")   
   
   translated_query =  result.messages[-1].content

   
   agent_2_prompt = f"""
   You are a multilingual translation and localization expert.
   
   ### Objective:
   Translate the provided English response into the user's original detected language while keeping it:
   - Clear and easy to understand for common citizens.
   - Grammatically correct and naturally flowing in that language.
   - Faithful to the meaning of the original English text (do not summarize or alter facts).
   
   ### Input:
   - user_prefered_language: {user_data['preferred_language']}
   - english_response: <search_agent_output>
   
   ### Output Format:
   {{
     "translated_response": "<final response translated in user's language>"
   }}
   
   If the prefered_language is 'English', simply return the english_response as is.
   """
   

       
   # Stage 1 – Retrieve Slugs
   slugs = recommend_schemes(user_data)
   
   # Stage 2 – Fetch Full Info
   full_info = get_complete_scheme_details(slugs, _load_dataframe())
   
   # Stage 3 – Prepare Context
   scheme_context = prepare_llm_context(full_info)
   
   # Stage 4 – Generate Structured JSON
   final_json = generate_structured_json(user_data, scheme_context)
   
   print(json.dumps(final_json, indent=2))

   
   native_translator= AssistantAgent(name="Native_Translator", model_client=model_client, system_message=agent_2_prompt)

   max_messages_termination = MaxMessageTermination(2)
   team2= RoundRobinGroupChat(
       participants=[native_translator],
       termination_condition=max_messages_termination
   )

   result2 = await team2.run(task=f"""Translate this into {user_data['preferred_language']}:\n{json.dumps(final_json, indent=2)}
   as it is and keep the structured response same""")
   final_output = result2.messages[-1].content
   with open("final_output.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

   print("✅ Final output saved to final_output.json")
   print(final_output)
   

if __name__ == "__main__":
    asyncio.run(main())
