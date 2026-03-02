import glob
import os
from html.parser import HTMLParser
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "en")
DB_PATH = os.path.join(os.path.dirname(__file__), "chromadb")
COLLECTION_NAME = "arch_wiki"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 500

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []

    def handle_data(self, data: str):
        self.text_parts.append(data)

    def get_text(self) -> str:
        return "".join(self.text_parts)

def extract_text_from_html(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return parser.get_text()

def load_html_documents(directory: str) -> list[dict]:
    docs: list[dict] = []
    for path in sorted(glob.glob(os.path.join(directory, "*.html"))):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = extract_text_from_html(f.read()).strip()
        if not text:
            continue
        filename = os.path.basename(path)
        title = filename.removesuffix(".html").replace("_", " ")
        docs.append({"filename": filename, "title": title, "text": text})
    return docs

def chunk_documents(docs: list[dict]) -> tuple[list[str], list[str], list[dict]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    ids, texts, metadatas = [], [], []
    for doc in docs:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc['filename']}::chunk{i}")
            texts.append(chunk)
            metadatas.append({
                "source": doc["filename"],
                "title": doc["title"],
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
    return ids, texts, metadatas

def ingest():
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    docs = load_html_documents(DATA_DIR)
    assert docs, f"No HTML files found in {DATA_DIR}"

    ids, texts, metadatas = chunk_documents(docs)
    print(f"Ingesting {len(ids)} chunks from {len(docs)} pages...")

    for start in range(0, len(ids), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(ids))
        collection.upsert(
            ids=ids[start:end],
            documents=texts[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"Done. Collection has {collection.count()} chunks.")

if __name__ == "__main__":
    ingest()
