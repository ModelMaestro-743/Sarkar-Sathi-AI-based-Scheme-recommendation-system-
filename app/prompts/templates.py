import json


def scheme_advisor_prompt(user_data: dict, scheme_context: str) -> str:
    return f"""You are an AI Government Scheme Advisor.

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


def web_search_prompt(user_data: dict, translated_query: str) -> str:
    state = user_data.get("state", "")
    city = user_data.get("city", "")
    area = user_data.get("area_type", "")
    location = " ".join(filter(None, [city, state, area]))
    sector = user_data.get("interest_sector", "")

    return f"""Find all the currently active and most suitable State Government schemes for citizens based on the following user profile:

### Inputs Provided:
- Full Name: {user_data.get("name", "")}
- Age: {user_data.get("age", "")}
- Gender: {user_data.get("gender", "")}
- Marital Status: {user_data.get("marital_status", "")}
- Caste: {user_data.get("caste", "")}
- City/Town/Village: {city}
- State: {state}
- Area Type: {area}
- Education Level: {user_data.get("education", "")}
- Employment Type: {user_data.get("employment", "")}
- Monthly Income: {user_data.get("income", "")}
- Interest Sector: {sector}
- User Query (English): {translated_query}

### Core Search Objective:
Retrieve all active and relevant State Government schemes for {location} that match the user's demographic, financial, and occupational background.

Each scheme should:
- Be currently open or recently launched
- Match the user's eligibility profile (age, gender, caste, income, education, etc.)
- Offer direct benefits relevant to the user's interest or goal
- Include official application links and verified details

### Include in Search:
1. Welfare Programs – financial aid, insurance, health, and livelihood schemes.
2. Entrepreneurship & Business Support – startup grants, MSME support, credit-linked subsidies.
3. Education & Training – scholarships, vocational programs, employability schemes.
4. Agriculture & Rural Development – subsidies, loans, and farmer support schemes.
5. Women, Youth, and Social Welfare – empowerment, safety, and inclusion programs.
6. Any Other State-specific Initiatives beneficial to the user profile.

### Prioritize Trusted Sources:
- Official state portals and department websites
- https://www.myscheme.gov.in, https://www.india.gov.in
- Press releases from PIB, NIC, or State Gazette

### Keywords to Focus:
"{location} government scheme", "{location} yojana", "{location} subsidy program",
"{sector} assistance", "{location} employment scheme", "{location} financial aid".

### Output Expectation:
- Return all relevant verified schemes fitting the user's profile.
- Rank using recommendation_score.
- Each scheme must include a short summary explaining how it benefits the user.
"""
