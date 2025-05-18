from typing import Tuple
import logging
from base import BaseTranslator
from browsers.chatgpt_selenium import Handler
from browsers.novelhi_selenium import NovelHiHandler

# Configure logging
logger = logging.getLogger(__name__)


class ChatGPTTranslator(BaseTranslator):
    """
    Translator that uses ChatGPT through a Selenium browser interface.
    """
    
    def __init__(self, username: str, password: str, chat_prompt: str):
        """
        Initialize the ChatGPT translator.
        
        Args:
            username: OpenAI account username
            password: OpenAI account password
            chat_prompt: Initial prompt to send to ChatGPT
        """
        self.openai_handler = Handler(username, password)
        # Initialize the ChatGPT session with the prompt
        answer = self.openai_handler.interact(chat_prompt)
        logger.info(answer)
        logger.info("ChatGPT translator initialized")

    def translate_text(self, text: str) -> str:
        """
        Translate Chinese text to English using ChatGPT.
        
        Args:
            text: Chinese text to translate
            
        Returns:
            Translated English text
        """
        english_text = self.openai_handler.interact(
            self._get_translate_prompt(text)
        )
        return english_text.strip()
        
    def translate_title_and_content(self, chinese_title: str, chinese_content: str) -> Tuple[str, str]:
        """
        Translate both title and content from Chinese to English.
        
        Args:
            chinese_title: Title in Chinese
            chinese_content: Content in Chinese
            
        Returns:
            Tuple of (english_title, english_content)
        """
        english_title = self.translate_text(chinese_title)
        english_content = self.translate_text(chinese_content)
        return english_title, english_content

    def _get_translate_prompt(self, text: str) -> str:
        """
        Format the translation prompt for ChatGPT.
        
        Args:
            text: Text to translate
            
        Returns:
            Formatted prompt
        """
        return f"translate from chinese to english. Only return the text within the dashes:\n---\n{text}\n---"


class NovelHiTranslator(BaseTranslator):
    """
    Translator that uses NovelHi's translation service through a Selenium browser interface.
    """
    
    def __init__(self) -> None:
        """Initialize the NovelHi translator."""
        self.novelhi_handler = NovelHiHandler()

    def translate_text(self, text: str) -> str:
        """
        Translate Chinese text to English using NovelHi.
        
        Args:
            text: Chinese text to translate
            
        Returns:
            Translated English text
        """
        return self.novelhi_handler.translate_text(text)
