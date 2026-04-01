import argparse
import os
import logging
from enum import Enum, auto
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from PromtBuilder import PromtBuilder

class RAGBot:
    DB_PATH = "../faiss_db"

    DEFAULT_MAX_DOCUMENTS = 42

    def __init__(
        self,
        setup_dir: str = ""
    ):
        self.current_dir = setup_dir or os.path.dirname(os.path.abspath(__file__))

        self.vector_db = self._load_db()
        self.ollama = OllamaLLM(model="llama3.1")
        self.prompts = PromtBuilder().Prompts

    def search_documents(self, query: str) -> list[Document]:
        results = self.vector_db.similarity_search(
            query, k=40, fetch_k=25000
        )

        return results

    def format_context(self, documents: list[Document]) -> str:
        if not documents:
            print("No document in db.")
            return

        context = []
        for i, doc in enumerate(documents, 1):
            context.append(
                f"""
                Chunk: {doc.metadata.get("chunk_id", "N/A")}
                Content:
                {doc.page_content}
                """
            )

        return "\n".join(context)

    def ask(self, question: str, prompt_type: str = "base"):
        print(f"Got query :`{question}`.")
        documents = self.search_documents(question)
        context = self.format_context(documents)

        chain = (
            {"context": lambda x: x["context"], "question": lambda x: x["question"]}
            | self.prompts[prompt_type]
            | self.ollama
            | StrOutputParser()
        )

        response = chain.invoke({"context": context, "question": question})
        print(f"Response: '{response}'.\n")

        return {
            "query": question,
            "prompt_type": prompt_type,
            "response": response,
            "context": context,
            "prompt": self.prompts[prompt_type].format(context=context, question=question),
            "sources": [
                {
                    "source": doc.metadata.get("source", "Неизвестный источник"),
                    "category": doc.metadata.get("category", "Неизвестная категория"),
                    "chunk_id": doc.metadata.get("chunk_id", "N/A"),
                    "content_preview": f"{doc.page_content[:200]}...",
                }
                for doc in documents
            ],
            "num_sources": len(documents),
        }
        
    def _load_db(self):
        embeddings = HuggingFaceEmbeddings(
            model_name="all-mpnet-base-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        return FAISS.load_local(
            folder_path=self.DB_PATH,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
