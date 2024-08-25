import os
import re
from typing import Dict, Optional, Tuple
import requests
from base import BaseNovelTrawler
from bs4 import BeautifulSoup
from pycnnum import cn2num


class UukanshuNovelTrawler(BaseNovelTrawler):
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
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12491082":
                chapter_num = "5403"
                print(chapter_num, title)
            elif chapter_subpath.split(".")[0].split("/")[-1] == "12549943":
                chapter_num = "5461"
                print(chapter_num, title)

        return chapter_num


class NovelFullTrawler(BaseNovelTrawler):
    NOVEL_URL = "https://novelfull.com"

    def __init__(self) -> None:
        self.chapter_titles = None

    def get_book_cover(self, book_id: str) -> Optional[bytes]:
        homepage = f"{self.NOVEL_URL}/{book_id}.html"

        html = self._get_content(homepage)
        soup = BeautifulSoup(html, "html.parser")
        img_tag = soup.find("div", class_="book").find("img")

        img_url = img_tag["src"]
        full_img_url = os.path.join(self.NOVEL_URL, img_url.lstrip("/"))

        response = requests.get(full_img_url)
        if response.status_code != 200:
            # raise ValueError("Unable to download cover image")
            return None

        return response.content

    def get_chapter_titles(self, book_id: str) -> Dict[str, str]:
        if self.chapter_titles:
            return self.chapter_titles

        chapter_list_url = f"{self.NOVEL_URL}/{book_id}.html"

        html = self._get_content(chapter_list_url)
        full_chapter_list = []
        should_go_next = True

        next_page_url = f"/{book_id}.html"
        while should_go_next:
            html = self._get_content(f"{self.NOVEL_URL}{next_page_url}")
            chapters = self.get_partial_chapters(html)
            full_chapter_list = full_chapter_list + chapters
            next_page_url = self.get_next_page_url(html)
            print(
                f"next page found, url: {next_page_url}, chapters found: {len(full_chapter_list)}"
            )
            if next_page_url is None:
                should_go_next = False

        self.chapter_titles = {
            str(index + 1): {
                "subpath": item["url"],
                "title": item["title"],
                "chapter_number": str(index + 1),
            }
            for index, item in enumerate(full_chapter_list)
        }
        return self.chapter_titles

    def get_partial_chapters(self, html_content) -> Dict[str, str]:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all <a> tags within <ul class="list-chapter">
        chapter_links = soup.select("ul.list-chapter a[href]")
        chapters = []

        for link in chapter_links:
            href = link["href"]
            title = link.get("title", "")

            # Clean the chapter title to remove Unicode characters
            cleaned_title = re.sub(r"[^\x00-\x7F]+", "", title).strip()

            chapters.append({"url": href, "title": cleaned_title})

        return chapters

    def get_next_page_url(self, html_content) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the <li> tag with class 'next'
        next_page_li = soup.find("li", class_="next")

        if next_page_li:
            # Find the <a> tag inside this <li>
            next_page_a = next_page_li.find("a", href=True)

            if next_page_a:
                # Extract the href attribute
                next_page_url = next_page_a["href"]
                return next_page_url
        return None

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
        chapter_title = chapter_titles[chapter_num]["title"]

        content_url = f"{self.NOVEL_URL}{chapter_subpath}"

        html = self._get_content(content_url)
        soup = BeautifulSoup(html, "html.parser")

        content_div = soup.find("div", {"class": "chapter container"})

        chapter_content = self._get_text_with_line_breaks(content_div)
        chapter_content = chapter_content.strip()

        return chapter_title, chapter_content

    def _get_text_with_line_breaks(self, soup) -> str:
        # Find all block-level elements
        block_elements = soup.find_all(["p", "h3"])

        text_output = []

        for element in block_elements:
            text = element.get_text(separator="\n", strip=True)
            text_output.append(text)

        # Join the block texts with two new lines to preserve paragraph separation
        return "\n\n".join(text_output)

    def _get_text_without_line_breaks(self, soup) -> str:
        return soup.get_text().strip()

    def _get_content(self, url: str):
        response = requests.get(url)
        return response.content
