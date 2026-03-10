import logging

from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
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

def rewrite_query(state: MessagesState) -> dict:
    q = state["messages"][-1]["content"]
    # rewrite query ?
    new_q = q  # placeholder
    return {"query": new_q}

def retrieve_docs(state: dict) -> dict:
    q = state["query"]
    candidates = vector_store.similarity_search(q, k=RETRIEVAL_CANDIDATES)
    return {"docs": candidates}

def evaluate_docs(state: dict) -> dict:
    docs = state["docs"]
    good = rerank_documents(docs, state["query"], top_n=RETRIEVAL_K)
    return {"good_docs": good}

def format_context(state: dict) -> dict:
    ctx = "\n\n".join(
        f"Source: {d.metadata}\nContent: {d.page_content}"
        for d in state["good_docs"]
    )
    return {"context": ctx}

@tool(response_format="content_and_artifact")
def search_arch_wiki(query: str):
    """  
    Search the Arch Linux Wiki for troubleshooting advice, package
    names, configuration snippets, hardware compatibility, etc.
    ALWAYS call this tool for any question that mentions Arch, pacman,
    systemd, kernel, drivers, AUR, wifi, bluetooth, Xorg, etc.
    """
    candidates = vector_store.similarity_search(query, k=RETRIEVAL_CANDIDATES)
    reranked = rerank_documents(candidates, query, top_n=RETRIEVAL_K)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in reranked
    )
    return serialized, reranked


SYSTEM_PROMPT = (
    "You are a computer expert specializing in Arch Linux troubleshooting. "
    "You MUST call search_arch_wiki before answering any technical question. "
    "For casual greetings, respond naturally without tools. "
    "Base technical answers on retrieved wiki content. Cite source pages."
)

tools = [search_arch_wiki]

model_with_tools = model.bind_tools(tools)

def call_model(state: MessagesState):
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

graph = StateGraph(MessagesState)

graph.add_node("rewrite", rewrite_query)
graph.add_node("retrieve", retrieve_docs)
graph.add_node("evaluate", evaluate_docs)
graph.add_node("format", format_context)
graph.add_node("model", call_model)       

graph.add_edge(START, "rewrite")
graph.add_edge("rewrite", "retrieve")
graph.add_edge("retrieve", "evaluate")
graph.add_edge("evaluate", "format")
graph.add_edge("format", "model")

graph.add_node("tools", ToolNode(tools))
graph.add_edge("model", "tools")
graph.add_edge("tools", "model")
graph.add_edge("model", END)

agent = graph.compile()