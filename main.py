from base import TextReaderWriter

import hidden_file
from commandr import Run, command
from translators import ChatGPTTranslator
from trawlers import UukanshuNovelTrawler


OPENAI_KEY = hidden_file.OPENAI_KEY
OPENAI_USERNAME = hidden_file.OPENAI_USERNAME
OPENAI_PASSWORD = hidden_file.OPENAI_PASSWORD
BOOK_ID = 11992  # nine star hegemon book key
STARTING_CHAPTER_ID = 7392047

# temp vars
BOOK_TITLE = "nshba"
DOWNLOADED_BOOKS_DIR = "downloaded_books"


class NovelTranslater:
    def __init__(self, translater_api_key: str):
        self.translater_api_key = translater_api_key


@command
def get_chapter(book_id, chapter_num):
    uukanshu_trawler = UukanshuNovelTrawler()
    title, content = uukanshu_trawler.get_chapter(
        book_id=str(book_id), chapter_num=str(chapter_num)
    )
    print(content)
    print(title)


@command
def get_and_save_book(book_id, starting_chapter_num=None, ending_chapter_num=None):
    print(starting_chapter_num, ending_chapter_num)
    uukanshu_trawler = UukanshuNovelTrawler()
    text_writer = TextReaderWriter(parent_dir=DOWNLOADED_BOOKS_DIR)

    chapter_titles = uukanshu_trawler.get_chapter_titles(book_id)
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
        int(ending_chapter_num) if ending_chapter_num else int(list(chapter_titles)[-1])
    )

    for chapter_num in range(start, end + 1):
        print(f"retrieving content for chapter {chapter_num}..")
        title, content = uukanshu_trawler.get_chapter(
            book_id=book_id, chapter_num=str(chapter_num)
        )
        print(f"retrieved content for title: {title}")

        text_writer.write_to_file(
            book_title=BOOK_TITLE, chapter_title=title, content=content
        )
        print(f"saved {title}")


@command
def save_chapter(book_id, chapter_num):
    uukanshu_trawler = UukanshuNovelTrawler()
    text_writer = TextReaderWriter(parent_dir=DOWNLOADED_BOOKS_DIR)

    title, content = uukanshu_trawler.get_chapter(
        book_id=str(book_id), chapter_num=str(chapter_num)
    )
    text_writer.write_to_file(
        book_title=BOOK_TITLE, chapter_title=title, content=content
    )


@command
def get_chapter_titles(book_id):
    uukanshu_trawler = UukanshuNovelTrawler()
    uukanshu_trawler.get_chapter_titles(book_id)


@command
def translate_chapter(chapter_num):
    text_rw = TextReaderWriter(parent_dir=DOWNLOADED_BOOKS_DIR)
    chinese_title, chinese_content = text_rw.get_file_content(
        book_title=BOOK_TITLE, chapter_num=chapter_num
    )
    print(f"retrieved chinese content {len(chinese_content)}")

    chatgpt_translator = ChatGPTTranslator(
        username=OPENAI_USERNAME, password=OPENAI_PASSWORD
    )
    english_translation = chatgpt_translator.translate_chapter(chinese_content=chinese_content)
    print("translated to english, saving to file")
    text_rw.write_to_file(
        book_title=BOOK_TITLE, 
        chapter_title=f"translated_{chinese_title}", 
        content=english_translation
    )
    print("translation complete")


if __name__ == "__main__":
    Run()
