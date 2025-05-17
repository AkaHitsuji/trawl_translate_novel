import json
import os
from abc import ABC, abstractmethod
import re
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


class BaseTranslator(ABC):
    @abstractmethod
    def translate_text(self, text: str) -> str:
        """
        Translates text from one language to another
        
        Returns the translated text
        """
        pass


class TextReaderWriter:
    """
    Handles reading and writing text files for books, chapters, covers, and metadata.
    Manages file organization for both downloaded and translated content.
    """
    COVER_IMAGE_FILENAME = "cover_image.jpg"
    BOOK_INFO_FILENAME = "book_info.json"

    def __init__(self, book_title: str):
        self.downloaded_dir = "downloaded_books"
        self.translated_dir = "translated_books"
        self.book_title = book_title

    def write_chapter_to_file(
        self,
        book_title: str,
        chapter_title: str,
        content: str,
        is_downloaded: bool = True,
    ) -> None:
        """
        Write chapter content to a file.
        
        Args:
            book_title: Title of the book
            chapter_title: Title of the chapter
            content: Chapter content to write
            is_downloaded: Whether to write to downloaded dir (True) or translated dir (False)
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        chapter_title = self._format_chapter_special_char(chapter_title)
        filepath = f"{parent_dir}/{book_title}/{chapter_title}.txt"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Saved {chapter_title}")
        except IOError as e:
            print(f"Error saving chapter {chapter_title}: {str(e)}")

    def save_book_cover(
        self,
        book_title: str,
        image_bytes: bytes,
        is_downloaded: bool = True,
    ) -> bool:
        """
        Save book cover image.
        
        Args:
            book_title: Title of the book
            image_bytes: Cover image as bytes
            is_downloaded: Whether to write to downloaded dir (True) or translated dir (False)
            
        Returns:
            bool: True if successful, False otherwise
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        filepath = f"{parent_dir}/{book_title}/{self.COVER_IMAGE_FILENAME}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "wb") as file:
                file.write(image_bytes)
            print("Saved cover image")
            return True
        except IOError as e:
            print(f"Error saving cover image: {str(e)}")
            return False

    def save_book_info(
        self,
        book_title: str,
        book_info: Dict,
        is_downloaded: bool = True,
    ) -> bool:
        """
        Save book information as JSON.
        
        Args:
            book_title: Title of the book
            book_info: Dictionary of book metadata
            is_downloaded: Whether to write to downloaded dir (True) or translated dir (False)
            
        Returns:
            bool: True if successful, False otherwise
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        filepath = f"{parent_dir}/{book_title}/{self.BOOK_INFO_FILENAME}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(book_info, file, ensure_ascii=False, indent=2)
            print("Saved book info")
            return True
        except IOError as e:
            print(f"Error saving book info: {str(e)}")
            return False

    def get_book_titles(self, order_key: Optional[str] = None) -> List[str]:
        """
        Get all chapter titles for a book.
        
        Args:
            order_key: Optional regex pattern to extract chapter numbers for ordering
            
        Returns:
            List of chapter filenames
        """
        parent_dir = self.downloaded_dir
        folderpath = f"{parent_dir}/{self.book_title}"
        
        try:
            chapter_titles = os.listdir(folderpath)
        except FileNotFoundError:
            print(f"Book directory not found: {folderpath}")
            return []

        # Remove non-chapter files
        chapter_titles = [
            f for f in chapter_titles
            if f not in [self.COVER_IMAGE_FILENAME, self.BOOK_INFO_FILENAME]
        ]

        # Order titles if order_key is provided
        if order_key:
            def extract_chapter_number(title):
                match = re.search(rf"{order_key}", title)
                return int(match.group(1)) if match else 0

            chapter_titles = sorted(chapter_titles, key=extract_chapter_number)

        return chapter_titles

    def get_chapter_content(
        self,
        chapter_path: str,
        is_downloaded: bool = True,
    ) -> Tuple[str, str]:
        """
        Get chapter content from a file.
        
        Args:
            chapter_path: Path to the chapter file relative to the book directory
            is_downloaded: Whether to read from downloaded dir (True) or translated dir (False)
            
        Returns:
            Tuple of (chapter_title, content)
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        folderpath = f"{parent_dir}/{self.book_title}"
        filepath = f"{folderpath}/{chapter_path}"
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            chapter_title = chapter_path.split(".")[0]
            return chapter_title, content
        except IOError as e:
            print(f"Error reading chapter {chapter_path}: {str(e)}")
            return chapter_path.split(".")[0], ""

    def get_info_and_cover(
        self,
        is_downloaded: bool = True,
    ) -> Tuple[Optional[bytes], Dict]:
        """
        Get book cover image and info.
        
        Args:
            is_downloaded: Whether to read from downloaded dir (True) or translated dir (False)
            
        Returns:
            Tuple of (cover_image_bytes, book_info_dict)
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        folderpath = f"{parent_dir}/{self.book_title}"
        
        # Get cover image
        cover_image_content = None
        cover_image_path = f"{folderpath}/{self.COVER_IMAGE_FILENAME}"
        try:
            with open(cover_image_path, "rb") as f:
                cover_image_content = f.read()
        except FileNotFoundError:
            print(f"Cover image not found at {cover_image_path}")
        except IOError as e:
            print(f"Error reading cover image: {str(e)}")
        
        # Get book info
        book_info = {}
        book_info_path = f"{folderpath}/{self.BOOK_INFO_FILENAME}"
        try:
            with open(book_info_path, "r", encoding="utf-8") as f:
                book_info = json.load(f)
        except FileNotFoundError:
            print(f"Book info not found at {book_info_path}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in book info file: {book_info_path}")
        except IOError as e:
            print(f"Error reading book info: {str(e)}")

        return cover_image_content, book_info

    def get_file_content(
        self,
        book_title: str,
        chapter_num: str,
        is_downloaded: bool = True,
    ) -> Tuple[str, str]:
        """
        Get content from a specific chapter file by chapter number.
        
        Args:
            book_title: Title of the book
            chapter_num: Chapter number to retrieve
            is_downloaded: Whether to read from downloaded dir (True) or translated dir (False)
            
        Returns:
            Tuple of (chapter_title, content)
        """
        parent_dir = self.downloaded_dir if is_downloaded else self.translated_dir
        folderpath = f"{parent_dir}/{book_title}"
        
        try:
            chapter_titles = os.listdir(folderpath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Book directory not found: {folderpath}")
        
        chapter_title = self._get_chapter_title(chapter_num, chapter_titles)
        if not chapter_title:
            raise ValueError(f"Chapter number {chapter_num} not found in {folderpath}")

        chapter_path = f"{folderpath}/{chapter_title}"
        try:
            with open(chapter_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            chapter_title = chapter_title.split(".")[0]
            return chapter_title, content
        except IOError as e:
            raise IOError(f"Error reading chapter {chapter_title}: {str(e)}")

    def _get_chapter_title(
        self, chapter_num: str, chapter_titles: List[str]
    ) -> Optional[str]:
        """
        Find the matching chapter title for a chapter number.
        
        Args:
            chapter_num: Chapter number to find
            chapter_titles: List of chapter titles to search
            
        Returns:
            Matching chapter title or None if not found
        """
        for title in chapter_titles:
            num = title.split("_")[0]
            if num == chapter_num:
                return title
        return None

    def _format_chapter_special_char(self, chapter_title: str) -> str:
        """
        Format chapter title to be safe for filenames.
        
        Args:
            chapter_title: Original chapter title
            
        Returns:
            Sanitized chapter title
        """
        # Replace problematic characters with safe alternatives
        return chapter_title.replace("/", "-").replace(":", "_").replace("?", "")
