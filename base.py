

from abc import ABC, abstractmethod
import os
from typing import Dict


class NovelTrawler(ABC):
    NOVEL_URL: str
    @abstractmethod
    def get_chapter(self, book_id: str, chapter_id: str) -> str:
        pass

    @abstractmethod
    def get_book(self, book_id: str, starting_chapter_id: str = None, ending_chapter_id: str = None) -> Dict[str, str]:
        """
        Gets book within range, defaults to getting full book if starting and ending chapter ids are not provided.

        Returns a dictionary of chapter titles as keys and content as values
        """
        pass

class TextWriter():
    def __init__(self, parent_dir: str) -> None:
        self.parent_dir = parent_dir

    def write_to_file(self, book_title: str,chapter_title: str, content: str):
        filepath = f"{self.parent_dir}/{book_title}/{chapter_title}.txt"
        # to make sure file path exists before writing
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as file:
            file.write(content)
            file.close()
