import os

from docx import Document
from pypdf import PdfReader


def load_document(file_path):

    extension = (
        os.path.splitext(file_path)[1]
        .lower()
    )

    if extension == ".txt":

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()


    if extension == ".pdf":

        reader = PdfReader(
            file_path
        )

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)


    if extension == ".docx":

        document = Document(
            file_path
        )

        paragraphs = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n\n".join(paragraphs)


    raise ValueError(
        f"Unsupported file type: {extension}"
    )