from langchain.tools import tool
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
import chromadb

from config import DB_PATH, COLLECTION_NAME, MODEL_NAME, RETRIEVAL_K

client = chromadb.PersistentClient(path=DB_PATH)
vector_store = Chroma(
    client=client,
    collection_name=COLLECTION_NAME,
)

model = ChatOllama(model=MODEL_NAME, temperature=0, stream=True)


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Search the Arch Linux Wiki for relevant information."""
    docs = vector_store.similarity_search(query, k=RETRIEVAL_K)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in docs
    )
    return serialized, docs


SYSTEM_PROMPT = (
    "You are a computer expert specializing in Arch Linux troubleshooting. "
    "Use the retrieve_context tool to search the Arch Linux Wiki before answering. "
    "Base your answers on the retrieved wiki content. Cite the source pages."
)

agent = create_agent(model, [retrieve_context], system_prompt=SYSTEM_PROMPT)