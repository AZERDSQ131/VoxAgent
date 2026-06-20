import re
from mistralai import Mistral

from config import (
    MISTRAL_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    AGENT_SYSTEM_PROMPT,
)
from executor import Executor


class Agent:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY non definie")
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.executor = Executor()
        self.messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        ]

    def process(self, user_text):
        self.messages.append({"role": "user", "content": user_text})

        res = self.client.chat.complete(
            model=LLM_MODEL,
            messages=self.messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )

        content = res.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": content})

        bash_cmds = re.findall(r"<bash>(.*?)</bash>", content, re.DOTALL)

        if bash_cmds:
            all_outputs = []
            for cmd in bash_cmds:
                cmd = cmd.strip()
                print(f"[Bash] {cmd}")
                output = self.executor.execute(cmd)
                print(f"[Output] {output[:200]}")
                all_outputs.append(f"Commande: {cmd}\nResultat: {output}")

            summary_prompt = (
                "Voici les resultats des commandes bash executees:\n\n"
                + "\n\n".join(all_outputs)
                + "\n\nFais un resume vocal court (2-3 phrases) pour l'utilisateur."
            )

            self.messages.append({"role": "user", "content": summary_prompt})

            res2 = self.client.chat.complete(
                model=LLM_MODEL,
                messages=self.messages,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )

            summary = res2.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": summary})
            return summary

        return content

    def should_stop(self, text):
        stop_words = ["stop", "arrete", "arrête", "au revoir", "merci c'est tout",
                      "c'est tout", "termine", "fin", "quit", "exit"]
        return any(word in text.lower() for word in stop_words)
