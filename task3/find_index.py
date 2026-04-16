from indexer import Indexer

tests = [
        "Who is Aragorn?",
        "What is The Fellowship of the Ring?",
        "Tell me about Angmar",
        "What is the famous of Hobbits?"
    ]

if __name__ == "__main__":

    indexer = Indexer()
    indexer.load_knowledge_base()
    index = indexer.create_faiss_index()

    for test in tests:
        print(f"Test is `{test}`")
        results = index.similarity_search(test, k=3)

        for i, result in enumerate(results, 1):
            print(f"Source {i}. {result.metadata['source']}:")
            print(f"{result.page_content[:300]}...\n\n")

    print("Done.")
