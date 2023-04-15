from typing import Tuple

from base import BaseTranslator
from chatgpt_selenium import Handler


class ChatGPTTranslator(BaseTranslator):
    def __init__(self, username: str, password: str, chat_prompt: str):
        self.openai_handler = Handler(username, password)
        # give prompt to start openai handler
        answer = self.openai_handler.interact(chat_prompt)
        print(answer)
        print("--chatbot initialised--")

    def translate_chapter(self, chinese_title, chinese_content) -> Tuple[str, str]:
        """
        Returns translated (title, content)
        """
        # subprocess.run("pbcopy", text=True, input=prompt)

        english_title = self.openai_handler.interact(
            self._get_translate_prompt(chinese_title)
        )
        english_content = self.openai_handler.interact(
            self._get_translate_prompt(chinese_content)
        )

        return english_title.strip(), english_content

    def _get_translate_prompt(self, text: str) -> str:
        return f"translate from chinese to english. Only return the text within the dashes:\n---\n{text}\n---"
        # return text
