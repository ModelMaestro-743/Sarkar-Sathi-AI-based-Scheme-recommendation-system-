<div align="center">

# 🏛️ Sarkar Sathi
### AI-Powered Government Scheme Recommendation System

*Helping every Indian citizen discover the government schemes they deserve — in their own language, on WhatsApp.*

[![Python](https://img.shields.io/badge/Python-3.11.9-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://twilio.com)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

### 💬 Try it — Chat with Sarkar Sathi on WhatsApp

<a href="https://wa.me/14155238886?text=Hello">
  <img src="https://img.shields.io/badge/WhatsApp-Start%20Chat%20Now-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="Chat on WhatsApp"/>
</a>

> **Save `+1 415 523 8886` on WhatsApp and send any message to begin.**
> The bot will guide you in English, Hindi, or Marathi — no app download needed.

---

[Features](#-features) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack) • [Setup](#-local-setup) • [API](#-api-endpoints) • [Deploy](#-deployment) • [Team](#-team)

</div>

---

## 📱 For Users — How to Use Sarkar Sathi

No installation needed. Just WhatsApp.

### Step 1 — Save the number and say Hello

Save **`+1 415 523 8886`** on your phone and open WhatsApp.

Or tap this link to open the chat directly:
👉 **[https://wa.me/14155238886?text=Hello](https://wa.me/14155238886?text=Hello)**

### Step 2 — Answer 8 simple questions

The bot will ask you questions one by one:

```
1. Choose your language      → English / Hindi / Marathi
2. Your name
3. Your state
4. Urban or Rural area
5. Employment type           → Student / Unemployed / Self-employed / Private / Government
6. Monthly income
7. Education level
8. Sector of interest        → Agriculture / Health / Education / Business / etc.
```

### Step 3 — Ask your query

After the questions, type your query in your own language:

```
"मुझे कृषि सब्सिडी के बारे में जानकारी चाहिए"
"मला शेती योजना हवी आहे"
"I need scholarships for higher education"
```

### Step 4 — Get your personalised scheme recommendations

The bot replies with the top 3 matching government schemes including benefits, eligibility, required documents, and how to apply.

### Step 5 — Continue the conversation

After getting results you can:

| Command | What it does |
|---|---|
| `more` / `और` / `आणखी` | Ask a new query with your same profile |
| `update income: 25000` | Update any profile field |
| `yes` / `हाँ` / `होय` | Restart the full form |
| `stop` / `रोक` / `थांब` | Pause your session |
| `resume` / `जारी` / `सुरू` | Resume a paused session |

---

## 📌 What is Sarkar Sathi?

**Sarkar Sathi** (meaning *Government Friend*) is a conversational AI assistant accessible via **WhatsApp** that recommends the most relevant Indian government schemes to citizens based on their personal profile.

The bot asks 8 simple questions, understands responses in **English, Hindi, or Marathi**, and uses a **RAG (Retrieval-Augmented Generation)** pipeline to match the user against a database of **3,400+ government schemes** — returning the top ranked results with full eligibility, benefits, and application details.

> **Problem it solves:** Millions of eligible Indians never benefit from government schemes simply because they don't know they exist or how to apply. Sarkar Sathi bridges this gap through the most widely used messaging platform in India — WhatsApp.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗣️ **Multilingual** | Supports English, Hindi, and Marathi — detects and responds in the user's language |
| 📱 **WhatsApp Native** | Works entirely over WhatsApp — no app download needed |
| 🔍 **AI-Powered Search** | FAISS vector search + GPT-4o-mini ranking for accurate recommendations |
| 🌐 **Live Web Search** | LinkUp API augments local database with real-time state-specific schemes |
| 💬 **Smart Conversation** | Session management with pause/resume, update fields, ask more queries |
| 📊 **3,400+ Schemes** | Covers Central, State, and Union Territory schemes across all categories |
| ⚡ **Fast Responses** | Pre-built FAISS index enables sub-second vector search |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (WhatsApp)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Message
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TWILIO WEBHOOK                                │
│              POST /webhook  (FastAPI)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SESSION MANAGER                                │
│         8-Step Questionnaire Flow                               │
│  Language → Name → State → Area → Employment →                  │
│  Income → Education → Interest Sector → Query                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Full user profile
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                                 │
│                                                                 │
│  1. translate_to_english()   GPT-4o-mini                        │
│       ↓                                                         │
│  2. build_enriched_query()   Combine profile + query            │
│       ↓                                                         │
│  3. FAISS MMR Search         Top 6 candidate schemes            │
│       ↓                           +                             │
│  4. LinkUp Web Search        Live state-specific schemes        │
│       ↓                                                         │
│  5. generate_structured_json()  GPT-4o-mini ranks top 3         │
│       ↓                                                         │
│  6. translate_from_english()  Back to user's language           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Top 3 schemes (formatted)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              TWILIO → WhatsApp Reply                            │
│         (auto-split at 1600 chars per message)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

<details>
<summary><b>Click to expand full tech stack</b></summary>

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI 0.136.1 | REST API + WhatsApp webhook |
| **Server** | Uvicorn 0.40.0 | ASGI server |
| **LLM** | GPT-4o-mini (OpenAI) | Scheme ranking, translation, language detection |
| **Embeddings** | text-embedding-3-large | Vector representation of 3,400 schemes |
| **Vector Store** | FAISS (CPU) | Fast similarity search with MMR diversity |
| **RAG Framework** | LangChain | Document loading and retrieval orchestration |
| **Messaging** | Twilio WhatsApp API | Send/receive WhatsApp messages |
| **Web Search** | LinkUp API | Live state-specific scheme lookup |
| **Data** | Pandas | CSV processing of scheme dataset |
| **Validation** | Pydantic v2 | Request/response schema validation |
| **Deployment** | Render | Cloud hosting |

</details>

---

## 📁 Project Structure

```
sarkar-sathi/
├── app/                          # Main application package
│   ├── main.py                   # FastAPI app entry point
│   ├── api/
│   │   └── routes.py             # All endpoints + webhook conversation logic
│   ├── constants/
│   │   └── conversation.py       # Question flow, UI text (EN/HI/MR), commands
│   ├── core/
│   │   ├── config.py             # Environment variables & file paths
│   │   └── session.py            # In-memory session store
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── prompts/
│   │   └── templates.py          # LLM prompt templates
│   └── services/
│       ├── rag.py                # FAISS search + LLM ranking pipeline
│       ├── translation.py        # Language detection & translation
│       ├── whatsapp.py           # Twilio messaging + message formatting
│       └── web_search.py         # LinkUp live web search
│
├── data/
│   ├── schemes.csv               # 3,400 Indian government schemes dataset
│   └── category_questions.json   # Category-specific follow-up questions
│
├── vector_store/
│   └── scheme_faiss_index/       # Pre-built FAISS vector embeddings (54 MB)
│
├── notebooks/
│   └── gov_scheme_rag.ipynb      # Development & experimentation notebook
│
├── requirements.txt
├── Procfile                      # Heroku / Render process definition
├── runtime.txt                   # Python 3.11.9
├── .env.example                  # Environment variable template
└── README.md
```

---

## 💬 Conversation Flow

```
User sends first message
        ↓
[1] Choose Language      →  English / Hindi / Marathi
[2] Your Name           →  Free text
[3] State               →  E.g. Maharashtra, Gujarat
[4] Area Type           →  Urban / Rural
[5] Employment          →  Student / Unemployed / Self-employed / Private / Government
[6] Monthly Income      →  In ₹
[7] Education Level     →  Free text
[8] Interest Sector     →  Agriculture / Health / Education / Business etc.
[9] Your Query          →  Ask anything in your language
        ↓
Bot searches + replies with Top 3 schemes
        ↓
User can:
  • Reply "more"              → Ask a new query with same profile
  • Reply "update field: val" → Update any profile field
  • Reply "yes"               → Restart the full form
  • Reply "stop"              → Pause session
  • Reply "resume"            → Continue paused session
```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.11.9
- OpenAI API key
- Twilio account with WhatsApp sandbox
- (Optional) LinkUp API key for live web search

### 1. Clone the repository

```bash
git clone https://github.com/your-username/sarkar-sathi.git
cd sarkar-sathi
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-your-openai-key
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
LINKUP_API_KEY=your-linkup-api-key
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`

### 6. Test the API

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

**Quick test:**
```bash
curl -X POST http://127.0.0.1:8000/process_query \
  -H "Content-Type: application/json" \
  -d '{"query": "I am a female student in Maharashtra looking for education scholarships"}'
```

### 7. Test WhatsApp locally (ngrok)

```bash
ngrok http 8000
```

Set `https://your-ngrok-url.ngrok.io/webhook` as your Twilio WhatsApp sandbox webhook URL.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/docs` | Interactive Swagger UI |
| `POST` | `/process_query` | Direct scheme search (JSON input) |
| `POST` | `/webhook` | Twilio WhatsApp webhook |

<details>
<summary><b>POST /process_query — Request & Response example</b></summary>

**Request:**
```json
{
  "query": "I am a farmer in Maharashtra looking for agricultural subsidies"
}
```

**Response:**
```json
{
  "user_profile_summary": "Farmer in Maharashtra seeking agricultural subsidies.",
  "recommended_schemes": [
    {
      "rank": 1,
      "scheme_name": "Nanaji Deshmukh Krishi Sanjivani Prakalp",
      "relevance_reason": "Climate-resilient farming support for Maharashtra farmers",
      "benefits": "70% subsidy for drip irrigation, poly houses, farm ponds...",
      "eligibility_summary": "Registered farmers in project villages",
      "application_process": "Register at dbt.mahapocra.gov.in",
      "required_documents": "Aadhaar, 7/12 extract, caste certificate",
      "level": "State",
      "category": "Agriculture, Rural & Environment"
    }
  ]
}
```

</details>

---

## 🌍 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | OpenAI API key (GPT-4o-mini + embeddings) |
| `TWILIO_ACCOUNT_SID` | ✅ | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | ✅ | Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | ✅ | Twilio WhatsApp sender number |
| `LINKUP_API_KEY` | ⚪ | LinkUp API key (optional — enables live web search) |

---

## 🚀 Deployment

### Deploy on Render (Recommended)

#### Step 1 — Push code to GitHub

```bash
git add .
git commit -m "initial deployment"
git push origin main
```

#### Step 2 — Create a Web Service on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub account and select your repository
3. Configure the service:

| Setting | Value |
|---|---|
| **Environment** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free (or Starter for always-on) |

#### Step 3 — Add environment variables

In your Render dashboard → **Environment** tab, add:

| Key | Value |
|---|---|
| `OPENAI_API_KEY` | your OpenAI key |
| `TWILIO_ACCOUNT_SID` | your Twilio SID |
| `TWILIO_AUTH_TOKEN` | your Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` |
| `LINKUP_API_KEY` | your LinkUp key |

#### Step 4 — Deploy

Click **Create Web Service**. Render will build and deploy automatically.
Your app URL will be: `https://your-app-name.onrender.com`

#### Step 5 — Connect Twilio Webhook

1. Go to **Twilio Console → Messaging → Try it out → Send a WhatsApp message**
2. Under **Sandbox Configuration**, set the webhook URL to:
```
https://your-app-name.onrender.com/webhook
```
3. Set HTTP method to **POST**
4. Save

#### Step 6 — Share your WhatsApp number with users

Give users this click-to-chat link (replace with your actual number after going live with a real Twilio number):
```
https://wa.me/YOUR_WHATSAPP_NUMBER?text=Hello
```

For the Twilio sandbox:
```
https://wa.me/14155238886?text=join your-sandbox-keyword
```

> ⚠️ **Render free tier:** Spins down after 15 minutes of inactivity — first message after a gap takes ~30 seconds. Upgrade to **Starter ($7/month)** for always-on availability ideal for demos and production.

> ⚠️ **Twilio sandbox:** Requires each user to send `join <keyword>` before they can receive messages. For production, upgrade to a real Twilio WhatsApp number — users can then message directly without joining.

---

## 📊 Dataset

The scheme database contains **3,400+ Indian government schemes** scraped from official portals:

| Field | Description |
|---|---|
| `scheme_name` | Official name of the scheme |
| `details` | Full description |
| `benefits` | Financial and non-financial benefits |
| `eligibility` | Who can apply |
| `application` | How to apply |
| `documents` | Required documents |
| `level` | Central / State / Union Territory |
| `schemeCategory` | Education, Health, Agriculture, etc. |
| `tags` | Search keywords |

**Sources:** myscheme.gov.in, india.gov.in, state government portals

---

## 🧠 How the RAG Pipeline Works

<details>
<summary><b>Click to understand the AI pipeline in detail</b></summary>

1. **User profile collection** — 8-step WhatsApp questionnaire collects demographic, financial, and interest data.

2. **Translation** — User's query (in Hindi/Marathi) is translated to English using GPT-4o-mini before search.

3. **Enriched query building** — Profile fields (state, employment, income, education, sector) are combined with the translated query into a rich context string.

4. **FAISS MMR Search** — The enriched query is embedded using `text-embedding-3-large` and searched against the pre-built FAISS index using **Maximal Marginal Relevance** (ensures diverse, non-redundant results). Top 6 candidates retrieved.

5. **Web search augmentation** — If a state is known and `LINKUP_API_KEY` is set, LinkUp API searches for live state-specific schemes and adds them to the context.

6. **LLM Ranking** — GPT-4o-mini reads all retrieved schemes + user profile and ranks the top 3 by relevance, generating a structured JSON output.

7. **Translation back** — Results are translated to the user's preferred language before sending.

8. **WhatsApp formatting** — Messages are split at 1600 characters (Twilio limit) and sent as numbered chunks.

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how:

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
# Make your changes
git commit -m "add: your feature description"
git push origin feature/your-feature-name
# Open a Pull Request
```

**Areas that would benefit from contributions:**
- Adding more Indian languages (Tamil, Telugu, Bengali, Kannada)
- Redis-based session persistence
- Admin dashboard for scheme analytics
- Automated scheme dataset updates

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

Built with ❤️ for India's 1.4 billion citizens

**Sarkar Sathi** — *Because every citizen deserves to know their rights.*

</div>
