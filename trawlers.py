from typing import Dict, Tuple
import requests
from base import NovelTrawler
from bs4 import BeautifulSoup
from pycnnum import cn2num


class UukanshuNovelTrawler(NovelTrawler):
    NOVEL_URL = "https://uukanshu.cc"

    def __init__(self) -> None:
        self.chapter_titles = None

    def get_chapter_titles(self, book_id: str) -> Dict[str, str]:
        if self.chapter_titles:
            return self.chapter_titles
        
        chapter_list_url = f"{self.NOVEL_URL}/book/{book_id}"
        html = self._get_content(chapter_list_url)
        soup = BeautifulSoup(html, "html.parser")
        chapters = {}
        for dd in soup.find_all("dd"):
            chapter_subpath = dd.a["href"]
            text = dd.a.text
            chinese_info = text.split(' ')
            chinese_number = chinese_info[0]
            title = chinese_info[1] if len(chinese_info) == 2 else ""
            chapter_num = self._get_english_chapter_number(chinese_number)

            chapters[chapter_num] = {
                "subpath": chapter_subpath,
                "chinese_title": title,
                "chinese_chapter_num": chinese_number,
            }

        self.chapter_titles = chapters
        return self.chapter_titles

    def get_book(
        self,
        book_id: str,
        starting_chapter_num: str = None,
        ending_chapter_num: str = None,
    ) -> Dict[str, str]:
        return super().get_book(book_id, starting_chapter_num, ending_chapter_num)

    def get_chapter(self, book_id: str, chapter_num: str) -> Tuple[str, str]:
        chapter_titles = self.get_chapter_titles(book_id)
        chapter_subpath = chapter_titles[chapter_num]["subpath"]
        chinese_title = chapter_titles[chapter_num]["chinese_title"]
        chapter_title = f"{chapter_num}_{chinese_title}"

        content_url = f"{self.NOVEL_URL}{chapter_subpath}"
        # print(content_url)
        html = self._get_content(content_url)
        soup = BeautifulSoup(html, "html.parser")
        text_content = (
            soup.find("p", class_="readcotent bbb font-normal").get_text().strip()
        )

        return chapter_title, text_content

    def _get_content(self, url: str):
        response = requests.get(url)
        return response.content

    def _get_english_chapter_number(self, chinese_numbers) -> str:
        english_numbers = cn2num(chinese_numbers)
        return str(english_numbers)
    