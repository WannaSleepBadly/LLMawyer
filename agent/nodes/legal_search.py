from ..agent_dependencies import get_retriever, logger


def LegalSearchNode(state):
    """
    Получение релевантных вопросу пунктов законодательства

    args:
        state (dict) - состояние агента:
            - "question": вопрос пользователя

    returns:
        dict: изменённое состояние с ключом "context" - полученные пункты законодательства
        и "retrieved_docs" - список документов с метаданными для форматирования ответа
    """
    question = state["question"]

    logger.info("Получение релевантных параграфов...")
    retriever = get_retriever()
    docs = retriever.invoke(
        question
    )  # List[Document(metadata={'paragraph_id': ...}, page_content='...')]

    # Формируем контекст из содержимого документов
    context = "\n\n".join(doc.page_content for doc in docs)

    logger.info(f"Найдено {len(docs)} фрагментов законодательства")

    return {"context": context, "question": question, "retrieved_docs": docs}
