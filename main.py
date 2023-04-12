import requests
import json
from bs4 import BeautifulSoup
import openai
from base import TextWriter

import hidden_file
from commandr import Run, command
from trawlers import UukanshuNovelTrawler

OPENAI_KEY = hidden_file.OPENAI_KEY
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
    title, content = uukanshu_trawler.get_chapter(book_id=str(book_id), chapter_num=str(chapter_num))
    print(content)
    print(title)

@command
def save_chapter(book_id, chapter_num):
    uukanshu_trawler = UukanshuNovelTrawler()
    text_writer = TextWriter(
        parent_dir=DOWNLOADED_BOOKS_DIR
    )
    
    title, content = uukanshu_trawler.get_chapter(book_id=str(book_id), chapter_num=str(chapter_num))
    text_writer.write_to_file(
        book_title=BOOK_TITLE,
        chapter_title=title,
        content=content
    )

@command
def get_chapter_titles(book_id):
    uukanshu_trawler = UukanshuNovelTrawler()
    uukanshu_trawler.get_chapter_titles(book_id)

if __name__ == "__main__":
  Run()