import json
import os
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


class Indexer:
    DB_PATH = "faiss_db"
    KB_PATH = "knowledge_base"

    def __init__(self, setup_dir: str | None = None):

        self.current_dir = setup_dir or os.path.dirname(os.path.abspath(__file__))
        self.faiss_db_dir = os.path.join(self.current_dir, self.DB_PATH)

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-mpnet-base-v2",
            model_kwargs={"device": "cpu"},  # Используем CPU для совместимости
            encode_kwargs={"normalize_embeddings": True},
        )

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=200)

        self.documents = list[Document]()
        self.chunks = list[Document]()

    def load_knowledge_base(self):
        for address, _, files in os.walk(self.KB_PATH):
            for filename in files:
                file_path = os.path.join(address, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if not content:
                        continue

                    relative_path = file_path.replace(self.KB_PATH, "")

                    metadata = {
                        "source": str(relative_path),
                        "filename": filename,
                        "file_path": str(file_path),
                        "file_size": len(content),
                    }
                    doc = Document(page_content=content, metadata=metadata)
                    self.documents.append(doc)
                    print(f"Added to base : {filename}.")

                except Exception as error:
                    print(f"Failed reading {file_path}:", error)
        for doc in self.documents:
            chunks = self.text_splitter.split_documents([doc])
            filtered_chunks = []
            for i, chunk in enumerate(chunks):
                if len(chunk.page_content.strip()) < 100:
                    continue

                chunk.metadata.update(
                    {
                        "chunk_id": f"{doc.metadata['filename']}_{i}",
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                )
                filtered_chunks.append(chunk)

            self.chunks.extend(filtered_chunks)

        print(f"Loaded knowledge base with {len(self.chunks)} chunks.")

    def create_faiss_index(self) -> FAISS:        
        faiss_index = FAISS.from_documents(documents=[self.chunks[0]], embedding=self.embeddings)
        self.add_chunks_to_index(faiss_index, self.chunks[1:])

        os.makedirs(self.faiss_db_dir, exist_ok=True)
        faiss_index.save_local(self.faiss_db_dir)

        return faiss_index

    def add_chunks_to_index(self, faiss_index: FAISS, chunks: list[Document]):
        total = len(chunks)
        for i in tqdm(range(total), total=total, desc="Index FAISS"):
            faiss_index.add_documents([self.chunks[i]])
