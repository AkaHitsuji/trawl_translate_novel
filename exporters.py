import re
from typing import Dict
from ebooklib import epub
from base import BaseExporter


class EpubExporter(BaseExporter):
    def __init__(self, book_id: str) -> None:
        self.book_id = book_id
        self.book_title = self._format_title()

    def export_epub(self, cover_page: bytes, book_info: Dict, book_content: Dict):
        # Create a new EPUB book
        book = epub.EpubBook()

        # Set metadata
        book.set_title(self.book_title)
        book.set_language("en")
        book.add_author(book_info.get("Author"))
        book.add_metadata("DC", "publisher", book_info.get("Source"))
        book.add_metadata("DC", "subject", book_info.get("Genre"))
        book.add_metadata(
            "DC", "contributor", f"{book_info.get('Author')}+', '+'Akahitsuji'"
        )

        # cover page
        cover_image = epub.EpubItem(
            uid="cover",
            file_name="cover.jpg",
            media_type="image/jpeg",
            content=cover_page,
        )
        book.add_item(cover_image)

        # Create introduction chapter
        intro_description = book_info.get("description")
        intro_content = intro_description.replace("\n", "<br/>")
        watermark = "<p><i>Downloaded and generated by Akahitsuji</i></p>"
        chapter_intro = epub.EpubHtml(
            title="Introduction",
            file_name="intro.xhtml",
            content=f"<h1>Introduction</h1>{watermark}<p>{intro_content}</p>",
        )
        book.add_item(chapter_intro)

        # Add chapters to the EPUB
        for chapter_title, chapter_content in book_content.items():
            # sanitise % from title
            chapter_title = chapter_title.replace("%", "percent")

            chapter = epub.EpubHtml(
                title=chapter_title, file_name=f"{chapter_title}.xhtml", lang="en"
            )
            chapter_content = chapter_content.replace("\n", "<br/>")
            chapter.set_content(f"<h1>{chapter_title}</h1><p>{chapter_content}</p>")

            # Add chapter to the book
            book.add_item(chapter)

        # Add default stylesheet
        style = """body { font-family: Arial, sans-serif; } h1 { color: #333; } p { margin: 1em 0; }"""
        style_file = epub.EpubItem(
            uid="style", file_name="styles.css", media_type="text/css", content=style
        )
        book.add_item(style_file)

        # Define the spine (order of chapters) and add the stylesheet
        book.spine = ["nav", style_file, chapter_intro] + [
            item
            for item in book.items
            if isinstance(item, epub.EpubHtml) and item != chapter_intro
        ]

        # Add a Table of Contents (TOC)
        book.toc = [epub.Link("intro.xhtml", "Introduction", "intro")] + [
            epub.Link(chapter.file_name, chapter.title, chapter.file_name)
            for chapter in book.items
            if isinstance(chapter, epub.EpubHtml) and chapter != chapter_intro
        ]

        # Add navigation file
        nav = epub.EpubNav()
        book.add_item(nav)

        # Write to the EPUB file
        epub.write_epub(f"{self.book_id}.epub", book, {})
        print(f"saved epub for {self.book_id}")

    def _format_title(self):
        # Replace hyphens with spaces
        title = self.book_id
        title = title.replace("-", " ")
        title = title.title()
        return title


# # Example usage
# chapters_dir = 'path_to_your_chapter_files'  # Replace with your directory containing text files
# epub_filename = 'output_book.epub'
# create_epub_from_chapters(chapters_dir, epub_filename)
