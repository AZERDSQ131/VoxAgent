import os

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"

STT_MODEL = "voxtral-mini-latest"
LLM_MODEL = "mistral-small-latest"
TTS_MODEL = "mistral-tts-latest"

STT_LANGUAGE = "fr"
TTS_VOICE = "default"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 1024

BASH_TIMEOUT = 30
RECORDING_TIMEOUT = 60
SILENCE_THRESHOLD = 15

AGENT_SYSTEM_PROMPT = """Tu es un assistant vocal agentique. Tu peux executer des commandes bash.

Regles:
1. Si l'utilisateur demande une action technique, reponds avec une commande bash entre <bash></bash>
2. Si l'utilisateur pose une question ou parle, reponds normalement
3. Apres chaque commande bash executee, analyse le resultat et repond en vocal
4. Si l'utilisateur dit "stop", "arrete", "merci" ou "au revoir", termine la session
5. Reponds toujours dans la langue de l'utilisateur (francais par defaut)
6. Sois concis pour la synthese vocale - max 2-3 phrases"""


def load_env():
    paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env.local"),
    ]
    for env_path in paths:
        env_path = os.path.abspath(env_path)
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, _, value = line.partition("=")
                        if key and value:
                            os.environ[key.strip()] = value.strip().strip("\"'")
            break


load_env()

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
