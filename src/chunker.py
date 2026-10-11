def _split_long_paragraph(
    paragraph,
    chunk_size
):
    words = paragraph.split()
    chunks = []
    current = ""

    for word in words:

        if not current:
            current = word
            continue

        candidate = (
            current + " " + word
        )

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


def chunk_text(
    text,
    chunk_size=500,
    overlap=100
):
    if not text or not text.strip():
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    processed_paragraphs = []

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:
            processed_paragraphs.append(
                paragraph
            )
        else:
            processed_paragraphs.extend(
                _split_long_paragraph(
                    paragraph,
                    chunk_size
                )
            )

    chunks = []
    current_chunk = ""

    for paragraph in processed_paragraphs:

        if not current_chunk:
            current_chunk = paragraph
            continue

        candidate = (
            current_chunk
            + "\n\n"
            + paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate
            continue

        chunks.append(
            current_chunk
        )

        previous_overlap = (
            current_chunk[-overlap:]
            if overlap > 0
            else ""
        )

        current_chunk = (
            previous_overlap
            + "\n\n"
            + paragraph
        ).strip()

        if len(current_chunk) > chunk_size:
            current_chunk = paragraph

    if current_chunk:
        chunks.append(
            current_chunk
        )

    return chunks