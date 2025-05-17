# Trawl Translate Novel

A Python application for scraping, translating, and exporting Chinese novels to e-book formats.

## Overview

This tool helps you:
1. Scrape content from Chinese novel websites (Uukanshu, NovelFull)
2. Translate Chinese text to English using either NovelHi or ChatGPT
3. Export the content to EPUB format for e-readers

## Features

- Scrape complete novels or specific chapter ranges
- Translate content with automated translation services
- Export to nicely formatted EPUB files with cover images and metadata
- Split long content into manageable chunks for translation
- Organize downloaded and translated content in separate directories

## Installation

1. Clone the repository
```
git clone https://github.com/yourusername/trawl_translate_novel.git
cd trawl_translate_novel
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. (Optional) For ChatGPT translation, create a `hidden_file.py` with your OpenAI credentials:
```python
OPENAI_KEY = "your-api-key"
OPENAI_USERNAME = "your-username"
OPENAI_PASSWORD = "your-password"
```

## Usage

The application uses the `typer` library to provide a command-line interface. Here are the main commands:

### Scraping Novel Content

#### Get a whole book from NovelFull
```
python -m main get-and-save-book-novelfull <book_id> [<starting_chapter_num>] [<ending_chapter_num>]
```

#### Get a whole book from Uukanshu
```
python -m main get-and-save-book <book_id> [<starting_chapter_num>] [<ending_chapter_num>]
```

#### Get a single chapter
```
python -m main get-chapter <book_id> <chapter_num>
```

#### Save a single chapter
```
python -m main save-chapter <book_id> <chapter_num>
```

#### List chapter titles
```
python -m main get-titles
```

### Translation

#### Translate a single chapter
```
python -m main translate-chapter <chapter_num>
```

#### Translate a range of chapters
```
python -m main translate-chapters <starting_chapter_num> <ending_chapter_num>
```

### Export

#### Export to EPUB
```
python -m main export-epub <book_id> [--debug] [--use-v1]
```

## Project Structure

- `main.py` - Main command-line interface using Typer
- `trawlers.py` - Web scrapers for novel sites (UukanshuNovelTrawler, NovelFullTrawler)
- `translators.py` - Translation services (ChatGPTTranslator, NovelHiTranslator)
- `exporters.py` - EPUB creation (EpubExporter)
- `exporters_v2.py` - Improved EPUB creation (EpubExporterV2)
- `base.py` - Base classes and file management utilities
- `downloaded_books/` - Directory for downloaded original language content
- `translated_books/` - Directory for translated content
- `browsers/` - Contains selenium handlers for NovelHi and ChatGPT

## Example Workflow

1. Download a novel from NovelFull:
```
python -m main get-and-save-book-novelfull reverend-insanity
```

2. Translate chapters:
```
python -m main translate-chapters 1 10
```

3. Export to EPUB:
```
python -m main export-epub reverend-insanity
```

## Notes

- The tool handles Chinese-specific numbering systems and fixes chapter title discrepancies
- For long chapters, the translator automatically splits the content into manageable chunks
- Book information and cover images are preserved in the EPUB output
- The application now uses the Typer library for CLI commands, which uses hyphens in command names instead of underscores
- Two EPUB exporter versions are available, with V2 being the default and offering improved formatting
