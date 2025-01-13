# pip install qdrant-client sentence-transformers numpy

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import numpy as np

# Ініціалізуємо модель для створення ембедінгів
model = SentenceTransformer('all-MiniLM-L6-v2')

# Підключаємося до Qdrant
#client = QdrantClient(path="./qa_storage")
client = QdrantClient(host="localhost", port=6333)
# Створюємо колекцію
collection_name = "orxid_collection"
vectors_config = models.VectorParams(
    size=384,  # Розмірність векторів для all-MiniLM-L6-v2
    distance=models.Distance.COSINE
)

# # Видаляємо стару колекцію якщо існує і створюємо нову
# client.recreate_collection(
#     collection_name=collection_name,
#     vectors_config=vectors_config
# )
#
# # Приклади питань і відповідей
# qa_pairs = [
#     {
#         "question": "Чим займається ательє Орхідея",
#         "answer": "Ательє Орхідея займається пошиттям і ремонтом одягу та прокатом костюмів."
#     },
#     {
#         "question": "Скільки працівників працює в ательє?",
#         "answer": "Станом на 2024 рік в ательє працює 5 майстрів"
#     },
#     {
#         "question": "Який номер телефону ательє?",
#         "answer": "Номер телефону ательє: +380123456789"
#     },
#     {
#         "question": "Де знаходиться ательє Орхідея?",
#         "answer": "Орхідея по вулиці 22 січня"
#     },
#     {
#         "question": "Яка адреса ательє?",
#         "answer": "Орхідея по вулиці 22 січня"
#     },
# ]
#
# # Додаємо пари питання-відповідь до бази
# for i, qa in enumerate(qa_pairs):
#     # Створюємо ембедінг для питання
#     vector = model.encode(qa["question"]).tolist()
#
#     # Додаємо в базу
#     client.upsert(
#         collection_name=collection_name,
#         points=[
#             models.PointStruct(
#                 id=i,
#                 vector=vector,
#                 payload={
#                     "question": qa["question"],
#                     "answer": qa["answer"]
#                 }
#             )
#         ]
#     )

def find_answer(question: str, top_k: int = 1):
    """Пошук відповіді на питання"""
    # Створюємо ембедінг для питання
    vector = model.encode(question).tolist()
    print(vector)

    # Шукаємо найбільш схожі питання
    results = client.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=top_k
    )

    return results

# # Приклад використання
# test_question = "адреса ательє?"
# results = find_answer(test_question, top_k=2)
#
# print(f"Питання: {test_question}\n")
# print("Знайдені відповіді:")
# for i, result in enumerate(results, 1):
#     print(f"\n{i}. Схожість: {result.score:.2f}")
#     print(f"Оригінальне питання: {result.payload['question']}")
#     print(f"Відповідь: {result.payload['answer']}")