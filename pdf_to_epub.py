# importing required modules
from PyPDF2 import PdfReader
from ebooklib import epub


BOOK_TITLE = "Overgeared_Novel"
TEXT_FILE = f"{BOOK_TITLE}.txt"
# creating a pdf reader object
reader = PdfReader(f"{BOOK_TITLE}.pdf")

# printing number of pages in pdf file
num_pages = len(reader.pages)
print(num_pages)

# getting a specific page from the pdf file
page = reader.pages[0]

full_text = ""
for i in range(num_pages):
    full_text += reader.pages[i].extract_text()

print(full_text[:100])
with open(TEXT_FILE, "w") as file:
    file.write(full_text)
    file.close()


# def create_epub(cover_page, list_of_links, window, lbl_numOfChapters, lbl_coverPage):
#     book = epub.EpubBook()

#     # set metadata
#     book.set_identifier('id123456789')
#     book.set_title(selected_novel + ' - EPUB generator by AkaHitsuji')
#     book.set_language('en')

#     book.set_cover("cover_page.jpg", open('cover_page.jpg', 'rb').read())
#     print("Cover page set for ePub")

#     list_of_epub_chapters = []
#     print('THIS IS THE LIST OF LINKS\n\n',list_of_links)
#     array_length = len(list_of_links)-2
#     chapter_number = 1
#     for i in range(array_length):
#         chapter_title = list_of_links[i].split("/")[3]
#         download_chapter('https://www.wuxiaworld.com' + list_of_links[i], chapter_title + '.html')
#         clean_chapter(chapter_title + '.html', chapter_title + '.xhtml')
#         chapter_content = open(chapter_title + '.xhtml', "r", encoding="utf8")
#         chapter_content = BeautifulSoup(chapter_content, 'html.parser')
#         chapter_content = chapter_content.get_text()
#         chapter_content = "<br />".join(chapter_content.split("\n"))
#         print("Chapter",chapter_number,"downloaded")
#         remove_file(chapter_title + '.xhtml')

#         # create chapter
#         epub_chapter = epub.EpubHtml(title=list_of_chapters[i], file_name=chapter_title + '.xhtml', lang='hr')
#         epub_chapter.content = '<head>\n<title>' + list_of_chapters[i] + '</title>\n</head>\n<body>\n<strong>' + list_of_chapters[i] + '</strong>\n<p>' + chapter_content + '</p>\n</body>\n</html>'

#         # update tkinter to display progress
#         lbl_numOfChapters.configure(text=str(chapter_number)+"/"+str(array_length)+" chapters downloaded")
#         window.update()

#         # add chapter
#         book.add_item(epub_chapter)
#         list_of_epub_chapters.append(epub_chapter)

#         chapter_number+=1
#         # for testing: set limit on test printing
#         # if chapter_number==5:
#         #     break

#     # define Table Of Contents
#     for epub_chapter in list_of_epub_chapters:
#         book.toc.append(epub_chapter)

#     # add default NCX and Nav file
#     book.add_item(epub.EpubNcx())
#     book.add_item(epub.EpubNav())

#     # define CSS style
#     style = 'BODY {color: white;}'
#     nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

#     # add CSS file
#     book.add_item(nav_css)

#     # basic spine
#     book.spine = ['nav']
#     for epub_chapter in list_of_epub_chapters:
#         book.spine.append(epub_chapter)

#     # write to the file
#     epub.write_epub(selected_novel + ' - EPUB generator by AkaHitsuji.epub', book)
