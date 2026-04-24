   search_prompt_linkup = f"""
   Find all the currently active and **most suitable State Government schemes** for citizens based on the following user profile:
   
   ### 🧾 Inputs Provided:
   - **Full Name:** {user_data["name"]}
   - **Age:** {user_data["age"]}
   - **Gender:** {user_data["gender"]}
   - **Marital Status:** {user_data["marital_status"]}
   - **Caste:** {user_data["caste"]}
   - **City/Town/Village:** {user_data["city"]}
   - **State:** {user_data["state"]}
   - **Area Type:** {user_data["area_type"]}
   - **Education Level:** {user_data["education"]}
   - **Employment Type:** {user_data["employment"]}
   - **Monthly Income:** {user_data["income"]}
   - **Interest Sector:** {user_data["interest_sector"]}
   - **User Query (English):** {translated_query}
   
   ---
   
   ### 🎯 Core Search Objective:
   Retrieve **all active and relevant State Government schemes** launched or managed by the **{user_data["city"]}{user_data["state"]}{user_data["area_type"]}** state government that are suitable for the user’s demographic, financial, and occupational background.
   
   Each scheme should:
   - Be **currently open or recently launched**
   - Match the user's **eligibility profile** (age, gender, caste, income, education, etc.)
   - Offer **direct benefits or assistance** relevant to the user’s interest or goal
   - Include **official application links and verified details**
   
   ---
   
   ### 🧩 Include in Search:
   1. **Welfare Programs** – financial aid, insurance, health, and livelihood schemes.  
   2. **Entrepreneurship & Business Support** – startup grants, MSME support, and credit-linked subsidies.  
   3. **Education & Training** – scholarships, vocational programs, and employability schemes.  
   4. **Agriculture & Rural Development** – subsidies, loans, and farmer support schemes.  
   5. **Women, Youth, and Social Welfare** – empowerment, safety, and inclusion programs.  
   6. **Any Other State-specific Initiatives** beneficial to the user profile.
   
   ---
   
   ### 🔍 Prioritize Trusted and Verified Sources:
   - Official state portals 
   - State department websites (Agriculture, MSME, Skill Development, Women & Child Welfare, Education, etc.)
   - https://www.myscheme.gov.in, https://www.india.gov.in
   - Press releases or official notifications from **PIB**, **NIC**, or **State Gazette**
   
   Avoid data from unofficial blogs, news aggregators, or unverified sources.
   
   ---
   
   ### 🧠 Keywords to Focus:
   “{user_data["city"]}{user_data["state"]}{user_data["area_type"]} government scheme”, “{user_data["city"]}{user_data["state"]}{user_data["area_type"]} yojana”, “{user_data["city"]}{user_data["state"]}{user_data["area_type"]} subsidy program”,  
   “{user_data['interest_sector']} assistance”, “{user_data["city"]}{user_data["state"]}{user_data["area_type"]}  employment scheme”, “{user_data["city"]}{user_data["state"]}{user_data["area_type"]}  startup support”,  
   “{user_data["city"]}{user_data["state"]}{user_data["area_type"]}  financial aid”, “{user_data["city"]}{user_data["state"]}{user_data["area_type"]}  training program”, “{user_data["city"]}{user_data["state"]}{user_data["area_type"]}  welfare benefit”.
   
   ---
   
   ### ⚡ Output Expectation:
   - Return **all relevant and verified schemes** that fit the user’s profile — not just the top few.  
   - Maintain ranking using `recommendation_score` (to indicate relevance).  
   - Each scheme must include a **short descriptive summary** explaining how it benefits the user.  
   - All information should be **accurate, current, and state-specific**.
   """
   
   
   def linkup_search_tool():
       """Search for relevant legal cases using Linkup API with strict valid URL enforcement."""
   
       linkup = LinkupClient(api_key=os.getenv("LINKUP_API_KEY"))
   
       search_query = search_prompt_linkup
   
       structured_schema = {
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
                        "geographical_scope": {"type": "string"}
                    },
                    "required": [
                        "beneficiaries",
                        "age_limit",
                        "income_limit",
                        "education_requirement",
                        "geographical_scope"
                    ]
                },
                "benefits": {
                    "type": "object",
                    "properties": {
                        "financial_assistance": {"type": "string"},
                        "training_support": {"type": "string"},
                        "interest_rate_terms": {"type": "string"},
                        "other_benefits": {"type": "string"},
                        "validity": {"type": "string"}
                    },
                    "required": [
                        "financial_assistance",
                        "training_support",
                        "interest_rate_terms",
                        "other_benefits",
                        "validity"
                    ]
                },
                "application": {
                    "type": "object",
                    "properties": {
                        "process": {"type": "string"},
                        "documents_required": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "mode": {"type": "string"},
                        "official_url": {"type": "string"}
                    },
                    "required": [
                        "process",
                        "documents_required",
                        "mode",
                        "official_url"
                    ]
                },
                "contact_info": {
                    "type": "object",
                    "properties": {
                        "department": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "grievance_portal": {"type": "string"}
                    },
                    "required": [
                        "department",
                        "email",
                        "phone",
                        "grievance_portal"
                    ]
                },
                "recommendation_score": {"type": "string"},
                "why_recommended": {"type": "string"},
                "last_updated": {"type": "string"},
                "source_url": {"type": "string"}
            },
            "required": [
                "scheme_name",
                "implementing_authority",
                "scheme_type",
                "objective",
                "eligibility",
                "benefits",
                "application",
                "contact_info",
                "recommendation_score",
                "why_recommended",
                "last_updated",
                "source_url"
            ]
        },
        "descriptive_summary": {"type": "string"}
    },
    "required": ["structured_output", "descriptive_summary"]
}
   
       # Run the search (LLM output expected)
       result = linkup.search(
           query=search_query,
           depth="standard",
           output_type="structured",
           structured_output_schema=json.dumps(structured_schema),
           include_images=False
       )
      
       formatted_result = json.dumps(result, indent=2)
           # Return the result as a JSON string for the agent
       return formatted_result