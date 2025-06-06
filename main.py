import subprocess
import logging
from typing import Optional
import typer
from base import TextReaderWriter
from exporters import EpubExporter
from exporters_v2 import EpubExporterV2
from translators import ChatGPTTranslator, NovelHiTranslator
from trawlers import NovelFullTrawler, UukanshuNovelTrawler
from utils import (
    split_content, 
    combine_content, 
    load_translated_titles, 
    get_translated_title,
    validate_chapter_range
)

# OPENAI_KEY = hidden_file.OPENAI_KEY
# OPENAI_USERNAME = hidden_file.OPENAI_USERNAME
# OPENAI_PASSWORD = hidden_file.OPENAI_PASSWORD
BOOK_ID = 11992  # nine star hegemon book key
STARTING_CHAPTER_ID = 7392047

# temp vars
BOOK_TITLE = "nshba"

logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer()

# Configure logging
def setup_logging(debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@app.command()
def export_epub(book_id: str, use_v1: bool = False):
    """Export a book to EPUB format"""
    # Regex for chapter numbering
    order_key = "Chapter (\d+)"

    text_reader = TextReaderWriter(book_id)
    
    # Select the appropriate exporter based on the use_v1 flag
    epub_exporter = EpubExporter(book_id) if use_v1 else EpubExporterV2(book_id)
    
    # Get content
    chapter_paths = text_reader.get_book_titles(order_key=order_key)
    logger.info("Retrieved chapter titles")

    content_chapters = {}
    for path in chapter_paths:
        title, content = text_reader.get_chapter_content(path)
        content_chapters[title] = content
    logger.info(f"Retrieved content for {len(chapter_paths)} chapters")

    # Get cover image and book info
    cover_image, book_info = text_reader.get_info_and_cover()
    logger.info("Retrieved cover image and book info")

    logger.info("Creating EPUB...")
    # Create epub
    epub_exporter.export_epub(
        cover_page=cover_image,
        book_info=book_info,
        book_content=content_chapters,
    )


@app.command()
def get_chapter(book_id: str, chapter_num: str):
    """Get a single chapter from a book"""
    uukanshu_trawler = UukanshuNovelTrawler()
    title, content = uukanshu_trawler.get_chapter(
        book_id=book_id, chapter_num=chapter_num
    )
    logger.info(content)
    logger.info(title)


@app.command()
def get_and_save_book(
    book_id: str, 
    starting_chapter_num: Optional[str] = None, 
    ending_chapter_num: Optional[str] = None
):
    """Download and save a book from Uukanshu"""
    uukanshu_trawler = UukanshuNovelTrawler()
    text_writer = TextReaderWriter(book_id)

    chapter_titles = uukanshu_trawler.get_chapter_titles(book_id)
    validate_chapter_range(chapter_titles, starting_chapter_num, ending_chapter_num)

    start = int(starting_chapter_num) if starting_chapter_num else 1
    end = (
        int(ending_chapter_num) if ending_chapter_num else int(list(chapter_titles)[-1])
    )

    for chapter_num in range(start, end + 1):
        logger.info(f"Retrieving content for chapter {chapter_num}...")
        title, content = uukanshu_trawler.get_chapter(
            book_id=book_id, chapter_num=str(chapter_num)
        )
        logger.info(f"Retrieved content for title: {title}")

        text_writer.write_chapter_to_file(
            book_title=book_id, chapter_title=title, content=content
        )


@app.command()
def get_and_save_book_novelfull(
    book_id: str, 
    starting_chapter_num: Optional[str] = None, 
    ending_chapter_num: Optional[str] = None
):
    """Download and save a book from NovelFull"""
    novelfull_trawler = NovelFullTrawler()
    text_writer = TextReaderWriter(book_id)

    # Download book cover
    book_cover = novelfull_trawler.get_book_cover(book_id)
    if book_cover is None:
        logger.info("Unable to download book cover")
    else:
        text_writer.save_book_cover(book_title=book_id, image_bytes=book_cover)

    # Download book info
    book_info = novelfull_trawler.get_book_info(book_id)
    text_writer.save_book_info(book_title=book_id, book_info=book_info)

    # Download book chapters
    chapter_titles = novelfull_trawler.get_chapter_titles(book_id)
    validate_chapter_range(chapter_titles, starting_chapter_num, ending_chapter_num)

    start = int(starting_chapter_num) if starting_chapter_num else 1
    end = (
        int(ending_chapter_num) if ending_chapter_num else int(list(chapter_titles)[-1])
    )

    for chapter_num in range(start, end + 1):
        logger.info(f"Retrieving content for chapter {chapter_num}...")
        title, content = novelfull_trawler.get_chapter(
            book_id=book_id, chapter_num=str(chapter_num)
        )
        logger.info(f"Retrieved content for title: {title}")

        text_writer.write_chapter_to_file(
            book_title=book_id, chapter_title=title, content=content
        )


@app.command()
def save_chapter(book_id: str, chapter_num: str):
    """Save a single chapter to a file"""
    uukanshu_trawler = UukanshuNovelTrawler()
    text_writer = TextReaderWriter(book_id)

    title, content = uukanshu_trawler.get_chapter(
        book_id=book_id, chapter_num=chapter_num
    )
    text_writer.write_chapter_to_file(
        book_title=book_id, chapter_title=title, content=content
    )


@app.command()
def get_chapter_titles(book_id: str):
    """List all chapter titles for a book"""
    uukanshu_trawler = UukanshuNovelTrawler()
    titles = uukanshu_trawler.get_chapter_titles(book_id)
    for num, info in titles.items():
        logger.info(f"{num}: {info['chinese_title']}")


@app.command()
def translate_chapter(book_id: str, chapter_num: str):
    """Translate a single chapter"""
    text_rw = TextReaderWriter(book_id)
    chinese_title, chinese_content = text_rw.get_file_content(
        book_title=book_id, chapter_num=chapter_num, is_downloaded=True
    )
    logger.info(f"Retrieved Chinese content ({len(chinese_content)} chars)")
    
    novelhi_translator = NovelHiTranslator()
    english_title = novelhi_translator.translate_text(chinese_title).strip()
    english_content = novelhi_translator.translate_text(chinese_content)
    
    logger.info("Translated to English, saving to file")
    text_rw.write_chapter_to_file(
        book_title=book_id,
        chapter_title=f"{chapter_num}_{english_title}",
        content=english_content,
        is_downloaded=False,
    )
    logger.info("Translation complete")


@app.command()
def translate_chapters(
    book_id: str,
    starting_chapter_num: str, 
    ending_chapter_num: str,
    titles_file: Optional[str] = None
):
    """Translate a range of chapters"""
    text_rw = TextReaderWriter(book_id)
    novelhi_translator = NovelHiTranslator()
    
    # Load translated titles if provided
    translated_titles = {}
    if titles_file:
        translated_titles = load_translated_titles(titles_file)
    
    for chapter_num in range(int(starting_chapter_num), int(ending_chapter_num) + 1):
        logger.info(f"Processing chapter: {chapter_num}...")
        chinese_title, chinese_content = text_rw.get_file_content(
            book_title=book_id, chapter_num=str(chapter_num), is_downloaded=True
        )
        logger.info(f"Retrieved Chinese content ({len(chinese_content)} chars)")

        # Split content for translation
        contents = split_content(chinese_content)

        # Get translated title
        if titles_file:
            english_title = get_translated_title(str(chapter_num), translated_titles)
        else:
            english_title = f"{chapter_num}_{novelhi_translator.translate_text(chinese_title).strip()}"
        
        logger.info(f"Using English title: {english_title}")

        # Translate content in chunks
        translated_contents = []
        for content in contents:
            logger.info(f"Translating content chunk ({len(content)} chars)")
            translated_contents.append(novelhi_translator.translate_text(content))
        
        english_content = combine_content(translated_contents)

        logger.info("Translated to English, saving to file")
        text_rw.write_chapter_to_file(
            book_title=book_id,
            chapter_title=english_title,
            content=english_content,
            is_downloaded=False,
        )
        logger.info(f"Translation for chapter {chapter_num} complete")


@app.command()
def test_split(book_id: str, chapter_num: str):
    """Test the content splitting function"""
    text_rw = TextReaderWriter(book_id)
    chinese_title, chinese_content = text_rw.get_file_content(
        book_title=book_id, chapter_num=chapter_num, is_downloaded=True
    )
    logger.info(f"Retrieved Chinese content ({len(chinese_content)} chars)")
    
    split_contents = split_content(chinese_content)
    logger.info(f"Split into {len(split_contents)} chunks")
    
    combined_content = combine_content(split_contents)
    logger.info(f"Combined content length: {len(combined_content)} chars")
    
    if chinese_content == combined_content:
        logger.info("Content unchanged after split/combine")
    else:
        logger.warning("WARNING: Content changed after split/combine")


@app.command()
def get_titles():
    """Copy all book titles to clipboard"""
    text_rw = TextReaderWriter(BOOK_TITLE)
    order_key = "Chapter (\d+)"
    titles = text_rw.get_book_titles(order_key=order_key)
    titles_text = "\n".join(titles)

    subprocess.run(["pbcopy"], text=True, input=titles_text, encoding='utf-8')
    logger.info(f"Retrieved and copied {len(titles)} titles to clipboard")


@app.command()
def transform_translated_titles(filepath: str = "nshba_translated_titles.txt"):
    """Transform translated titles to a standardized format"""
    translated_titles = {}
    
    with open(filepath, "r") as file:
        lines = file.readlines()
        for line in lines:
            details = line.split("_")
            chapter_num = details[0]
            title = details[1].strip() if len(details) > 1 else ""
            title = " ".join([word.capitalize() for word in title.split(" ")])
            final_str = f"{chapter_num}_{title}"
            translated_titles[details[0]] = final_str

    titles = ""
    for i in sorted(translated_titles.keys()):
        titles += f"{translated_titles[i]}\n"
        
    with open(filepath, "w") as file:
        file.write(titles)
        
    logger.info(f"Transformed titles saved to {filepath}")


# Global debug option via callback
@app.callback()
def main(debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode")):
    """CLI tool for downloading and translating novels"""
    setup_logging(debug)


if __name__ == "__main__":
    app()
