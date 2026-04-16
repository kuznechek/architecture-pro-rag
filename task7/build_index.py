from indexer import Indexer

if __name__ == "__main__":

    indexer = Indexer()
    indexer.load_knowledge_base()
    index = indexer.create_faiss_index()

    print("Done.")
