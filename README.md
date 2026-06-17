# 🎓 EduMind AI — Multimodal Educational Assistant
### Powered by Ollama — 100% FREE, No API Key Required

A fully-featured AI educational assistant built with **Python + Streamlit + Ollama** that runs entirely on your own computer for free.

---

## ✅ Features
- 💬 **Text Chat** — Ask any question, get clear educational answers
- 🖼 **Image Analysis** — Upload diagrams/photos, AI explains them (needs llava model)
- 🎙 **Voice Input** — Speak your question via browser mic
- 🔊 **Text-to-Speech** — Hear AI answers read aloud
- ✨ **Multimodal** — All features combined
- 🦙 **Ollama Backend** — Free local AI, no API key, no internet needed

---

## 📁 Project Structure

```
edumind_ai/
│
├── app.py                   ← Main entry point (run this)
├── requirements.txt         ← Python dependencies
│
├── pages/
│   ├── text_chat.py         ← Text Q&A mode
│   ├── image_analysis.py    ← Image upload + analysis
│   ├── voice_tts.py         ← Voice input + TTS
│   └── multimodal.py        ← All-in-one mode
│
├── utils/
│   ├── claude_client.py     ← Ollama API calls
│   ├── audio.py             ← TTS + voice widgets
│   └── session.py           ← Session state defaults
│
├── components/
│   └── chat_ui.py           ← Reusable chat UI
│
├── assets/
│   └── style.css            ← Custom theme
│
└── .streamlit/
    └── config.toml          ← Streamlit config
```

---

## 🚀 Complete Setup — Step by Step

### STEP 1 — Install Ollama (the free AI engine)

Go to **https://ollama.com/download** and install for your OS:

**Windows:**
- Download and run the `.exe` installer from ollama.com/download

**macOS:**
- Download `.dmg` from ollama.com/download, OR
- Run: `brew install ollama`

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

### STEP 2 — Start Ollama Server

Open a terminal and run:
```bash
ollama serve
```
Keep this terminal open the entire time you use EduMind AI.

---

### STEP 3 — Download Free AI Models

Open a SECOND terminal and run:

```bash
# For text chat (fast, smart, 2GB)
ollama pull llama3.2

# For image analysis (4GB — needed for Image mode)
ollama pull llava
```

Wait for downloads to complete (depends on internet speed).

**Other great free models:**
```bash
ollama pull mistral      # 4GB — great at reasoning
ollama pull gemma2       # 5GB — excellent for education
ollama pull phi3         # 2GB — lightweight and fast
ollama pull qwen2.5      # 4GB — multilingual
```

---

### STEP 4 — Set Up the Python Project

Open VS Code, navigate to the `edumind_ai` folder, open the terminal (`Ctrl + `` ` ``):

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows:
venv\Scripts\activate

# Activate — macOS/Linux:
source venv/bin/activate

# Install dependencies (no API key needed!)
pip install -r requirements.txt
```

---

### STEP 5 — Run the App

```bash
streamlit run app.py
```

Browser opens at **http://localhost:8501**

---

### STEP 6 — Select Your Model in the Sidebar

- The sidebar shows **Ollama Status: ✅ Running**
- Pick your **Text Model** (e.g. `llama3.2`)
- Pick your **Vision Model** (e.g. `llava`) for image mode
- Choose a **Topic** and **Mode** — start learning!

---

## 🎮 How to Use Each Mode

### 💬 Text Chat
- Type any question and press Enter
- Use quick-start buttons for instant examples
- Change topic in sidebar for focused answers

### 🖼 Image Analysis
- Upload JPG/PNG image on left panel
- Type your question or click a suggested prompt
- Uses `llava` model to see and explain the image

### 🎙 Voice + TTS
- Click **🎙 Click to Speak** widget
- Allow microphone in Chrome/Edge browser
- Speak → copy transcript → send
- Response plays back as audio automatically

### ✨ Multimodal
- Upload image + type/speak question together
- Gets the richest, most detailed response

---

## 🤖 Recommended Models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| `llama3.2` | 2GB | ⚡ Fast | General chat, quick answers |
| `mistral` | 4GB | ⚡ Fast | Reasoning, analysis |
| `gemma2` | 5GB | 🔄 Medium | Education, explanations |
| `phi3` | 2GB | ⚡ Fast | Lightweight, low-RAM devices |
| `llava` | 4GB | 🔄 Medium | **Image analysis** (required) |
| `moondream` | 1.6GB | ⚡ Fast | Images on low-RAM devices |

---

## 🌐 Browser Requirements

| Feature | Browser |
|---------|---------|
| Text, Image, TTS | All browsers |
| Voice Input (mic) | Chrome or Edge only |

---

## 🛠 Troubleshooting

### "Ollama not running" error
```bash
# Start Ollama server in a terminal:
ollama serve
```

### Model not found error
```bash
# Download the model shown in the error, e.g.:
ollama pull llama3.2
ollama pull llava
```

### "ModuleNotFoundError"
```bash
# Make sure venv is active, then:
pip install -r requirements.txt
```

### Voice input not working
- Use **Google Chrome** or **Microsoft Edge**
- Click **Allow** when asked for microphone permission

### App is slow / responses take long
- Use a smaller model: `phi3` or `llama3.2` (2GB)
- Reduce **Max response tokens** in sidebar to 512
- Close other heavy programs to free up RAM

### Port 8501 busy
```bash
streamlit run app.py --server.port 8502
```

---

## 🔧 Quick Commands

```bash
# Start Ollama (keep open)
ollama serve

# List downloaded models
ollama list

# Download a model
ollama pull llama3.2
ollama pull llava

# Activate Python venv — Windows
venv\Scripts\activate

# Activate Python venv — macOS/Linux
source venv/bin/activate

# Run EduMind AI
streamlit run app.py
```

---

Built with ❤️ using Python · Streamlit · Ollama · 100% Free & Local
