import subprocess
from typing import List
from commandr import Run, command

from base import TextReaderWriter
from translators import ChatGPTTranslator, NovelHiTranslator
from trawlers import UukanshuNovelTrawler

# OPENAI_KEY = hidden_file.OPENAI_KEY
# OPENAI_USERNAME = hidden_file.OPENAI_USERNAME
# OPENAI_PASSWORD = hidden_file.OPENAI_PASSWORD
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

        # to handle translator not being able to take that much text
        contents = _split_content(chinese_content)
    
        english_title = _get_translated_title(chapter_num)
        print(f"retrieved english title: {english_title}, now translating")

        translated_contents: List[str] = []
        for content in contents:
            translated_contents.append(novelhi_translator.translate_text(content))
        english_content = _combine_content(translated_contents)

        print("translated to english, saving to file")
        print(f"english title: {english_title}")
        text_rw.write_to_file(
            book_title=BOOK_TITLE,
            chapter_title=english_title,
            content=english_content,
            is_downloaded=False,
        )
        print(f"translation for chapter: {chapter_num} complete")


@command
def test_split(chapter_num):
    text_rw = TextReaderWriter()
    chinese_title, chinese_content = text_rw.get_file_content(
        book_title=BOOK_TITLE, chapter_num=chapter_num, is_downloaded=True
    )
    print(f"retrieved chinese content {len(chinese_content)}")
    split_contents = _split_content(chinese_content)
    combined_content = _combine_content(split_contents)

@command
def get_titles():
    text_rw = TextReaderWriter()
    titles = text_rw.get_book_titles(BOOK_TITLE)
    titles_text = "\n".join(titles)
    
    subprocess.run("pbcopy", text=True, input=titles_text)
    print(f"retrieved all {len(titles)} titles")

@command
def transform_translated_titles():
    translated_titles = {}
    filepath ="nshba_translated_titles.txt" 
    with open(filepath, "r") as file:
        lines = file.readlines()
        for line in lines:
            details = line.split("_")
            chapter_num = details[0]
            title = details[1].strip() if len(details) > 1 else ""
            title = " ".join([word.capitalize() for word in title.split(" ")])
            final_str = f"{chapter_num}_{title}"
            translated_titles[details[0]] = final_str
        file.close()

    titles = ""
    for i in sorted(translated_titles.keys()):
        titles += (f"{translated_titles[i]}\n")
    with open(filepath, "w") as file:
        file.write(titles)
        file.close()
    # print(translated_titles)

    

def _split_content(content: str) -> List[str]:
    index = len(content)//2

    for i in range(index, len(content)):
        if content[i] == '\n':
            divide_point = i
            break
    
    if not divide_point:
        raise ValueError("Unable to find split point as no new character")
    
    first_half = content[:divide_point+1]
    second_half = content[divide_point:]
    return [first_half, second_half]

def _combine_content(contents: List[str]) -> str:
    combined = ""
    for content in contents:
        combined += content
    
    return combined

def _get_translated_title(chapter_num):
    translated_titles = {}
    filepath ="nshba_translated_titles.txt" 
    with open(filepath, "r") as file:
        lines = file.readlines()
        for line in lines:
            details = line.split("_")
            translated_titles[details[0]] = line.strip()
        file.close()
    
    title = translated_titles.get(str(chapter_num))
    if title is None:
        raise ValueError(f"unable to find {chapter_num} in translated titles")
    return title

if __name__ == "__main__":
    Run()
