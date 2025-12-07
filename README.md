# HAL - Your AI Academic Advisor

An intelligent chatbot that helps Computer Engineering (CMPE) and Software Engineering (SE) students at San Jose State University navigate their academic journey. Think of it as having a knowledgeable advisor available 24/7 to answer your questions about courses, prerequisites, deadlines, and academic policies.

**Watch the demo:** [HAL in Action](https://youtu.be/dVwozVz11ho?t=78)

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

#### 2. Vector Database - The Smart Filing System

**What it is:** ChromaDB, a special database that stores information in a way that understands meaning, not just keywords.

**What it means:** When you ask "How do I drop a course?", it understands that's similar to "What's the process for withdrawing from a class?" even though the words are different.

**Why it matters:** You get relevant answers even if you don't use the exact terminology the university uses.

**Real-world analogy:** Like a librarian who knows that "car repair manual" and "automobile maintenance guide" mean the same thing.

#### 3. Intent Classification - The Question Detective

**What it is:** A fast AI model that figures out what type of question you're asking.

**What it means:** HAL quickly determines if you're asking about prerequisites, deadlines, advisors, or something else. This happens in milliseconds before generating the full answer.

**Why it matters:** By understanding your intent, HAL can search more effectively and give better answers.

**Real-world analogy:** Like a receptionist who can route your call to the right department before you finish your sentence.

#### 4. Conversation Context - The Memory System

**What it is:** HAL remembers what you talked about earlier in the conversation.

**What it means:** You can say "What about CMPE 135?" after asking about CMPE 131, and HAL knows you're still talking about prerequisites.

**Why it matters:** You can have a natural conversation without repeating yourself.

**Real-world analogy:** Like talking to a friend who remembers what you said five minutes ago.

#### 5. Confidence Scoring - The Self-Awareness System

**What it is:** HAL evaluates how confident it is about each answer.

**What it means:** HAL considers multiple factors: How well the retrieved documents matched your question, how clear your question was, whether it found enough information, etc.

**Why it matters:** HAL knows its limits. If confidence is low, it tells you to verify with a human advisor.

**Real-world analogy:** Like a knowledgeable friend who says "I'm pretty sure, but double-check with an expert" when they're uncertain.

#### 6. Human Handoff - The Safety Net

**What it is:** A system that recognizes when HAL can't help and smoothly directs you to a human advisor.

**What it means:** For sensitive topics (academic probation), personal situations, or when confidence is very low, HAL provides booking links to speak with a real advisor.

**Why it matters:** You never get stuck with unhelpful answers. HAL knows when you need human expertise.

**Real-world analogy:** Like a store employee who says "Let me get the manager who specializes in this" when a question is beyond their expertise.

#### 7. Pluggable AI Brains

**What it is:** HAL supports three different AI providers: Claude (Anthropic), GPT (OpenAI), and Ollama (local).

**What it means:** The "intelligence" behind HAL can be swapped out. You can use cloud-based AI services or run everything locally on your computer.

**Why it matters:** Flexibility in cost, privacy, and performance. Universities can choose between cloud services or completely private local deployment.

**Real-world analogy:** Like a car that can run on gas, electric, or hybrid - same functionality, different power source.

#### 8. Background Jobs - The Automated Assistant

**What it is:** Scheduled tasks that run automatically without human intervention.

**What it means:** Every week, HAL analyzes user feedback to find common issues. Every day, it checks system health. Every hour, it verifies the knowledge base is working.

**Why it matters:** Continuous improvement and maintenance without manual work.

**Real-world analogy:** Like a night cleaning crew that tidies up the office while everyone's asleep.

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

---

## Quick Start

### Requirements

**Python Version:** 3.10 - 3.12 (3.11 recommended)

> **Important:** Python 3.13+ is not currently supported due to dependency compatibility issues with ChromaDB. Please use Python 3.11 for the best experience.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HAL-AI-AdvisorBot.git
   cd HAL-AI-AdvisorBot
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy the example environment file and edit it with your API keys:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and configure:
   - `LLM_PROVIDER` - Choose: `claude`, `openai`, or `ollama`
   - `ANTHROPIC_API_KEY` - Your Claude API key (if using Claude)
   - `OPENAI_API_KEY` - Your OpenAI API key (if using OpenAI)
   - `OLLAMA_BASE_URL` - URL for local Ollama (if using Ollama)
   - `SECRET_KEY` - Random secret for Flask sessions

4. **Build Tailwind CSS** (for the web interface)

   First-time setup:
   ```bash
   # Download Tailwind CLI (macOS Apple Silicon)
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
   chmod +x tailwindcss-macos-arm64
   mv tailwindcss-macos-arm64 tailwindcss
   ```

   Build CSS:
   ```bash
   ./scripts/build-css.sh build
   ```

   Or for development (auto-rebuild on changes):
   ```bash
   ./scripts/build-css.sh watch
   ```

5. **Run the application**
   ```bash
   python3 run.py
   ```

   Open your browser and go to: **http://127.0.0.1:5000/**

### Using Docker (Easiest Way)

Don't want to install dependencies? Use Docker:

```bash
# Pull the pre-built image
docker pull mfaryan/hal-final

# Run it
docker run -p 5000:5000 mfaryan/hal-final
```

Then visit: **http://127.0.0.1:5000/**

---

## Architecture Deep Dive

For those who want to understand how everything connects:

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Chat + Admin Dashboard)                    │
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
├── legacy/                       # Old ChatterBot version (for reference)
│
├── templates/                    # HTML pages
├── static/                       # CSS, JavaScript, images
├── instance/                     # Database files (created at runtime)
├── scripts/                      # Build scripts (CSS compilation)
│
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
└── .env                          # Your configuration (API keys, etc.)
```

### The RAG Pipeline (Step by Step)

When you ask a question, here's what happens behind the scenes:

**Step 1: Intent Classification** (Fast AI Model)
- Analyzes your question to determine type (prerequisite, advisor lookup, deadline, etc.)
- Extracts entities (course codes, names)
- Checks if context from previous messages is needed
- Takes ~100-200ms with a small, fast model

**Step 2: Context Resolution** (Conversation Manager)
- If you said "What about that course?", it figures out which course you mean
- Resolves pronouns like "it", "that", "those"
- Maintains conversation state across messages

**Step 3: Vector Retrieval** (ChromaDB)
- Converts your question into a numerical representation (embedding)
- Searches the knowledge base for semantically similar content
- Returns the top 5 most relevant documents
- Includes courses, advisors, policies, deadlines

**Step 4: Confidence Scoring** (Multi-Factor Analysis)
- Evaluates retrieval quality (how well docs matched)
- Considers intent confidence (how clear the question was)
- Checks context resolution success
- Calculates overall confidence: 0.0 (no confidence) to 1.0 (very confident)

**Step 5: Response Generation** (Main AI Model)
- Takes retrieved documents as context
- Generates a natural language answer
- Strictly uses only the provided context (no invention)
- Formats response appropriately

**Step 6: Human Handoff** (Quality Control)
- If confidence < 0.4, suggests human advisor
- Detects sensitive topics (academic probation, appeals)
- Recognizes when user explicitly asks for human help
- Provides advisor booking link when needed

### Database Schema

The system uses SQLite with these main tables:

- **Course**: All CMPE/SE courses with prerequisites, descriptions, units
- **Advisor**: Academic advisors with name ranges they serve
- **Policy**: Academic policies (enrollment, drops, grades, graduation)
- **Deadline**: Important dates (registration, drops, semester schedules)
- **Conversation**: All chat messages for analytics
- **Feedback**: User ratings and comments on responses
- **AdminUser**: Login credentials for admin interface

---

## Admin Interface

Administrators can access **http://127.0.0.1:5000/admin** to:

- **Manage Content**: Add/edit/delete courses, advisors, policies, deadlines
- **View Analytics**: See usage patterns, popular questions, satisfaction rates
- **Analyze Feedback**: AI-powered analysis of user feedback to identify issues
- **Monitor System**: Check scheduled jobs, RAG index health, system status
- **Export Data**: Download conversations and feedback for analysis

---

## Configuration Options

### LLM Provider Selection

HAL supports three AI providers:

**1. Claude (Anthropic)** - Recommended for production
- High quality, latest models
- Main model: `claude-opus-4-5` or `claude-sonnet-4`
- Classifier: `claude-3-5-haiku-20241022` (fast)
- Requires: `ANTHROPIC_API_KEY`

**2. OpenAI (GPT)** - Good alternative
- Widely available, reliable
- Main model: `gpt-4o` or `gpt-4-turbo`
- Classifier: `gpt-4o-mini` (fast, cheap)
- Requires: `OPENAI_API_KEY`

**3. Ollama (Local)** - Best for privacy/development
- Runs completely on your computer
- Free, no API costs, full privacy
- Main model: `llama3.2:latest` or `qwen2.5:14b`
- Classifier: `phi3:3.8b` or `qwen2.5:3b`
- Requires: Local Ollama installation

### Multi-Model Setup

HAL uses a two-model approach:

- **Classifier Model** (fast, small): Determines question type (~200ms)
- **Main Model** (powerful, larger): Generates detailed answers (~2-3 seconds)

This combination optimizes both speed and quality.

---

## Background Jobs

HAL automatically runs these maintenance tasks:

| Job | Schedule | Purpose |
|-----|----------|---------|
| **Weekly Feedback Analysis** | Monday 6 AM | Analyzes all user feedback, identifies common issues |
| **Daily Analytics Aggregation** | Daily 2 AM | Compiles usage statistics, calculates metrics |
| **RAG Index Health Check** | Every hour | Verifies knowledge base is accessible |
| **Weekly Cleanup** | Sunday 3 AM | Removes old conversation data (90+ days) |

Administrators can manually trigger jobs via the admin interface.

---

## How to Contribute

We welcome contributions! Here are ways you can help:

### Adding Content
- Add more course information
- Update academic policies
- Add advisor information
- Improve prerequisite data

### Improving the Code
- Enhance intent classification patterns
- Improve confidence scoring algorithms
- Add new features (calendar integration, course planning, etc.)
- Fix bugs

### Testing and Feedback
- Test with real student questions
- Report inaccurate answers
- Suggest new features
- Improve documentation

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## Troubleshooting

### "ChromaDB not working" / "Pulsar client error"
- Make sure you're using Python 3.10-3.12 (not 3.13+)
- Try: `pip install chromadb --upgrade`

### "No API key found"
- Check your `.env` file exists in the project root
- Verify the key names match: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Restart the application after changing `.env`

### "RAG index empty"
- Run data migration: `python3 -m hal.cli.migrate_data`
- Check admin interface to verify content exists

### "CSS not loading" / "Styles look broken"
- Build Tailwind CSS: `./scripts/build-css.sh build`
- Check that `static/css/output.css` exists

### Slow responses
- If using Ollama locally, larger models (14B+) are slower
- Consider using smaller models for development
- Cloud providers (Claude, OpenAI) are typically faster

---

## Privacy and Data

### What data does HAL store?

- **Conversations**: Questions and answers (for analytics)
- **Feedback**: Ratings and optional comments
- **Session IDs**: Anonymous identifiers (no personal info)

### What data does HAL NOT store?

- Student names or IDs
- Personal information
- Login credentials (HAL is public, no login required)

### How long is data kept?

- Conversations: 90 days (automatic cleanup)
- Feedback: Indefinitely (for improvement)
- Session data: Until browser session ends

### Can I run HAL completely offline?

Yes! Use Ollama as your LLM provider and all AI processing happens locally on your computer. No data leaves your machine.

---

## Roadmap

Future enhancements we're considering:

- [ ] Course planning tool (semester-by-semester roadmap)
- [ ] Calendar integration (sync deadlines to Google/Outlook)
- [ ] Multi-language support (Spanish, Chinese, etc.)
- [ ] Voice interface (ask questions via microphone)
- [ ] Mobile app (iOS/Android)
- [ ] Integration with official SJSU systems
- [ ] Personalized recommendations based on academic history
- [ ] Peer advisor matching (connect with upperclassmen)

---

## Credits and Acknowledgments

**Built with:**
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Anthropic Claude](https://www.anthropic.com/) - AI model (primary)
- [OpenAI GPT](https://openai.com/) - AI model (alternative)
- [Ollama](https://ollama.ai/) - Local AI (privacy option)
- [Tailwind CSS](https://tailwindcss.com/) - UI styling
- [Flask-Admin](https://flask-admin.readthedocs.io/) - Admin interface
- [APScheduler](https://apscheduler.readthedocs.io/) - Background jobs

**Special thanks to:**
- SJSU CMPE/SE Department for academic content
- All students who provided feedback during testing
- Contributors who helped improve HAL

---

## License

[Add your license here - e.g., MIT, Apache 2.0, etc.]

---

## Contact and Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/HAL-AI-AdvisorBot/issues)
- **Questions**: Open a [Discussion](https://github.com/yourusername/HAL-AI-AdvisorBot/discussions)
- **Email**: [your-email@example.com]

---

## FAQ

**Q: Is HAL an official SJSU tool?**
A: HAL is a student project designed to help SJSU engineering students. Always verify important academic information with official SJSU resources and advisors.

**Q: Can HAL access my academic records?**
A: No, HAL has no access to student records, grades, or personal information. It only provides general academic advising based on public university policies.

**Q: What if HAL gives me wrong information?**
A: While HAL strives for accuracy, always verify important decisions with your academic advisor. Use the feedback system to report incorrect answers so we can improve.

**Q: Can I use HAL for other departments?**
A: HAL is currently designed for CMPE/SE students. However, the system could be adapted for other departments by updating the knowledge base.

**Q: Is my conversation data private?**
A: Conversations are stored anonymously (no personal info) for analytics. If using Ollama locally, all data stays on your computer. For cloud providers, standard API privacy policies apply.

**Q: How often is the information updated?**
A: The knowledge base should be updated each semester. Administrators can update policies, courses, and deadlines through the admin interface.

---

**Happy advising! 🎓**

*Built with care for SJSU engineering students*
