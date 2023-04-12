
from typing import Dict
import requests
from base import NovelTrawler
from bs4 import BeautifulSoup


class UukanshuNovelTrawler(NovelTrawler):
    NOVEL_URL = "https://uukanshu.cc"

    def get_book(self, book_id: str, starting_chapter_id: str = None, ending_chapter_id: str = None) -> Dict[str, str]:
        return super().get_book(book_id, starting_chapter_id, ending_chapter_id)
    
    def get_chapter(self, book_id: str, chapter_id: str) -> str:
        html = self._get_content(book_id, chapter_id)
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.find('p', class_='readcotent bbb font-normal').get_text().strip()

        print(text_content)
        return text_content

    def _get_content(self, book_id: str, chapter_id: str):
        content_url = f"{self.NOVEL_URL}/book/{book_id}/{chapter_id}.html"
        response = requests.get(content_url)
        return response.content