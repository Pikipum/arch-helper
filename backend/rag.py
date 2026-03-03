from langchain.tools import tool
from langchain.agents import create_agent
import os
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
import chromadb

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chromadb"))
COLLECTION_NAME = "arch_wiki"

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)
vector_store = Chroma(client=client, collection_name=COLLECTION_NAME)

model = ChatOllama(model="mistral", temperature=0)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    docs = vector_store.similarity_search(query, k=2)
    for d in docs:
        print("retrieved", d.metadata)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in docs
    )
    return serialized, docs

tools = [retrieve_context]
prompt = (
    "You are a computer expert specializing in Arch Linux troubleshooting. "
    "Use the tool to search the Arch Linux Wiki for solutions."
)
agent = create_agent(model, tools, system_prompt=prompt)

if __name__ == "__main__":
    # test query
    query = "How to install packages from the AUR?\n\nWhich docs did you use?"
    for event in agent.stream(
        {"messages":[{"role":"user","content":query}]},
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()
