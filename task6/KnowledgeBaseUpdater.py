import logging
import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document


class KnowledgeBaseUpdater:
    SOURCE = "https://narnia.fandom.com"
    
    def __init__(self, api_url: str = f"{SOURCE}/api.php"):
        self.api_url = api_url
        self.category = "Category:Characters"
        self.base_wiki = f"{SOURCE}/wiki/"
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.chunk_size = 1000
        self.chunk_overlap = 100
        self.faiss_db_path = "./faiss_db"
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
        self.log = logging.getLogger(__name__)

    def _fetch_category_pages(self) -> List[str]:
        titles = []
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": self.category,
            "cmlimit": 500,
            "format": "json"
        }
        while True:
            resp = requests.get(self.api_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            titles.extend(p["title"] for p in data.get("query", {}).get("categorymembers", []))
            if "continue" not in data:
                break
            params.update(data["continue"])
        self.log.info(f"Fetched {len(titles)} pages")
        return titles

    def _fetch_page_content(self, title: str) -> Optional[str]:
        params = {
            "action": "parse",
            "page": title,
            "format": "json",
            "prop": "text",
            "disableeditsection": True,
            "disabletoc": True
        }
        try:
            resp = requests.get(self.api_url, params=params, timeout=30)
            resp.raise_for_status()
            html = resp.json().get("parse", {}).get("text", {}).get("*", "")
            if not html:
                return None
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["table", "div.hatnote", "span.mw-editsection"]):
                tag.decompose()
            text = soup.get_text(" ")
            return " ".join(text.split())
        except Exception:
            return None

    def _load_documents(self, titles: List[str]) -> List[Document]:
        docs = []
        for t in tqdm(titles, desc="Fetching pages"):
            content = self._fetch_page_content(t)
            if content:
                docs.append(Document(
                    page_content=content,
                    metadata={"source": t, "url": self.base_wiki + t.replace(" ", "_")}
                ))
        self.log.info(f"Loaded {len(docs)} documents")
        return docs

    def _split_documents(self, docs: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(docs)
        self.log.info(f"Created {len(chunks)} chunks")
        return chunks

    def _build_faiss_db(self, chunks: List[Document]) -> FAISS:
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(self.faiss_db_path)
        self.log.info(f"Saved index to {self.faiss_db_path}")
        return vectorstore

    def run(self) -> bool:
        self.log.info("Starting update")
        try:
            titles = self._fetch_category_pages()
            docs = self._load_documents(titles)
            chunks = self._split_documents(docs)
            self._build_faiss_db(chunks)
            self.log.info(f"Update completed successfully by {chunks.count} chunks.")
            return True
        except Exception as e:
            self.log.error(f"Update failed: {e}")
            return False
        