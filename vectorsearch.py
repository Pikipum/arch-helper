import os
import glob
import chromadb
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self):
        return "".join(self.text_parts)


def extract_text_from_html(content: str) -> str:
    parser = TextExtractor()
    parser.feed(content)
    return parser.get_text()

def load_html_documents(directory: str):
    pattern = os.path.join(directory, "*.html")
    ids = []
    documents = []

    for path in glob.glob(pattern):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
        except Exception as e:
            print(f"failed to read {path}: {e}")
            continue

        text = extract_text_from_html(html)
        ids.append(os.path.basename(path))
        documents.append(text)

    return ids, documents

chroma_client = chromadb.PersistentClient(path="chromadb")
collection = chroma_client.get_or_create_collection(name="my_collection")

if not (os.path.isdir('chromadb')):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "en")
    ids, docs = load_html_documents(data_dir)
    if ids:
        collection.upsert(documents=docs, ids=ids)
        print(f"upserted {len(ids)} documents into collection\n")
    else:
        print("no documents found to ingest")

# test query
results = collection.query(
    query_texts=["Mixing additional audio into the microphone's audio"],
    n_results=6
)
print(results["ids"])
