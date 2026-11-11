
import re


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def normalize_text(text: str) -> str:
    """
    Normalize extracted document text without removing
    meaningful technical content.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    text = normalize_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        if end < len(text):
            # Prefer a nearby sentence or word boundary
            search_start = start + int(chunk_size * 0.7)

            sentence_end = max(
                text.rfind(". ", search_start, end),
                text.rfind("? ", search_start, end),
                text.rfind("! ", search_start, end),
            )

            if sentence_end != -1:
                end = sentence_end + 1
            else:
                word_end = text.rfind(" ", search_start, end)

                if word_end != -1:
                    end = word_end

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        # Move forward while retaining overlap
        next_start = max(start + 1, end - overlap)

        # Avoid beginning a chunk in the middle of a word
        if next_start > 0 and text[next_start - 1] != " ":
            next_space = text.find(" ", next_start)

            if next_space != -1 and next_space < end:
                next_start = next_space + 1

        start = next_start

    return chunks


def process_extracted_blocks(
    blocks: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict]:

    processed_chunks = []

    for block in blocks:

        normalized = normalize_text(block.get("text", ""))

        if not normalized:
            continue

        chunks = split_into_chunks(
            normalized,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in chunks:
            processed_chunks.append({
                "content": chunk,
                "source_type": block["source_type"],
                "source_number": block["source_number"],
            })

    return processed_chunks
