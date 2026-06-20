import sys
import signal
import time
import threading

from voice import VoiceEngine
from agent import Agent


class VoiceAgentApp:
    def __init__(self):
        self.running = True
        self.voice = VoiceEngine()
        self.agent = Agent()

    def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.voice.speak("Assistant vocal pret. Appuie sur Entree pour parler, ou tape 'stop' pour quitter.")

        while self.running:
            try:
                cmd = input("\n[Entree] Parler  |  [taper] Texte  |  stop/quit: ").strip()

                if not cmd:
                    stop_event = threading.Event()
                    t = threading.Thread(target=self.voice.record, args=(stop_event,))
                    t.start()
                    input("")
                    stop_event.set()
                    t.join()
                    audio = self.voice.audio_data
                    if audio is None:
                        self.voice.speak("Je n'ai pas entendu de son.")
                        continue
                    text = self.voice.transcribe(audio)
                    if not text:
                        self.voice.speak("Je n'ai pas compris.")
                        continue
                    print(f"[Toi] {text}")
                else:
                    text = cmd

                if self.agent.should_stop(text):
                    self.voice.speak("Au revoir !")
                    self.running = False
                    break

                print("[Agent reflechit...]")
                response = self.agent.process(text)
                self.voice.speak(response)

            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n[Erreur] {e}")
                self.voice.speak("Desole, une erreur est survenue.")
                time.sleep(1)

    def _signal_handler(self, signum, frame):
        self.running = False


def main():
    app = VoiceAgentApp()
    app.run()


if __name__ == "__main__":
    main()
