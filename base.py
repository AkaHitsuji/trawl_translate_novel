from abc import ABC, abstractmethod
import os
from typing import Dict, List, Optional, Tuple


class BaseNovelTrawler(ABC):
    NOVEL_URL: str

    @abstractmethod
    def get_chapter_titles(self, book_id: str) -> Dict[str, str]:
        """
        Retrieves all the titles of the book and their sub urls
        """
        pass

    @abstractmethod
    def get_chapter(self, book_id: str, chapter_num: str) -> Tuple[str, str]:
        """
        Gets chapter content

        Returns Tuple[chapter title, chapter content]
        """
        pass

    @abstractmethod
    def get_book(
        self,
        book_id: str,
        starting_chapter_num: str = None,
        ending_chapter_num: str = None,
    ) -> Dict[str, str]:
        """
        Gets book within range, defaults to getting full book if starting and ending chapter ids are not provided.

        Returns a dictionary of chapter titles as keys and content as values
        """
        pass


class TextReaderWriter:
    def __init__(self, parent_dir: str) -> None:
        self.parent_dir = parent_dir

    def write_to_file(self, book_title: str, chapter_title: str, content: str):
        filepath = f"{self.parent_dir}/{book_title}/{chapter_title}.txt"
        # to make sure file path exists before writing
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as file:
            file.write(content)
            file.close()

    def get_file_content(self, book_title: str, chapter_num: str) -> Tuple[str, str]:
        """
        Returns (title, content)
        """
        folderpath = f"{self.parent_dir}/{book_title}"
        chapter_titles = os.listdir(folderpath)
        chapter_title = self._get_chapter_title(chapter_num, chapter_titles)
        if not chapter_title:
            raise ValueError(f"chapter number not found in {self.parent_dir}/{book_title} directory")

        chapter_path = f"{folderpath}/{chapter_title}"
        with open(chapter_path) as f:
            content = f.read()
            f.close()
        
        return chapter_title, content

    
    def _get_chapter_title(self, chapter_num: str, chapter_titles: List[str]) -> Optional[str]:
        for title in chapter_titles:
            num = title.split("_")[0]
            if num == chapter_num:
                return title
        return None        

class BaseTranslator(ABC):
    @abstractmethod
    def translate_chapter(self, content) -> str:
        """
        Translates content from chinese to english
        """
        pass