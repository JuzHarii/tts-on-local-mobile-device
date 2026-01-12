def chunk_text(text: str, max_len: int = 800):
    chunks = []
    buffer = ""

    for line in text.split("\n"):
        if len(buffer) + len(line) > max_len:
            chunks.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks
