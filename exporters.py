import copy
from EbookLib import epub
from base import BaseExporter
import os


class EpubExporter(BaseExporter):
    def __init__(self, book_id:str) -> None:
        self.book_id = book_id
        self.book_title = self._format_title(self.book_id)

    # TODO: complete implementation of this method
    def export_epub(self):
        # Create a new EPUB book
        book = epub.EpubBook()

        # Set metadata
        book.set_title(self.book_id)
        book.set_language('en')
        book.add_author("Author Name")

        # List all chapter files in the given directory
        chapter_files = sorted(
            (os.path.join(chapters_dir, f) for f in os.listdir(chapters_dir) if f.endswith('.txt')),
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0].replace('chapter-', ''))
        )

        # Add chapters to the EPUB
        for chapter_file in chapter_files:
            # Read chapter content
            with open(chapter_file, 'r', encoding='utf-8') as file:
                chapter_title = os.path.splitext(os.path.basename(chapter_file))[0].replace('chapter-', 'Chapter ')
                chapter_content = file.read()

            # Create a new EPUB chapter
            chapter = epub.EpubHtml(title=chapter_title, file_name=os.path.basename(chapter_file), lang='en')
            chapter.set_content(f'<h1>{chapter_title}</h1><p>{chapter_content.replace("\n", "<br/>")}</p>')

            # Add chapter to the book
            book.add_item(chapter)

        # Define the spine (order of chapters)
        book.spine = ['nav'] + [epub.EpubHtml(title='Introduction', file_name='intro.xhtml', content='<h1>Introduction</h1><p>This is the introduction.</p>')] + list(book.items)

        # Add a Table of Contents (TOC)
        book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
                    (epub.Section('Chapters'), [epub.Link(chapter.file_name, chapter.title, chapter.file_name) for chapter in book.items if isinstance(chapter, epub.EpubHtml)]))

        # Add default stylesheet
        style = '''body { font-family: Arial, sans-serif; } h1 { color: #333; } p { margin: 1em 0; }'''
        style_file = epub.EpubItem(uid="style", file_name="styles.css", media_type="text/css", content=style)
        book.add_item(style_file)
        
        # Define the spine (order of chapters) and add the stylesheet
        book.spine = ['nav', style_file] + [item for item in book.items if item != style_file]

        # Write to the EPUB file
        epub.write_epub(epub_filename, book, {})

    def _format_title(self):
        # Replace hyphens with spaces
        title = copy(self.book_id)
        title = title.replace('-', ' ')
        title = title.title()
        return title
# # Example usage
# chapters_dir = 'path_to_your_chapter_files'  # Replace with your directory containing text files
# epub_filename = 'output_book.epub'
# create_epub_from_chapters(chapters_dir, epub_filename)
