# Mini Project 3 (Final Week 2 Project)

# RAG Chatbot with Source Citations + Confidence Scores — this is the production-grade capstone combining everything.

# What you build:

# A fully interactive chatbot that:

# Loads multiple PDFs (same folder as MP2)
# Answers questions with memory
# Shows sources with page number, filename, chunk content preview, AND similarity score
# Uses similarity_search_with_score to get confidence scores for each retrieved chunk
# Only shows sources above a confidence threshold — filters weak matches
# Multiple sessions with separate memories
# inspect_session() on quit

import warnings
warnings.filterwarnings("ignore")

import os
import json

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableParallel
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from operator import itemgetter

pdf_folder = "pdfs"
all_chunks = []
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 3000,
    chunk_overlap = 300
)

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        path = os.path.join(pdf_folder,filename)
        loader = PyPDFLoader(path)
        pages = loader.load()
        chunks = splitter.split_documents(pages)
        all_chunks.extend(chunks)
        print(f"loaded {filename} - {len(chunks)} chunks")
print(f"total chunks: {len(all_chunks)}")

embeddings = HuggingFaceEmbeddings(
    model_name = "all-MiniLM-L6-v2",
    cache_folder = ".models",
    model_kwargs = {"device":"cpu"},
    encode_kwargs = {"normalize_embeddings":True}
)

INDEX_PATH = "faiss_index"
if os.path.exists(INDEX_PATH):
    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization = True
    )
else:
    vectorstore = FAISS.from_documents(all_chunks,embeddings)
    vectorstore.save_local(INDEX_PATH)

doc1_retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {
        "k": 6,
        "filter": lambda meta: "power-automate" in meta.get("source","")
    }
)

doc2_retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {
        "k": 6,
        "filter": lambda meta: "Game of Thrones" in meta.get("source","")
    }
)

full_retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {
        "k": 6
    }
)

llm = ChatOllama(model = "llama3.2:3b", temperature = 0)

classifier_chain = ChatPromptTemplate.from_messages([
    ("system","""Your task is to classify the user input to any one of the category. 
             doc1 = contains power automate content
             doc2 = contains game of thrones content
             both = question spans both or is unclear
             
             Return exactly one word: doc1, doc2 , or both
             No explanation and No extra text"""),
    ("human","{input}")
])|llm|StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system","""You're a helpful assistant,answer the question user asks using the context.
        if answer is not in the context say I don't know, Keep answers concise and accurate.
        
        context = {context}"""),
    MessagesPlaceholder(variable_name = "chat_history"),
    ("human","{input}")
])

doc1_context_chain = itemgetter("input") | doc1_retriever
doc2_context_chain = itemgetter("input") | doc2_retriever
full_context_chain = itemgetter("input") | full_retriever

doc1_chain = RunnableParallel(
    input = itemgetter("input"),
    chat_history = itemgetter("chat_history"),
    context = doc1_context_chain
)|prompt|llm|StrOutputParser()

doc2_chain = RunnableParallel(
    input = itemgetter("input"),
    chat_history = itemgetter("chat_history"),
    context = doc2_context_chain
)|prompt|llm|StrOutputParser()

full_chain = RunnableParallel(
    input = itemgetter("input"),
    chat_history = itemgetter("chat_history"),
    context = full_context_chain
)|prompt|llm|StrOutputParser()

store = {}
def session_history(session_id:str)->InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

doc1_with_memory = RunnableWithMessageHistory(
    doc1_chain,
    session_history,
    input_messages_key = "input",
    history_messages_key = "chat_history"
)

doc2_with_memory = RunnableWithMessageHistory(
    doc2_chain,
    session_history,
    input_messages_key = "input",
    history_messages_key = "chat_history"
)

full_with_memory = RunnableWithMessageHistory(
    full_chain,
    session_history,
    input_messages_key = "input",
    history_messages_key = "chat_history"
)

def ask(session_id:str,question:str)->str:
    category = classifier_chain.invoke({"input":question}).strip().lower()

    if category == "doc1":
        chain = doc1_with_memory
    elif category == "doc2":
        chain = doc2_with_memory
    else:
        chain = full_with_memory

    answer = chain.invoke(
        {"input":question},
        config = {"configurable":{"session_id":session_id}}
    )

    results = vectorstore.similarity_search_with_score(question, k=6)
    print(f"question: {question}")
    print(f"answer: {answer}")

    print("\nSources (confidence score — lower = more relevant):")
    for i, (doc,score) in enumerate(results):
        if score < 1.5:
            page = doc.metadata.get("page","unknown")
            source = doc. metadata.get("source","unknown")
            print(f"[{i+1}] | Page: {page} | Source: {source}| Score {score:.4f}")
            print(f"Content: {doc.page_content[:200]}")

def inspect_session(session_id):
    history = store.get(session_id)
    if not history or not history.messages:
        print(f"session {session_id} is empty")
        return {}
    
    messages = history.messages
    total_messages = len(messages)
    
    human_messages = [msg for msg in messages if msg.__class__.__name__ == "HumanMessage"]
    ai_messages = [msg for msg in messages if msg.__class__.__name__ == "AIMessage"]
    first_question = human_messages[0].content if human_messages else "No questions asked"
    last_answer = ai_messages[-1].content[:200] if ai_messages else "No answers given"

    return {
        "session ID": session_id,
        "total messages": total_messages,
        "Human Messages": len(human_messages),
        "AI Messages": len(ai_messages),
        "first question": first_question,
        "last answer": last_answer
    }

if __name__ == "__main__":
    print("-------MultiPDF with Score----------")
    
    session_id = input("please enter your name: ")
    print(f"Welcome {session_id}")
    print("type 'quit' to exit")

    while True:
        question = input("please enter your question: ")
        if question.lower() == "quit":
            break
        ask(session_id, question)

    print("----------SESSION SUMMARY----------")
    print(json.dumps(inspect_session(session_id), indent = 4))