# VoxAgent

Assistant vocal agentique — parle, execute des commandes bash, ecoute la reponse.

## Stack

- **STT** : Mistral Voxtral
- **LLM** : Mistral Small (agent + tool use)
- **TTS** : Mistral TTS
- **Execution** : bash (sandboxe)

## Usage

```bash
cp .env.example .env
# edite .env avec ta clé API Mistral
pip install -r requirements.txt
python src/main.py
```

Appuie sur **Entree** pour parler, ou tape directement ton texte.
