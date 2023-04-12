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
            chinese_info = text.split(" ")
            chinese_number = chinese_info[0]
            title = chinese_info[1] if len(chinese_info) == 2 else ""
            chapter_num = self._get_english_chapter_number(chinese_number)

            # fix for nshba chapter discrepancies
            chapter_num = self._fix_chapter_title_discrepancies(
                book_id=book_id,
                chapter_num=chapter_num,
                chapter_subpath=chapter_subpath,
                title=title,
                chinese_number=chinese_number,
            )

            chapters[chapter_num] = {
                "subpath": chapter_subpath,
                "chinese_title": title,
                "chinese_chapter_num": chinese_number,
            }

        # breakpoint()
        self.chapter_titles = chapters
        return self.chapter_titles

    def get_book(
        self,
        book_id: str,
        starting_chapter_num: str = None,
        ending_chapter_num: str = None,
    ) -> Dict[str, str]:
        chapter_titles = self.get_chapter_titles(book_id)
        if (
            starting_chapter_num is not None
            and chapter_titles.get(starting_chapter_num) is None
        ):
            raise ValueError("bad starting chapter number provided")
        if (
            ending_chapter_num is not None
            and chapter_titles.get(ending_chapter_num) is None
        ):
            raise ValueError("bad ending chapter number provided")

        start = int(starting_chapter_num) if starting_chapter_num else 1
        end = (
            int(ending_chapter_num)
            if ending_chapter_num
            else int(list(chapter_titles)[-1])
        )

        book_content = {}
        for chapter_num in range(start, end + 1):
            print(f"retrieving content for chapter {chapter_num}..")
            title, content = self.get_chapter(
                book_id=book_id, chapter_num=str(chapter_num)
            )
            book_content[title] = content
            print(f"retrieved content for title: {title}")

        return book_content

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

    def _fix_chapter_title_discrepancies(
        self, book_id, chapter_num, chapter_subpath, title, chinese_number
    ):
        if book_id == "11992":
            if chapter_num == "4903":
                if len(title) == 2:
                    chapter_num = "4904"
                    print(chapter_num, title)
            elif chapter_num == "6060":
                if len(title) == 4:
                    chapter_num = "5060"
                    print(chapter_num, title)
            elif chapter_num == "6062":
                if len(title) == 3:
                    chapter_num = "5062"
                    print(chapter_num, title)
            elif chapter_num == "6067":
                if len(title) == 4:
                    chapter_num = "5067"
                    print(chapter_num, title)
            elif chapter_num == "437" and len(chinese_number) == 7:
                if len(title) == 4:
                    chapter_num = "5437"
                    print(chapter_num, title)
            elif chapter_num == "5114":
                if chapter_subpath.split(".")[0].split("/")[-1] == "12309969":
                    chapter_num = "5113"
                    print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12332869":
                chapter_num = "5135"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12394674":
                chapter_num = "5237"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12424386":
                chapter_num = "5278"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12441014":
                chapter_num = "5310"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12472439":
                chapter_num = "5365"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] ==  "12491082":
                chapter_num = "5403"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12549943":
                chapter_num = "5461"
                print(chapter_num, title)


                

        return chapter_num