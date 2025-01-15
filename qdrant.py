
from init import collection_name, modelEmbed, client

def find_answer(question: str, top_k: int = 1):
    """Пошук відповіді на питання"""
    # Створюємо ембедінг для питання
    vector = modelEmbed.encode(question).tolist()
    print(f"Вектор запитання: {vector}")

    # Шукаємо найбільш схожі питання
    results = client.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=top_k
    )
    print(f"Запитання: {question}\nВідповідь: {results}")
    return results
