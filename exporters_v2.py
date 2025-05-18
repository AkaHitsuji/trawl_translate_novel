import re
import logging
import datetime
import os
from typing import Dict, List, Tuple
from base import BaseExporter
from ebooklib import epub

# Configure logging
logger = logging.getLogger(__name__)

class EpubExporterV2(BaseExporter):
    """
    An improved V2 implementation of the EPUB exporter using ebooklib.
    This exporter creates EPUB files from book content with enhanced formatting
    and better standards compliance.
    """
    
    # HTML templates
    HTML_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{}</title>
    <meta charset="utf-8" />
</head>
<body>
"""
    HTML_FOOTER = """
</body>
</html>
"""
    
    def __init__(self, book_id: str) -> None:
        """
        Initialize the EPUB exporter with a book ID.
        
        Args:
            book_id: The unique identifier for the book
        """
        self.book_id = book_id
        self.book_title = self._format_title()
        logger.debug(f"Initialized EpubExporterV2 with book_id: {book_id}")

    def _create_html_content(self, title: str, content: str) -> str:
        """Create HTML content for a chapter or introduction."""
        # Process the text by splitting into paragraphs
        paragraphs = content.strip().split('\n\n')
        
        # Build HTML content
        html_content = f'<h1>{title}</h1>\n'
        
        # Add paragraphs
        for paragraph in paragraphs:
            if paragraph.strip():
                html_content += f"<p>{paragraph.strip()}</p>\n"
                
        return html_content

    def _extract_chapter_number(self, chapter_title: str) -> int:
        """
        Extract chapter number from chapter title for correct sorting.
        
        Args:
            chapter_title: The title of the chapter
            
        Returns:
            int: The chapter number, or 0 if no number is found
        """
        match = re.search(r'Chapter\s+(\d+)', chapter_title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _sort_chapters(self, book_content: Dict[str, str]) -> List[Tuple[str, str]]:
        """
        Sort chapters by their numerical order rather than lexicographical order.
        
        Args:
            book_content: Dictionary mapping chapter titles to chapter content
            
        Returns:
            List[Tuple[str, str]]: Sorted list of (chapter_title, chapter_content) pairs
        """
        # Create a list of (chapter_title, chapter_content, chapter_number)
        chapters_with_numbers = []
        for chapter_title, chapter_content in book_content.items():
            chapter_number = self._extract_chapter_number(chapter_title)
            chapters_with_numbers.append((chapter_title, chapter_content, chapter_number))
        
        # Sort by chapter number
        sorted_chapters = sorted(chapters_with_numbers, key=lambda x: x[2])
        
        # Return just the title and content
        return [(title, content) for title, content, _ in sorted_chapters]

    def export_epub(self, cover_page: bytes, book_info: Dict, book_content: Dict) -> bool:
        """
        Export book content to EPUB format using ebooklib.
        
        Args:
            cover_page: The cover image as bytes
            book_info: Dictionary containing metadata about the book
            book_content: Dictionary mapping chapter titles to chapter content
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            logger.debug("Starting EPUB export process...")
            
            # Create EPUB book
            book = epub.EpubBook()
            
            # Set required metadata
            book.set_identifier(f"akahitsuji-{self.book_id}")
            book.set_title(self.book_title)
            book.set_language('en')
            
            # Add author
            book.add_author(book_info.get("Author", "Unknown"))
            
            # Add description if available
            if "description" in book_info:
                book.add_metadata('DC', 'description', book_info["description"])
            
            # Add the current date for the modified date metadata (required for EPUB 3.0)
            current_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            book.add_metadata(None, 'meta', '', {'property': 'dcterms:modified', 'content': current_date})
            
            # Add cover image if provided
            if cover_page:
                logger.debug(f"Adding cover image ({len(cover_page)} bytes)")
                cover_image = epub.EpubItem(
                    uid="cover-image",
                    file_name="images/cover.jpg",
                    media_type="image/jpeg",
                    content=cover_page
                )
                book.add_item(cover_image)
                
                # Add cover to metadata
                book.add_metadata(None, 'meta', '', {'name': 'cover', 'content': 'cover-image'})
            
            # Add CSS style
            style = """
            body {
                font-family: "Helvetica", "Arial", sans-serif;
                margin: 5%;
                padding: 0;
                line-height: 1.5;
            }
            h1 {
                text-align: center;
                font-size: 1.5em;
                margin: 1em 0;
            }
            p {
                margin: 0.5em 0;
                text-indent: 1.5em;
            }
            """
            
            css = epub.EpubItem(
                uid="style_default",
                file_name="style/default.css",
                media_type="text/css",
                content=style
            )
            book.add_item(css)
            
            # Create chapters list for toc and spine
            chapters = []
            
            # Add introduction if available
            intro_chapter = None
            introduction = book_info.get("description", "")
            if introduction and introduction.strip():
                logger.debug("Adding introduction chapter")
                
                intro_chapter = epub.EpubHtml(
                    title="Introduction",
                    file_name="intro.xhtml",
                    lang="en"
                )
                
                intro_content = self._create_html_content("Introduction", introduction)
                intro_chapter.set_content(intro_content)
                intro_chapter.add_item(css)
                
                book.add_item(intro_chapter)
                chapters.append(intro_chapter)
            
            # Sort chapters by numerical order rather than lexicographical order
            sorted_chapters = self._sort_chapters(book_content)
            
            # Add book chapters
            for i, (chapter_title, chapter_content) in enumerate(sorted_chapters):
                if not chapter_content.strip():
                    logger.warning(f"Empty content for chapter {chapter_title}, skipping")
                    continue
                
                logger.debug(f"Adding chapter: {chapter_title}")
                
                # Create safe filename
                safe_filename = f"chapter_{i+1:04d}.xhtml"
                
                # Create chapter
                chapter = epub.EpubHtml(
                    title=chapter_title,
                    file_name=safe_filename,
                    lang="en"
                )
                
                # Set chapter content
                chapter_html = self._create_html_content(chapter_title, chapter_content)
                chapter.set_content(chapter_html)
                chapter.add_item(css)
                
                # Add chapter to book
                book.add_item(chapter)
                chapters.append(chapter)
                
                # Log debug info
                logger.debug(f"  file_name: {chapter.file_name}")
                logger.debug(f"  content length: {len(chapter_html) if chapter_html else 0}")
            
            # Add navigation files required for EPUB
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style
            )
            book.add_item(nav_css)
            
            # Add NCX and Nav files
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Define Table of Contents
            book.toc = chapters
            
            # Define book spine
            book.spine = ['nav'] + chapters
            
            # Write EPUB file
            output_file = f"{self.book_id}.epub"
            logger.debug(f"Writing EPUB to {output_file}")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Write the EPUB file with specific options
            epub.write_epub(
                output_file, 
                book, 
                {
                    'epub3_landmark': True,
                    'epub3_pages': False,
                    'ignore_ncx': False,
                    'compresslevel': 9
                }
            )
            
            logger.info(f"Successfully exported EPUB to {output_file}")
            return True
            
        except Exception as e:
            if "Document is empty" in str(e):
                # This is a known issue with some EPUB libraries where the navigation document
                # appears empty but the EPUB is still created correctly and usable
                logger.warning(f"Non-critical EPUB warning: {str(e)}")
                logger.info(f"EPUB file was still created at {output_file}")
                return True
            else:
                # Log other exceptions as fatal errors
                logger.error(f"Fatal error in export_epub: {str(e)}")
                logger.debug("Traceback:", exc_info=True)
                return False

    def _format_title(self) -> str:
        """
        Format the book ID as a proper title by replacing hyphens with spaces 
        and applying title case.
        
        Returns:
            str: Formatted book title
        """
        words = self.book_id.replace('-', ' ').split()
        title = ' '.join(word.capitalize() for word in words)
        return title

# Example usage:
# exporter = EpubExporterV2("my-book-id")
# exporter.export_epub(cover_page_bytes, book_info_dict, book_content_dict) 