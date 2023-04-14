import subprocess
import openai

from base import BaseTranslator
from chatgpt_selenium import Handler


class ChatGPTTranslator(BaseTranslator):
    def __init__(self, username: str, password: str):
        self.openai_handler = Handler(username, password)
        # give prompt to start openai handler
        answer = self.openai_handler.interact(
            "I will be providing you with chinese webnovel chapters, you will respond with the english translation of the chinese webnovel chapter. Give me your best translation while retaining the tone and writing style of this chinese martial novel. Are you ready?"
        )
        print(answer)
        print("--chatbot initialised--")

    def translate_chapter(self, chinese_content) -> str:
        prompt = (
            f"translate novel from chinese to english: \n```\n{chinese_content}\n```"
        )
        # subprocess.run("pbcopy", text=True, input=prompt)

        english_translation = self.openai_handler.interact(f"{prompt}")

        return english_translation
