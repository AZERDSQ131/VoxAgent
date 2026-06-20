# VoxAgent

**VoxAgent** is an agentic voice assistant powered entirely by [Mistral AI](https://mistral.ai). It listens to your voice (or reads your typed input), reasons through an LLM, optionally executes bash commands on your machine, and responds out loud — all in one seamless terminal loop.

---

## Features

- **Voice Input** – Press Enter and speak. Recording stops automatically after a short silence.
- **Text Fallback** – Type your query directly instead of speaking.
- **Speech-to-Text** – Powered by Mistral Voxtral (`voxtral-mini-latest`).
- **LLM Reasoning** – Mistral Small (`mistral-small-latest`) decides whether to answer normally or run bash commands.
- **Bash Execution** – The LLM can produce `<bash>...</bash>` tags. VoxAgent executes them safely (allowlist + dangerous-pattern filter) and feeds the output back to the LLM for a spoken summary.
- **Text-to-Speech** – Mistral TTS reads the final response aloud (macOS `afplay`, fallback `say`).
- **Conversation Memory** – Full message history is kept during the session.
- **macOS Optimized** – Uses `afplay` for audio playback and `say` as a fallback TTS engine.

---

## Stack

| Component         | Technology                   |
| ----------------- | ---------------------------- |
| Speech-to-Text    | Mistral Voxtral              |
| Language Model    | Mistral Small (agent + tools)|
| Text-to-Speech    | Mistral TTS + `afplay`       |
| Command Execution | Bash (sandboxed)             |
| Audio I/O         | `sounddevice`, `numpy`       |

---

## Prerequisites

- Python 3.10+
- A [Mistral API key](https://console.mistral.ai)
- macOS (for `afplay`; playback can be adapted to other platforms)
- Working microphone

---

## Installation

```bash
# Clone the repository
git clone https://github.com/AZERDSQ/computer-use.git
cd computer-use

# Set up your API key
cp .env.example .env
# Edit .env and add your Mistral API key:
#   MISTRAL_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
python src/main.py
# or
bash run.sh
```

### Interactive commands

| Action              | Input                        |
| ------------------- | ---------------------------- |
| Speak a query       | Press **Enter** (talk, then silence stops recording) |
| Type a query        | Type your message and press **Enter** |
| Stop the session    | Type `stop`, `quit`, `exit`, or `au revoir` |

### Example session

```
[Enter] Parler  |  [taper] Texte  |  stop/quit:
[Parle maintenant...]
[Enregistrement termine]
[Toi] what files are in the current directory?
[Agent reflechit...]
[Bash] ls -la
[Output] total 32 ...
[Voix] There are 7 items in the current directory including source files, configuration, and documentation.
```

---

## Configuration

All settings live in `src/config.py`:

| Variable              | Default                 | Description                    |
| --------------------- | ----------------------- | ------------------------------ |
| `STT_MODEL`           | `voxtral-mini-latest`   | Speech-to-text model           |
| `LLM_MODEL`           | `mistral-small-latest`  | Language model                 |
| `TTS_MODEL`           | `mistral-tts-latest`    | Text-to-speech model           |
| `LLM_TEMPERATURE`     | `0.3`                   | LLM sampling temperature       |
| `LLM_MAX_TOKENS`      | `1024`                  | Max tokens per LLM response    |
| `BASH_TIMEOUT`        | `30`                    | Bash command timeout (seconds) |
| `RECORDING_TIMEOUT`   | `60`                    | Max recording duration         |
| `SILENCE_THRESHOLD`   | `15`                    | Amplitude threshold for silence detection |

---

## Safety

Bash execution is sandboxed with two layers of protection:

1. **Allowlist** – Only commands in `ALLOWED_COMMANDS` (e.g. `ls`, `cat`, `git`, `python3`, `curl`) can run.
2. **Denylist** – Dangerous patterns (`rm -rf /`, `sudo`, `mkfs`, etc.) are blocked before execution.

---

## Project Structure

```
computer-use/
├── .env.example       # Environment template
├── .gitignore
├── README.md
├── requirements.txt   # mistralai, sounddevice, numpy
├── run.sh             # Convenience launcher
└── src/
    ├── __init__.py
    ├── main.py        # Entry point, app loop, signal handling
    ├── config.py      # All configuration & .env loader
    ├── agent.py       # LLM orchestration, conversation, bash parsing
    ├── executor.py    # Sandboxed bash command execution
    └── voice.py       # Recording (sounddevice), STT, TTS playback
```

---

## Roadmap Ideas

- Persistent conversation history (JSONL / SQLite)
- Web UI (Streamlit or Gradio)
- Multi-turn tool calling (sequential bash, file edits)
- Cross-platform audio playback (Linux `aplay`, Windows `winsound`)
- Docker sandbox for command execution
- Custom tool definitions (e.g. `<python>`, `<search>`)

---

## License

MIT
