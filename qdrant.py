from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from companyInfo import INFO

model = SentenceTransformer('all-MiniLM-L6-v2')

#client = QdrantClient(path="./qa_storage")
client = QdrantClient(host="localhost", port=6333)

collection_name = "orxid_collection"
vectors_config = models.VectorParams(
    size=384,  # Розмірність векторів для all-MiniLM-L6-v2
    distance=models.Distance.COSINE
)

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=vectors_config
)


# Додаємо пари питання-відповідь до бази
for i, qa in enumerate(INFO):
    # Створюємо ембедінг для питання
    vector = model.encode(qa["question"]).tolist()

    # Додаємо в базу
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=i,
                vector=vector,
                payload={
                    "question": qa["question"],
                    "answer": qa["answer"]
                }
            )
        ]
    )

def find_answer(question: str, top_k: int = 1):
    """Пошук відповіді на питання"""
    # Створюємо ембедінг для питання
    vector = model.encode(question).tolist()
    print(f"Вектор запитання: {vector}")


    # Шукаємо найбільш схожі питання
    results = client.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=top_k
    )
    print(f"Запитання: {question}\nВідповідь: {results}")
    return results
