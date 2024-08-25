import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class BaseExporter(ABC):
    pass


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
    def __init__(self):
        self.downloaded_dir = "downloaded_books"
        self.translated_dir = "translated_books"

    def write_chapter_to_file(
        self,
        book_title: str,
        chapter_title: str,
        content: str,
        is_downloaded: bool = True,
    ):
        """
        is_downloaded: bool. Determines if should write to downloaded dir or translated dir
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        chapter_title = self._format_chapter_special_char(chapter_title)
        # breakpoint()
        filepath = f"{parent_dir}/{book_title}/{chapter_title}.txt"
        # to make sure file path exists before writing
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as file:
            file.write(content)
            file.close()
        print(f"saved {chapter_title}")

    def save_book_cover(
        self,
        book_title: str,
        image_bytes: bytes,
        is_downloaded: bool = True,
    ):
        """
        is_downloaded: bool. Determines if should write to downloaded dir or translated dir
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        filepath = f"{parent_dir}/{book_title}/cover_image.jpg"
        # to make sure file path exists before writing
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as file:
            file.write(image_bytes)
            file.close()
        print(f"saved cover image")

    def save_book_info(
        self,
        book_title: str,
        book_info: Dict,
        is_downloaded: bool = True,
    ):
        """
        is_downloaded: bool. Determines if should write to downloaded dir or translated dir
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        filepath = f"{parent_dir}/{book_title}/book_info.json"
        # to make sure file path exists before writing
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(book_info, file, ensure_ascii=False, indent=2)
            file.close()

        print(f"saved book info")

    def get_book_titles(
        self,
        book_title: str,
    ) -> List[str]:
        parent_dir = self.downloaded_dir
        folderpath = f"{parent_dir}/{book_title}"
        chapter_titles = os.listdir(folderpath)
        return chapter_titles

    def get_file_content(
        self,
        book_title: str,
        chapter_num: str,
        is_downloaded: bool = True,
    ) -> Tuple[str, str]:
        """
        Returns (title, content)
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir

        folderpath = f"{parent_dir}/{book_title}"
        chapter_titles = os.listdir(folderpath)
        chapter_title = self._get_chapter_title(chapter_num, chapter_titles)
        if not chapter_title:
            raise ValueError(
                f"chapter number not found in {parent_dir}/{book_title} directory"
            )

        chapter_path = f"{folderpath}/{chapter_title}"
        with open(chapter_path) as f:
            content = f.read()
            f.close()

        chapter_title = chapter_title.split(".")[0]
        return chapter_title, content

    def _get_chapter_title(
        self, chapter_num: str, chapter_titles: List[str]
    ) -> Optional[str]:
        for title in chapter_titles:
            num = title.split("_")[0]
            if num == chapter_num:
                return title
        return None

    def _format_chapter_special_char(self, chapter_title: str) -> str:
        return chapter_title.replace("/", "-")


class BaseTranslator(ABC):
    @abstractmethod
    def translate_text(self, content) -> str:
        """
        Translates content from chinese to english
        """
        pass
