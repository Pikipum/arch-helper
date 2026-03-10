import logging

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
import chromadb
from rank_bm25 import BM25Okapi

from config import DB_PATH, COLLECTION_NAME, MODEL_NAME, RETRIEVAL_K, RETRIEVAL_CANDIDATES

logger = logging.getLogger(__name__)

client = chromadb.PersistentClient(path=DB_PATH)
vector_store = Chroma(
    client=client,
    collection_name=COLLECTION_NAME,
)

model = ChatOllama(model=MODEL_NAME, temperature=0, stream=True)


def rerank_documents(docs: list, query: str, top_n: int):
    tokenized_docs = [doc.page_content.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_docs)
    scores = bm25.get_scores(query.lower().split())

    scored_docs = sorted(enumerate(zip(scores, docs)), key=lambda x: x[1][0], reverse=True)

    logger.info("BM25 reranking for query: %s", query)
    for new_rank, (orig_rank, (score, doc)) in enumerate(scored_docs, 1):
        logger.info(
            "  %2d -> %2d | score=%.4f | %s",
            orig_rank + 1, new_rank, score, doc.metadata.get("source", "unknown"),
        )

    return [doc for _, (_, doc) in scored_docs[:top_n]]

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """ Search the Arch Linux Wiki for relevant information. """
    candidates = vector_store.similarity_search(query, k=RETRIEVAL_CANDIDATES)
    reranked = rerank_documents(candidates, query, top_n=RETRIEVAL_K)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in reranked
    )
    return serialized, reranked


SYSTEM_PROMPT = (
    "You are a computer expert specializing in Arch Linux troubleshooting. "
    "Use the retrieve_context tool to search the Arch Linux Wiki before answering. "
    "Base your answers on the retrieved wiki content. Cite the source pages."
)

agent = create_agent(model, [retrieve_context], system_prompt=SYSTEM_PROMPT)