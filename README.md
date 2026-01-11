# Simple LLM System - Interview

Simple and straightforward system to execute multiple LLMs (OpenAI, Claude, Gemini, HuggingFace) dynamically.

## 🚀 Quick Setup

```bash
# 1. Configure API keys
cp .env.example .env
# Edit .env with your keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test
python run_llm.py --list
```

## 📖 Usage

### Basic
```bash
# Use OpenAI
python run_llm.py --llm openai --prompt "Your question here"

# Use Claude
python run_llm.py --llm claude --prompt "Your question here"

# Use Gemini
python run_llm.py --llm gemini --prompt "Your question here"
```

### From file
```bash
python run_llm.py --llm openai --prompt-file prompts/qa_basic.txt
```

### With system prompt
```bash
python run_llm.py --llm claude --prompt "Question" --system "You are a Python expert"
```

## 📁 Structure

```
lab_prompts/
├── run_llm.py              # Main script
├── COMANDOS.md             # Detailed command guide
├── .env                    # API keys (gitignored)
├── .env.example            # Template
├── requirements.txt        # Dependencies
├── llms/                   # Implemented providers
│   ├── base.py             # Base interface
│   ├── openai_llm.py       # OpenAI
│   ├── claude.py           # Anthropic
│   ├── gemini.py           # Google
│   └── huggingface.py      # HuggingFace
└── prompts/                # Organized prompts
    ├── qa_basic.txt
    ├── code_review.txt
    └── tech_comparison.txt
```

## 🎯 For Interview

### Demo 1: Switch LLMs dynamically
```bash
# Same question, different LLMs
python run_llm.py --llm openai --prompt "Explain SOLID"
python run_llm.py --llm claude --prompt "Explain SOLID"
```

### Demo 2: Organized prompts
```bash
# Use specialized prompts
python run_llm.py --llm claude --prompt-file prompts/code_review.txt
```

### Demo 3: Custom system prompts
```bash
python run_llm.py --llm openai --prompt "Review this code" --system "You are a security expert"
```

## 💡 Features

- ✅ **Simple**: One script, one command
- ✅ **Flexible**: Switch LLM with one parameter
- ✅ **Organized**: Prompts in separate files
- ✅ **Extensible**: Easy to add new LLMs
- ✅ **Professional**: Based on SOLID principles

## 🔑 Environment Variables

```bash
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
GOOGLE_API_KEY=your-key
HF_TOKEN=your-token
```

## 📚 Documentation

See [COMANDOS.md](COMANDOS.md) for complete usage guide.

## 🛠️ Troubleshooting

### API key error
Check that `.env` has the keys configured.

### Import error
Execute from project root:
```bash
cd D:\lab_provectus
python run_llm.py --list
```

### Module not found
```bash
pip install -r requirements.txt
```

## 📝 Notes

- Providers (llms/) are already implemented
- You only need to configure API keys
- You can modify prompts during interview (they allow you to use AI)
- System designed to be simple and demonstrable

---

**Interview ready - Simple and professional system** 🎯
