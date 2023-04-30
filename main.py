from commandr import Run, command

import hidden_file
from base import TextReaderWriter
from translators import ChatGPTTranslator, NovelHiTranslator
from trawlers import UukanshuNovelTrawler

OPENAI_KEY = hidden_file.OPENAI_KEY
OPENAI_USERNAME = hidden_file.OPENAI_USERNAME
OPENAI_PASSWORD = hidden_file.OPENAI_PASSWORD
BOOK_ID = 11992  # nine star hegemon book key
STARTING_CHAPTER_ID = 7392047

# temp vars
BOOK_TITLE = "nshba"


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
    text_writer = TextReaderWriter()

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
    text_writer = TextReaderWriter()

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
    text_rw = TextReaderWriter()
    chinese_title, chinese_content = text_rw.get_file_content(
        book_title=BOOK_TITLE, chapter_num=chapter_num, is_downloaded=True
    )
    print(f"retrieved chinese content {len(chinese_content)}")
    novelhi_translator = NovelHiTranslator()
    english_title = novelhi_translator.translate_text(chinese_title).strip()
    english_content = novelhi_translator.translate_text(chinese_content)
    print("translated to english, saving to file")
    text_rw.write_to_file(
        book_title=BOOK_TITLE,
        chapter_title=f"{chapter_num}_{english_title}",
        content=english_content,
        is_downloaded=False,
    )
    print("translation complete")


@command
def translate_chapters(starting_chapter_num=None, ending_chapter_num=None):
    if starting_chapter_num is None or ending_chapter_num is None:
        raise ValueError("starting or ending chapter number needs to be provided")

    text_rw = TextReaderWriter()
    novelhi_translator = NovelHiTranslator()
    for chapter_num in range(int(starting_chapter_num), int(ending_chapter_num) + 1):
        print(f"processing chapter: {chapter_num}..")
        chinese_title, chinese_content = text_rw.get_file_content(
            book_title=BOOK_TITLE, chapter_num=str(chapter_num), is_downloaded=True
        )
        print(f"retrieved chinese content {len(chinese_content)}")

        english_title = novelhi_translator.translate_text(chinese_title)
        english_title = f"{chapter_num}_{english_title}"
        english_content = novelhi_translator.translate_text(chinese_content)

        print("translated to english, saving to file")
        print(f"english title: {english_title}")
        text_rw.write_to_file(
            book_title=BOOK_TITLE,
            chapter_title=english_title,
            content=english_content,
            is_downloaded=False,
        )
        print(f"translation for chapter: {chapter_num} complete")


if __name__ == "__main__":
    Run()
