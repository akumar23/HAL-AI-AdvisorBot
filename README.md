# HAL - Your AI Academic Advisor

An intelligent chatbot that helps Computer Engineering (CMPE) and Software Engineering (SE) students at San Jose State University navigate their academic journey. Think of it as having a knowledgeable advisor available 24/7 to answer your questions about courses, prerequisites, deadlines, and academic policies.

**Watch the demo:** [HAL in Action](https://youtu.be/dVwozVz11ho?t=78)

---

## Table of Contents

- [What is HAL?](#what-is-hal)
- [How It Works (In Plain English)](#how-it-works-in-plain-english)
- [Features at a Glance](#features-at-a-glance)
- [Quick Start](#quick-start)
  - [Method 1: Docker (Easiest - No Python Required)](#method-1-docker-easiest---no-python-required)
  - [Method 2: Local Python Installation](#method-2-local-python-installation)
  - [Method 3: Next.js Frontend](#method-3-nextjs-frontend-modern-react-interface)
- [Architecture Deep Dive](#architecture-deep-dive)
- [Configuration Options](#configuration-options)
- [Admin Interface](#admin-interface)
- [Glossary](#glossary)
- [Troubleshooting](#troubleshooting)
- [Contributing](#how-to-contribute)
- [FAQ](#faq)

---

## What is HAL?

HAL is an AI-powered chatbot designed specifically for SJSU engineering students. Instead of waiting for office hours or searching through multiple websites, you can simply ask HAL questions like:

- "What are the prerequisites for CMPE 131?"
- "Who is my academic advisor?"
- "When is the last day to drop a class?"
- "How many units can I take per semester?"

HAL understands context, remembers your conversation, and knows when to connect you with a human advisor for complex situations.

---

## How It Works (In Plain English)

### The Big Picture

Imagine you're in a library with thousands of books. When you ask the librarian a question, they don't read every book - they know exactly which shelf to check, pull the relevant books, and give you an answer based on what they found. That's essentially what HAL does, but with academic information.

Here's the step-by-step journey of your question:

```
Your Question
    ↓
1. Understanding What You're Asking (Intent Classification)
    ↓
2. Finding the Right Information (RAG Retrieval)
    ↓
3. Generating a Smart Answer (AI Response)
    ↓
4. Checking Confidence (Should a Human Help?)
    ↓
Your Answer (or Connection to Human Advisor)
```

### The Key Technologies (Explained Simply)

#### 1. RAG - The Smart Librarian System

**What it stands for:** Retrieval-Augmented Generation

**What it means:** Instead of making up answers, HAL searches a curated knowledge base first, finds relevant information, and then uses AI to craft an answer based only on what it found.

**Why it matters:** This prevents HAL from "hallucinating" or inventing information. If it's not in the knowledge base, HAL won't make it up.

**Real-world analogy:** Like Google search + ChatGPT combined - it searches for facts first, then writes a helpful answer using those facts.

**Technical details:**
- Uses ChromaDB to store course information, policies, and deadlines
- Converts your question into numbers (embeddings) to find semantically similar content
- Returns the top 5 most relevant documents to build a response

#### 2. Vector Database - The Smart Filing System

**What it is:** ChromaDB, a special database that stores information in a way that understands meaning, not just keywords.

**What it means:** When you ask "How do I drop a course?", it understands that's similar to "What's the process for withdrawing from a class?" even though the words are different.

**Why it matters:** You get relevant answers even if you don't use the exact terminology the university uses.

**Real-world analogy:** Like a librarian who knows that "car repair manual" and "automobile maintenance guide" mean the same thing.

**Technical details:**
- Stores documents as high-dimensional vectors (numerical representations)
- Uses cosine similarity to find related content
- Supports semantic search (meaning-based, not just keyword matching)

#### 3. Intent Classification - The Question Detective

**What it is:** A fast AI model that figures out what type of question you're asking.

**What it means:** HAL quickly determines if you're asking about prerequisites, deadlines, advisors, or something else. This happens in milliseconds before generating the full answer.

**Why it matters:** By understanding your intent, HAL can search more effectively and give better answers.

**Real-world analogy:** Like a receptionist who can route your call to the right department before you finish your sentence.

**Technical details:**
- Uses a small, fast model (Claude Haiku or GPT-4o-mini)
- Combines rule-based patterns with AI for speed
- Extracts entities (course codes, dates) from your question

#### 4. Conversation Context - The Memory System

**What it is:** HAL remembers what you talked about earlier in the conversation.

**What it means:** You can say "What about CMPE 135?" after asking about CMPE 131, and HAL knows you're still talking about prerequisites.

**Why it matters:** You can have a natural conversation without repeating yourself.

**Real-world analogy:** Like talking to a friend who remembers what you said five minutes ago.

**Technical details:**
- Stores conversation history in Flask sessions
- Resolves pronouns ("it", "that", "these") to actual entities
- Maintains context across multiple turns

#### 5. Confidence Scoring - The Self-Awareness System

**What it is:** HAL evaluates how confident it is about each answer.

**What it means:** HAL considers multiple factors: How well the retrieved documents matched your question, how clear your question was, whether it found enough information, etc.

**Why it matters:** HAL knows its limits. If confidence is low, it tells you to verify with a human advisor.

**Real-world analogy:** Like a knowledgeable friend who says "I'm pretty sure, but double-check with an expert" when they're uncertain.

**Technical details:**
- Multi-factor scoring algorithm
- Considers retrieval quality, intent clarity, and context resolution
- Score range: 0.0 (no confidence) to 1.0 (very confident)
- Threshold < 0.4 triggers human handoff

#### 6. Human Handoff - The Safety Net

**What it is:** A system that recognizes when HAL can't help and smoothly directs you to a human advisor.

**What it means:** For sensitive topics (academic probation), personal situations, or when confidence is very low, HAL provides booking links to speak with a real advisor.

**Why it matters:** You never get stuck with unhelpful answers. HAL knows when you need human expertise.

**Real-world analogy:** Like a store employee who says "Let me get the manager who specializes in this" when a question is beyond their expertise.

**Technical details:**
- Automatic escalation when confidence < 0.4
- Pattern detection for sensitive topics
- Provides advisor contact information and booking links

#### 7. Pluggable AI Brains

**What it is:** HAL supports three different AI providers: Claude (Anthropic), GPT (OpenAI), and Ollama (local).

**What it means:** The "intelligence" behind HAL can be swapped out. You can use cloud-based AI services or run everything locally on your computer.

**Why it matters:** Flexibility in cost, privacy, and performance. Universities can choose between cloud services or completely private local deployment.

**Real-world analogy:** Like a car that can run on gas, electric, or hybrid - same functionality, different power source.

**Technical details:**
- Factory pattern for provider abstraction
- Unified interface across Claude, OpenAI, and Ollama
- Configurable via environment variables
- Two-model approach: fast classifier + powerful main model

#### 8. Background Jobs - The Automated Assistant

**What it is:** Scheduled tasks that run automatically without human intervention.

**What it means:** Every week, HAL analyzes user feedback to find common issues. Every day, it checks system health. Every hour, it verifies the knowledge base is working.

**Why it matters:** Continuous improvement and maintenance without manual work.

**Real-world analogy:** Like a night cleaning crew that tidies up the office while everyone's asleep.

**Technical details:**
- Powered by APScheduler
- Weekly feedback analysis (Monday 6 AM)
- Daily analytics aggregation (2 AM)
- Hourly RAG index health checks
- Weekly cleanup of old data (Sunday 3 AM)

---

## Features at a Glance

- **Smart Q&A**: Ask questions in natural language, get accurate answers based on official university information
- **Context-Aware**: Remembers your conversation, handles follow-up questions naturally
- **Course Information**: Prerequisites, descriptions, units, department details
- **Advisor Lookup**: Find your assigned academic advisor based on your last name
- **Policy Knowledge**: Enrollment, dropping classes, refunds, graduation requirements
- **Important Deadlines**: Registration dates, drop deadlines, semester schedules
- **Confidence Indicators**: See how confident HAL is about each answer
- **Human Escalation**: Automatic connection to human advisors when needed
- **Quick Replies**: Contextual suggestions for follow-up questions
- **Feedback System**: Rate answers, help improve HAL over time
- **Admin Dashboard**: Manage content, view analytics, analyze feedback (for administrators)
- **Dual Frontend Options**: Choose between Flask (server-rendered) or Next.js (modern React)
- **Docker Support**: Easy deployment with Docker Compose

---

## Quick Start

Choose the installation method that works best for you:

### Method 1: Docker (Easiest - No Python Required)

This is the fastest way to get HAL running. Docker handles all the dependencies for you.

#### Option A: Pre-built Docker Image (Fastest)

```bash
# Pull the pre-built image
docker pull mfaryan/hal-final

# Run it
docker run -p 5000:5000 mfaryan/hal-final
```

Then visit: **http://127.0.0.1:5000/**

#### Option B: Docker Compose (Recommended for Production)

This runs both the Flask backend and Next.js frontend together.

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HAL-AI-AdvisorBot.git
   cd HAL-AI-AdvisorBot
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```bash
   LLM_PROVIDER=claude  # or openai, ollama
   ANTHROPIC_API_KEY=your-key-here
   SECRET_KEY=your-random-secret-key
   ```

3. **Start all services**
   ```bash
   docker compose up -d
   ```

4. **Access the application**
   - Next.js Frontend: **http://localhost:3000/**
   - Flask Backend API: **http://localhost:5000/**
   - Admin Interface: **http://localhost:5000/admin**

5. **View logs** (optional)
   ```bash
   docker compose logs -f
   ```

6. **Stop services**
   ```bash
   docker compose down
   ```

**What Docker Compose Includes:**
- Flask backend (Python API)
- Next.js frontend (React interface)
- Nginx reverse proxy (production mode)
- Persistent volumes for database and sessions

---

### Method 2: Local Python Installation

For developers who want to run HAL directly on their machine.

#### Prerequisites

**Python Version:** 3.10 - 3.12 (3.11 recommended)

> **Important:** Python 3.13+ is not currently supported due to dependency compatibility issues with ChromaDB. Please use Python 3.11 for the best experience.

To check your Python version:
```bash
python3 --version
```

#### Step-by-Step Installation

**Step 1: Clone the repository**
```bash
git clone https://github.com/yourusername/HAL-AI-AdvisorBot.git
cd HAL-AI-AdvisorBot
```

**Step 2: Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

This installs:
- Flask (web framework)
- ChromaDB (vector database)
- SQLAlchemy (database ORM)
- Flask-Admin (admin interface)
- APScheduler (background jobs)
- And more...

**Step 3: Configure environment variables**

Copy the example file:
```bash
cp .env.example .env
```

Open `.env` in a text editor and configure these settings:

```bash
# Choose your AI provider
LLM_PROVIDER=claude  # Options: claude, openai, ollama

# If using Claude (recommended)
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here

# If using OpenAI
OPENAI_API_KEY=sk-...your-key-here

# If using Ollama (local, free)
OLLAMA_BASE_URL=http://localhost:11434

# Flask secret (generate a random string)
SECRET_KEY=your-random-secret-key-here
```

**How to get API keys:**
- **Claude (Anthropic)**: Sign up at [console.anthropic.com](https://console.anthropic.com)
- **OpenAI**: Sign up at [platform.openai.com](https://platform.openai.com)
- **Ollama**: Download from [ollama.ai](https://ollama.ai) - runs completely locally, no API key needed

**Step 4: Build Tailwind CSS** (for the web interface)

First-time setup:
```bash
# Download Tailwind CLI (macOS Apple Silicon)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss

# For other platforms, see: https://tailwindcss.com/blog/standalone-cli
```

Build the CSS:
```bash
./scripts/build-css.sh build
```

Or for development (auto-rebuild on changes):
```bash
./scripts/build-css.sh watch
```

**Step 5: Migrate data to the database** (optional but recommended)

This imports the initial course and policy data:
```bash
python3 -m hal.cli.migrate_data
```

**Step 6: Run the application**
```bash
python3 run.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Step 7: Open in your browser**

Visit: **http://127.0.0.1:5000/**

You should see the HAL chat interface. Try asking a question like "What are the prerequisites for CMPE 131?"

---

### Method 3: Next.js Frontend (Modern React Interface)

For developers who prefer a modern React-based frontend with TypeScript and client-side routing.

#### Prerequisites
- Node.js 18+ and npm
- Flask backend already running (see Method 2 above)

#### Installation Steps

**Step 1: Start the Flask backend** (in one terminal)
```bash
python3 run.py
```

**Step 2: Install and run Next.js frontend** (in a second terminal)
```bash
# Navigate to frontend directory
cd nextjs-frontend

# Install dependencies (first time only)
npm install

# Configure API URL
cp .env.example .env.local
# Edit .env.local and set: NEXT_PUBLIC_API_URL=http://localhost:5000

# Start development server
npm run dev
```

**Step 3: Open in your browser**

Visit: **http://localhost:3000/**

**What's Different About the Next.js Frontend?**
- Modern React with TypeScript
- Client-side routing (no page reloads)
- Dark mode with system preference detection
- Optimized performance with Next.js 14+ App Router
- Rich components for courses, feedback, and escalation
- Fully responsive mobile-first design

For more details, see `nextjs-frontend/README.md`

---

## Architecture Deep Dive

For those who want to understand how everything connects:

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│       (Flask Templates OR Next.js React App)             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Flask Application                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Routes: /api/chat, /admin, /api/feedback       │   │
│  └──────────────────┬───────────────────────────────┘   │
└────────────────────┬┴───────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌───────┐  ┌──────────┐  ┌──────────┐
    │Session│  │Database  │  │Background│
    │Manager│  │(SQLite)  │  │Scheduler │
    └───────┘  └──────────┘  └──────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   RAG Pipeline         │
        │  ┌──────────────────┐  │
        │  │1. Intent         │  │
        │  │   Classification │  │
        │  └────────┬─────────┘  │
        │           ▼            │
        │  ┌──────────────────┐  │
        │  │2. Context        │  │
        │  │   Resolution     │  │
        │  └────────┬─────────┘  │
        │           ▼            │
        │  ┌──────────────────┐  │
        │  │3. Vector         │  │
        │  │   Retrieval      │  │◄─── ChromaDB
        │  └────────┬─────────┘  │
        │           ▼            │
        │  ┌──────────────────┐  │
        │  │4. Confidence     │  │
        │  │   Scoring        │  │
        │  └────────┬─────────┘  │
        │           ▼            │
        │  ┌──────────────────┐  │
        │  │5. LLM Response   │  │◄─── Claude/OpenAI/Ollama
        │  │   Generation     │  │
        │  └────────┬─────────┘  │
        │           ▼            │
        │  ┌──────────────────┐  │
        │  │6. Human Handoff  │  │
        │  │   (if needed)    │  │
        │  └──────────────────┘  │
        └────────────────────────┘
```

### Project Structure Explained

```
HAL-AI-AdvisorBot/
│
├── hal/                          # Main application package
│   ├── app.py                    # Web server and API routes
│   ├── config.py                 # Configuration (API keys, models)
│   │
│   ├── models/                   # Database structure
│   │   └── models.py             # Tables: courses, advisors, conversations
│   │
│   ├── services/                 # The brain of HAL
│   │   ├── rag_engine.py         # Main pipeline orchestrator
│   │   ├── llm_providers.py      # AI provider abstraction (Claude/OpenAI/Ollama)
│   │   ├── intent_classifier.py  # Question type detection
│   │   ├── conversation_manager.py # Conversation memory
│   │   ├── confidence_scoring.py # Confidence calculation & handoff
│   │   └── quick_replies.py      # Smart follow-up suggestions
│   │
│   ├── admin/                    # Admin interface
│   │   ├── admin.py              # Content management UI
│   │   ├── analytics.py          # Usage statistics
│   │   └── feedback_analyzer.py  # AI-powered feedback insights
│   │
│   ├── utils/                    # Helpers
│   │   └── scheduler.py          # Background jobs
│   │
│   └── cli/                      # Command-line tools
│       └── migrate_data.py       # Import legacy data
│
├── nextjs-frontend/              # Next.js 14+ React frontend
│   ├── app/                      # App Router pages
│   ├── components/               # React components (Chat, Messages, etc.)
│   ├── hooks/                    # Custom hooks (useChat, useDarkMode)
│   ├── lib/                      # API client and utilities
│   ├── types/                    # TypeScript type definitions
│   └── Dockerfile                # Next.js container
│
├── legacy/                       # Old ChatterBot version (for reference)
│
├── templates/                    # Flask HTML templates (Jinja2)
├── static/                       # CSS, JavaScript, images (Flask UI)
├── instance/                     # Database files (created at runtime)
├── scripts/                      # Build scripts (CSS compilation)
│
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── .env                          # Your configuration (API keys, etc.)
├── Dockerfile                    # Flask backend container
├── docker-compose.yml            # Multi-container orchestration
└── nginx.conf                    # Nginx reverse proxy config
```

### The RAG Pipeline (Step by Step)

When you ask a question, here's what happens behind the scenes:

**Step 1: Intent Classification** (~100-200ms)
- **What happens:** A fast AI model analyzes your question
- **Determines:** Question type (prerequisite, advisor lookup, deadline, etc.)
- **Extracts:** Entities (course codes like "CMPE 131", names, dates)
- **Checks:** If context from previous messages is needed
- **Model used:** Claude Haiku, GPT-4o-mini, or Phi-3 (depending on provider)

**Step 2: Context Resolution** (~50ms)
- **What happens:** The conversation manager looks at message history
- **Resolves:** Pronouns like "it", "that", "those" to actual entities
- **Example:** If you asked "What about CMPE 135?" after discussing CMPE 131, it knows you're still talking about prerequisites
- **Maintains:** Conversation state across multiple turns

**Step 3: Vector Retrieval** (~200-500ms)
- **What happens:** Your question is converted into a numerical vector (embedding)
- **Searches:** ChromaDB for semantically similar content
- **Returns:** Top 5 most relevant documents
- **Includes:** Courses, advisors, policies, deadlines
- **Technology:** Cosine similarity search in high-dimensional vector space

**Step 4: Confidence Scoring** (~10ms)
- **What happens:** Multi-factor analysis of the retrieval results
- **Evaluates:**
  - Retrieval quality (how well documents matched)
  - Intent confidence (how clear the question was)
  - Context resolution success
  - Number of relevant documents found
- **Calculates:** Overall confidence score (0.0 to 1.0)
- **Decision:** If confidence < 0.4, triggers human handoff

**Step 5: Response Generation** (~2-3 seconds)
- **What happens:** The main AI model generates an answer
- **Input:** Retrieved documents + your question + conversation context
- **Process:** AI reads documents and crafts a natural language answer
- **Constraint:** Strictly uses only the provided context (no invention)
- **Output:** Formatted response with course cards, lists, or plain text

**Step 6: Human Handoff** (~10ms)
- **What happens:** Quality control check
- **Triggers:**
  - Confidence < 0.4
  - Sensitive topics detected (probation, appeals, personal situations)
  - User explicitly asks for human help
- **Provides:** Advisor contact information and booking links
- **Safety:** Ensures you never get stuck with unhelpful or risky answers

### Database Schema

The system uses SQLite with these main tables:

**Content Tables:**
- **Course**: All CMPE/SE courses with prerequisites, descriptions, units
- **Advisor**: Academic advisors with name ranges they serve (A-C, D-F, etc.)
- **Policy**: Academic policies (enrollment, drops, grades, graduation)
- **Deadline**: Important dates (registration, drops, semester schedules)

**Analytics Tables:**
- **Conversation**: All chat messages for analytics (user questions + bot responses)
- **Feedback**: User ratings (thumbs up/down) and optional comments

**Admin Tables:**
- **AdminUser**: Login credentials for admin interface

**Vector Store:**
- **ChromaDB**: Separate vector database for embeddings (not in SQLite)

---

## Configuration Options

### LLM Provider Selection

HAL supports three AI providers. Choose based on your needs:

| Provider | Best For | Pros | Cons | Cost |
|----------|----------|------|------|------|
| **Claude (Anthropic)** | Production | Highest quality, latest models, excellent reasoning | Requires API key, usage costs | $$ |
| **OpenAI (GPT)** | Production | Widely available, reliable, good performance | Requires API key, usage costs | $$ |
| **Ollama (Local)** | Development/Privacy | Free, private, no API needed, runs locally | Slower, requires powerful hardware | Free |

#### 1. Claude (Anthropic) - Recommended

Best for production deployment with high-quality responses.

**Configuration:**
```bash
# In .env file
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here
```

**Models used:**
- Main model: `claude-opus-4-5` or `claude-sonnet-4`
- Classifier: `claude-3-5-haiku-20241022` (fast, efficient)

**Get API key:** [console.anthropic.com](https://console.anthropic.com)

#### 2. OpenAI (GPT) - Good Alternative

Reliable alternative with wide availability.

**Configuration:**
```bash
# In .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key-here
```

**Models used:**
- Main model: `gpt-4o` or `gpt-4-turbo`
- Classifier: `gpt-4o-mini` (fast, cheap)

**Get API key:** [platform.openai.com](https://platform.openai.com)

#### 3. Ollama (Local) - Best for Privacy

Run everything locally on your computer. No API costs, complete privacy.

**Configuration:**
```bash
# In .env file
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

**Installation:**
1. Download Ollama from [ollama.ai](https://ollama.ai)
2. Install and start the Ollama service
3. Pull models:
   ```bash
   # Main model
   ollama pull llama3.2:latest
   # or
   ollama pull qwen2.5:14b

   # Classifier model
   ollama pull phi3:3.8b
   # or
   ollama pull qwen2.5:3b
   ```

**Models used:**
- Main model: `llama3.2:latest` or `qwen2.5:14b`
- Classifier: `phi3:3.8b` or `qwen2.5:3b`

**Hardware requirements:**
- 16GB+ RAM recommended for 14B models
- 8GB RAM sufficient for smaller models (3B-7B)

### Multi-Model Setup Explained

HAL uses a two-model approach for optimal performance:

```
Question arrives
    ↓
[Fast Classifier Model]  ← Small, optimized for speed (~200ms)
    │
    ├─ Determines question type
    ├─ Extracts entities
    └─ Assesses context needs
    ↓
[Main Model]  ← Powerful, optimized for quality (~2-3s)
    │
    ├─ Generates detailed answer
    ├─ Uses retrieved context
    └─ Formats response
    ↓
Final answer
```

**Why two models?**
- **Speed**: Classifier is fast, handles simple logic quickly
- **Quality**: Main model is powerful, generates high-quality answers
- **Cost**: Classifier is cheaper, reduces API costs
- **Efficiency**: Best of both worlds

---

## Admin Interface

Administrators can access **http://127.0.0.1:5000/admin** to manage HAL.

### Features

**Content Management**
- Add/edit/delete courses with prerequisites
- Manage advisor assignments
- Update academic policies
- Maintain deadline calendars

**Analytics Dashboard**
- View usage statistics (questions per day, popular topics)
- Track satisfaction rates (thumbs up/down ratio)
- Monitor confidence scores over time
- Identify frequently asked questions

**Feedback Analysis**
- AI-powered analysis of user comments
- Identifies common issues and improvement opportunities
- Sentiment analysis of feedback
- Trends over time

**System Monitoring**
- Check scheduled job status
- Verify RAG index health
- Monitor database size
- View system logs

**Data Management**
- Export conversations for analysis
- Download feedback reports
- Backup/restore functionality
- Bulk import/export of content

### Creating an Admin Account

First time setup:

```python
# Start Python shell
python3

# Create admin user
from hal import create_app
from hal.models import db, AdminUser

app = create_app()
with app.app_context():
    admin = AdminUser(username='admin')
    admin.set_password('your-secure-password')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

Then login at http://127.0.0.1:5000/admin with:
- Username: `admin`
- Password: `your-secure-password`

---

## Background Jobs

HAL automatically runs these maintenance tasks:

| Job | Schedule | Purpose | Duration |
|-----|----------|---------|----------|
| **Weekly Feedback Analysis** | Monday 6 AM | Analyzes all user feedback, identifies common issues, generates improvement report | ~5 min |
| **Daily Analytics Aggregation** | Daily 2 AM | Compiles usage statistics, calculates metrics, updates dashboard | ~2 min |
| **RAG Index Health Check** | Every hour | Verifies ChromaDB is accessible, checks index size, validates embeddings | ~30 sec |
| **Weekly Cleanup** | Sunday 3 AM | Removes old conversation data (90+ days), cleans up sessions | ~5 min |

### Managing Jobs

**Via Admin Interface:**
1. Login to admin panel
2. Navigate to "Scheduler" section
3. View job status, next run time, and history
4. Manually trigger jobs if needed

**Via CLI:**
```bash
# View job status
python3 -c "from hal.utils.scheduler import get_scheduler; print(get_scheduler().get_jobs())"

# Manually trigger feedback analysis
python3 -m hal.admin.feedback_analyzer
```

### Customizing Schedule

Edit `hal/utils/scheduler.py` to change job timing:

```python
# Example: Change feedback analysis to daily instead of weekly
scheduler.add_job(
    analyze_feedback,
    'cron',
    day_of_week='*',  # Changed from 'mon' to '*' (daily)
    hour=6,
    minute=0
)
```

---

## Glossary

Technical terms used in this project, explained in simple language:

### A-C

**API (Application Programming Interface)**
- A way for programs to talk to each other
- Example: HAL uses the Claude API to send questions and get responses

**API Key**
- A secret password that lets your application access a service
- Like a membership card for using Claude or OpenAI

**APScheduler**
- A Python library that runs tasks on a schedule
- Like a cron job or scheduled task in Windows

**ChromaDB**
- A vector database for storing and searching embeddings
- The "smart filing system" that finds relevant documents

**Classifier Model**
- A fast AI model that categorizes your question
- Determines if you're asking about courses, advisors, deadlines, etc.

**Confidence Score**
- A number (0.0 to 1.0) showing how confident HAL is about an answer
- Higher = more confident, lower = less confident

**Context Resolution**
- Figuring out what pronouns like "it" or "that" refer to
- Example: "What about CMPE 135?" → knows you mean prerequisites

**Cosine Similarity**
- A mathematical way to measure how similar two vectors are
- Used to find documents that match your question

### D-H

**Docker**
- Software that packages applications with all their dependencies
- Makes it easy to run HAL without installing Python, libraries, etc.

**Docker Compose**
- A tool to run multiple Docker containers together
- Used to run both Flask backend and Next.js frontend

**Embedding**
- Converting text into numbers that represent its meaning
- Allows computers to understand similarity between texts

**Flask**
- A Python web framework for building web applications
- Powers HAL's backend API and server

**Hallucination**
- When an AI invents information that isn't true
- RAG prevents this by only using retrieved documents

**Human Handoff**
- When HAL recognizes it can't help and directs you to a human advisor
- Triggered by low confidence or sensitive topics

### I-N

**Intent Classification**
- Figuring out what type of question you're asking
- Example: "What are prereqs?" → intent is "prerequisite_inquiry"

**LLM (Large Language Model)**
- An AI system trained on vast amounts of text
- Examples: Claude, GPT-4, Llama

**Multi-turn Conversation**
- A conversation with multiple back-and-forth messages
- HAL remembers what was said earlier

**Next.js**
- A React framework for building modern web applications
- Used for HAL's optional modern frontend

### O-R

**Ollama**
- Software for running AI models locally on your computer
- Free, private alternative to cloud APIs

**Pluggable**
- Easily swappable or replaceable
- HAL's LLM providers are pluggable (Claude, OpenAI, or Ollama)

**Prerequisite**
- A course you must complete before taking another course
- Example: CMPE 126 is a prerequisite for CMPE 127

**RAG (Retrieval-Augmented Generation)**
- An AI architecture that retrieves documents before generating answers
- Prevents hallucination and grounds responses in facts

**React**
- A JavaScript library for building user interfaces
- Used in HAL's Next.js frontend

### S-Z

**Semantic Search**
- Searching by meaning rather than exact keywords
- Example: "drop course" finds "withdraw from class"

**Session**
- A temporary storage of your conversation data
- Deleted when you close your browser

**SQLAlchemy**
- A Python library for working with databases
- Used to store courses, advisors, policies, etc.

**SQLite**
- A lightweight database that stores data in a single file
- Used for HAL's main database

**Tailwind CSS**
- A CSS framework for styling web interfaces
- Makes HAL's interface look clean and modern

**TypeScript**
- JavaScript with type checking
- Used in Next.js frontend for better code quality

**Vector**
- A list of numbers representing text meaning
- Example: "CMPE 131" → [0.23, -0.45, 0.67, ...]

**Vector Database**
- A database optimized for storing and searching vectors
- ChromaDB is HAL's vector database

**Vector Retrieval**
- Finding documents with similar vectors to your question
- The "search" step in RAG

---

## Troubleshooting

Common issues and how to fix them:

### Installation Issues

#### "Python 3.13 not supported" / "ChromaDB installation failed"

**Problem:** ChromaDB doesn't work with Python 3.13+

**Solution:**
```bash
# Check Python version
python3 --version

# If 3.13+, install Python 3.11
# macOS with Homebrew:
brew install python@3.11

# Use Python 3.11 for installation
python3.11 -m pip install -r requirements.txt
python3.11 run.py
```

#### "No module named 'hal'"

**Problem:** Python can't find the HAL package

**Solution:**
```bash
# Make sure you're in the project root directory
cd /path/to/HAL-AI-AdvisorBot

# Install in development mode
pip3 install -e .
```

#### "pip install fails" / "Dependency conflicts"

**Problem:** Conflicting package versions

**Solution:**
```bash
# Use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration Issues

#### "No API key found"

**Problem:** HAL can't find your API key

**Solution:**
```bash
# Check .env file exists
ls -la .env

# If not, copy example
cp .env.example .env

# Edit .env and add your key
nano .env  # or use any text editor

# Verify key names match exactly:
# ANTHROPIC_API_KEY (not ANTHROPIC_KEY or CLAUDE_API_KEY)
# OPENAI_API_KEY (not OPENAI_KEY)

# Restart the application
python3 run.py
```

#### "Invalid API key" / "Authentication failed"

**Problem:** API key is incorrect or expired

**Solution:**
1. Verify key is copied correctly (no extra spaces)
2. Check API key is active on provider's dashboard
3. For Claude: Visit [console.anthropic.com](https://console.anthropic.com)
4. For OpenAI: Visit [platform.openai.com](https://platform.openai.com)
5. Regenerate key if necessary

#### "Ollama connection refused"

**Problem:** Ollama service is not running

**Solution:**
```bash
# Check if Ollama is installed
ollama --version

# If not installed, download from ollama.ai

# Start Ollama service
# macOS/Linux: it starts automatically
# Windows: check system tray

# Verify it's running
curl http://localhost:11434/api/tags

# Pull required models
ollama pull llama3.2:latest
ollama pull phi3:3.8b
```

### Runtime Issues

#### "RAG index empty" / "No documents found"

**Problem:** ChromaDB has no data

**Solution:**
```bash
# Run data migration
python3 -m hal.cli.migrate_data

# Verify data was imported
python3 -c "from hal.models import db, Course; from hal import create_app; app = create_app(); app.app_context().push(); print(f'Courses: {Course.query.count()}')"

# If count is 0, check admin interface to add content manually
```

#### "CSS not loading" / "Styles look broken"

**Problem:** Tailwind CSS not compiled

**Solution:**
```bash
# Check if output.css exists
ls -la static/css/output.css

# If not, build CSS
./scripts/build-css.sh build

# If script fails, install Tailwind CLI manually
# macOS Apple Silicon:
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss

# Then run build script
./scripts/build-css.sh build
```

#### Slow responses / Timeout errors

**Problem:** AI model is taking too long

**Solution:**

For Ollama (local):
```bash
# Check model size
ollama list

# If using large model (14B+), switch to smaller one
ollama pull qwen2.5:3b  # Much faster

# Update .env or config.py to use smaller model
```

For Claude/OpenAI:
```bash
# Check internet connection
ping api.anthropic.com

# Verify API key has sufficient credits
# Check dashboard for usage limits

# Try switching to faster model
# Claude: claude-3-5-haiku-20241022
# OpenAI: gpt-4o-mini
```

#### "Database is locked"

**Problem:** SQLite database is being accessed by multiple processes

**Solution:**
```bash
# Stop all running instances
pkill -f "python.*run.py"

# Check for zombie processes
ps aux | grep python

# Remove stale lock files
rm instance/*.db-journal

# Restart application
python3 run.py
```

### Docker Issues

#### "Port already in use"

**Problem:** Port 5000 or 3000 is already taken

**Solution:**
```bash
# Find what's using the port
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or use different port
docker compose down
docker compose up -d

# Or modify docker-compose.yml to use different ports
```

#### "Container keeps restarting"

**Problem:** Application crashes on startup

**Solution:**
```bash
# View container logs
docker compose logs -f backend

# Common issues:
# 1. Missing .env file → create it
# 2. Invalid API key → check .env
# 3. Port conflict → change ports

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### "Cannot connect to Docker daemon"

**Problem:** Docker is not running

**Solution:**
1. Start Docker Desktop (macOS/Windows)
2. Or start Docker service (Linux):
   ```bash
   sudo systemctl start docker
   ```
3. Verify Docker is running:
   ```bash
   docker ps
   ```

### Next.js Frontend Issues

#### "NEXT_PUBLIC_API_URL not defined"

**Problem:** Next.js can't find the backend

**Solution:**
```bash
cd nextjs-frontend

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local

# Restart dev server
npm run dev
```

#### "API calls failing" / "CORS errors"

**Problem:** Cross-origin requests blocked

**Solution:**
1. Ensure Flask backend is running: `python3 run.py`
2. Check Flask has CORS enabled (it should by default)
3. Verify API URL is correct in `.env.local`
4. Check browser console for specific error

#### "Module not found" in Next.js

**Problem:** Missing dependencies

**Solution:**
```bash
cd nextjs-frontend

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Start dev server
npm run dev
```

---

## How to Contribute

We welcome contributions! Here are ways you can help:

### Adding Content

The easiest way to contribute - help expand HAL's knowledge base:

**What to add:**
- More course information (descriptions, prerequisites, units)
- Updated academic policies
- New advisor information
- Current semester deadlines

**How to add:**
1. Login to admin interface: http://127.0.0.1:5000/admin
2. Navigate to the relevant section (Courses, Advisors, etc.)
3. Click "Create" and fill in the form
4. Submit

Or contribute via code:
1. Add data to `legacy/trainingData.py`
2. Run migration: `python3 -m hal.cli.migrate_data`
3. Submit a pull request

### Improving the Code

For developers who want to enhance HAL's functionality:

**Areas to improve:**
- Intent classification patterns (add more question types)
- Confidence scoring algorithm (improve accuracy)
- New features (calendar integration, course planning, etc.)
- Bug fixes
- Performance optimizations

**Development workflow:**
1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test thoroughly (try various questions)
5. Commit with clear messages:
   ```bash
   git commit -m "Add calendar integration feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Submit a pull request on GitHub

### Testing and Feedback

Help us make HAL better by testing and reporting issues:

**What to test:**
- Ask real student questions
- Try edge cases (ambiguous questions, typos, etc.)
- Test on different devices (desktop, mobile, tablet)
- Try different browsers (Chrome, Firefox, Safari)

**How to report issues:**
1. Go to [GitHub Issues](https://github.com/yourusername/HAL-AI-AdvisorBot/issues)
2. Click "New Issue"
3. Provide:
   - What you asked
   - What HAL responded
   - What you expected
   - Screenshots if helpful
4. Submit

**Providing feedback:**
- Use the thumbs up/down in the chat interface
- Add comments explaining what was wrong
- Suggest improvements in GitHub Discussions

### Improving Documentation

Documentation is just as important as code:

**What to improve:**
- Fix typos or unclear explanations
- Add more examples
- Create video tutorials
- Translate to other languages
- Add diagrams or illustrations

**How to contribute:**
1. Edit README.md or other .md files
2. Submit a pull request with changes
3. Explain what you improved in the PR description

### Code Style Guidelines

**Python:**
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions
- Keep functions focused and small

**JavaScript/TypeScript:**
- Use ESLint configuration provided
- Follow React best practices
- Write JSDoc comments
- Use meaningful variable names

**Commit messages:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issue numbers if applicable

---

## Privacy and Data

### What data does HAL store?

**Stored in database:**
- **Conversations**: Questions you ask and answers HAL provides
- **Feedback**: Thumbs up/down ratings and optional comments
- **Session IDs**: Anonymous identifiers to track conversation flow
- **Timestamps**: When questions were asked

**NOT stored:**
- Student names or IDs
- Personal information
- Login credentials (HAL is public, no login required)
- IP addresses
- Browser fingerprints

### How long is data kept?

| Data Type | Retention Period | Reason |
|-----------|------------------|--------|
| Conversations | 90 days | Analytics and improvement |
| Feedback | Indefinitely | Long-term improvement tracking |
| Sessions | Until browser closes | Maintain conversation context |
| Admin logs | 30 days | Security and debugging |

**Automatic cleanup:**
- Weekly job removes conversations older than 90 days
- Session data deleted when you close browser
- No personal data is ever stored

### Can I run HAL completely offline?

**Yes!** For complete privacy:

1. Use Ollama as your LLM provider (local AI)
2. Run HAL on your own computer (not cloud)
3. Don't expose to internet (localhost only)

**Result:**
- All data stays on your machine
- No API calls to external services
- No data sent to Claude, OpenAI, or anyone else
- Complete privacy and control

**Setup:**
```bash
# In .env file
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Run locally
python3 run.py

# Access only from your computer
# http://127.0.0.1:5000
```

### GDPR and Privacy Compliance

**For institutions deploying HAL:**

- Data is stored locally (SQLite database)
- No third-party tracking or analytics
- Easy to export/delete all data
- Clear data retention policies
- Optional offline mode available

**Recommendations:**
1. Add privacy policy page explaining data usage
2. Implement data export feature for users
3. Provide clear opt-out mechanisms
4. Regular security audits
5. Use local Ollama for sensitive deployments

---

## Roadmap

Future enhancements we're considering:

### Short-term (Next 3 months)

- [ ] **Mobile app** - Native iOS/Android apps
- [ ] **Voice interface** - Ask questions via microphone
- [ ] **Calendar integration** - Sync deadlines to Google/Outlook
- [ ] **Email notifications** - Deadline reminders
- [ ] **Improved admin analytics** - More charts and insights

### Medium-term (6 months)

- [ ] **Course planning tool** - Generate semester-by-semester roadmap
- [ ] **Degree audit** - Track progress toward graduation
- [ ] **Multi-language support** - Spanish, Chinese, Vietnamese, etc.
- [ ] **Integration with SJSU systems** - MySJSU, Canvas, PeopleSoft
- [ ] **Personalized recommendations** - Based on academic history

### Long-term (1 year+)

- [ ] **Peer advisor matching** - Connect with upperclassmen
- [ ] **Career guidance** - Job recommendations based on courses
- [ ] **Professor ratings integration** - Link to RateMyProfessors
- [ ] **Study group finder** - Connect students in same classes
- [ ] **Expand to other departments** - Beyond CMPE/SE

**Want to help with any of these?** Check out [Contributing](#how-to-contribute) section!

---

## Credits and Acknowledgments

### Built With

**Backend:**
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Flask-Admin](https://flask-admin.readthedocs.io/) - Admin interface
- [APScheduler](https://apscheduler.readthedocs.io/) - Background jobs

**AI Providers:**
- [Anthropic Claude](https://www.anthropic.com/) - Primary AI model
- [OpenAI GPT](https://openai.com/) - Alternative AI model
- [Ollama](https://ollama.ai/) - Local AI option

**Frontend:**
- [Tailwind CSS](https://tailwindcss.com/) - UI styling
- [Next.js](https://nextjs.org/) - React framework (optional)
- [TypeScript](https://www.typescriptlang.org/) - Type safety (Next.js)

**Infrastructure:**
- [Docker](https://www.docker.com/) - Containerization
- [Nginx](https://www.nginx.com/) - Reverse proxy

### Special Thanks

- **SJSU CMPE/SE Department** - For academic content and support
- **All beta testers** - Students who provided feedback during testing
- **Contributors** - Everyone who helped improve HAL
- **Open source community** - For amazing tools and libraries

---

## License

[Add your license here - e.g., MIT, Apache 2.0, etc.]

---

## Contact and Support

### Get Help

- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/HAL-AI-AdvisorBot/issues)
- **Questions**: Ask in [GitHub Discussions](https://github.com/yourusername/HAL-AI-AdvisorBot/discussions)
- **Email**: [your-email@example.com]

### Community

- **Discord**: [Join our Discord](https://discord.gg/your-invite) (coming soon)
- **Twitter**: [@HAL_AdvisorBot](https://twitter.com/HAL_AdvisorBot) (coming soon)

### For SJSU Students

- **Official SJSU Advising**: [sjsu.edu/advising](https://www.sjsu.edu/advising)
- **CMPE/SE Department**: [sjsu.edu/cmpe](https://www.sjsu.edu/cmpe)

**Important:** HAL is a student project to supplement, not replace, official advising. Always verify important academic decisions with official SJSU resources and advisors.

---

## FAQ

### General Questions

**Q: Is HAL an official SJSU tool?**

A: No, HAL is a student project designed to help SJSU engineering students. It's not affiliated with or endorsed by SJSU. Always verify important academic information with official SJSU resources and advisors.

**Q: Is HAL free to use?**

A: Yes, HAL is open source and free. However, if you're running your own instance, you'll need to pay for AI API usage (Claude or OpenAI) unless you use the free local option (Ollama).

**Q: Can I use HAL for other universities or departments?**

A: Yes! HAL's architecture is flexible. You'd need to:
1. Update the knowledge base (courses, policies, advisors)
2. Modify templates and branding
3. Adjust intent classification for your use case

The core RAG pipeline works for any domain.

### Privacy and Security

**Q: Can HAL access my academic records?**

A: No, HAL has zero access to student records, grades, or personal information. It only provides general academic advising based on public university policies and course catalogs.

**Q: Is my conversation data private?**

A: Conversations are stored anonymously (no personal info) for analytics. For complete privacy, use the local Ollama option which keeps all data on your computer.

**Q: What happens to my data if I close the browser?**

A: Session data (conversation context) is deleted. The actual questions and answers remain in the database for 90 days for analytics, then automatically deleted.

### Technical Questions

**Q: What if HAL gives me wrong information?**

A: While HAL strives for accuracy, AI can make mistakes. Always verify important decisions with your academic advisor. Use the feedback system (thumbs down) to report incorrect answers so we can improve.

**Q: Why does HAL sometimes say "I don't know"?**

A: HAL is designed to be honest about its limitations. When confidence is low or information isn't in the knowledge base, it will admit uncertainty and refer you to human advisors.

**Q: Can I run HAL on my phone?**

A: Yes! The web interface is mobile-responsive. Visit http://your-hal-url from your phone's browser. A native mobile app is on the [roadmap](#roadmap).

**Q: How often is the information updated?**

A: The knowledge base should be updated each semester by administrators. Check the admin interface for the last update date. Out-of-date information is one reason HAL might give incorrect answers.

**Q: Why is HAL slow sometimes?**

A: Response time depends on:
- **AI provider**: Cloud (Claude/OpenAI) is faster than local (Ollama)
- **Model size**: Larger models (14B+) are slower but more accurate
- **Internet speed**: For cloud providers
- **Hardware**: For local Ollama deployment

Typical response times:
- Cloud providers: 2-3 seconds
- Ollama (local, 7B model): 5-10 seconds
- Ollama (local, 14B model): 10-20 seconds

**Q: Can I customize HAL's personality or tone?**

A: Yes! Edit the system prompts in:
- `hal/services/rag_engine.py` (main responses)
- `hal/services/intent_classifier.py` (classification)

You can make HAL more formal, casual, humorous, etc.

**Q: Does HAL support languages other than English?**

A: Not currently, but multi-language support is on the [roadmap](#roadmap). The underlying AI models (Claude, GPT) support many languages, so it's technically feasible.

### Deployment Questions

**Q: Can I deploy HAL to a server for my whole university?**

A: Yes! Use Docker Compose for production deployment:
```bash
docker compose --profile production up -d
```

This includes Nginx reverse proxy and is suitable for multi-user deployment.

**Q: What are the server requirements?**

A: Minimum requirements:
- **CPU**: 2 cores
- **RAM**: 4GB (for cloud AI providers)
- **Disk**: 10GB
- **Network**: Stable internet connection

For local Ollama:
- **CPU**: 4+ cores
- **RAM**: 16GB+ (depending on model size)
- **GPU**: Optional but highly recommended for speed

**Q: How many users can HAL handle?**

A: Depends on your setup:
- **Cloud providers (Claude/OpenAI)**: Scales well, limited by API rate limits
- **Local Ollama**: Limited by hardware, ~10-20 concurrent users on typical server

For large deployments (100+ users), use cloud providers and horizontal scaling.

**Q: Is there a demo I can try without installing?**

A: Watch the [demo video](https://youtu.be/dVwozVz11ho?t=78) to see HAL in action. For hands-on experience, use the [Docker method](#method-1-docker-easiest---no-python-required) - it's the fastest way to get started.

---

**Happy advising!**

*Built with care for SJSU engineering students*

**Ready to get started?** Jump to [Quick Start](#quick-start) to install HAL in minutes!
