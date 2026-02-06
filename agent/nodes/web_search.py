from ..agent_dependencies import create_node_chain, get_search_tool, logger
from ..prompts.web_search import WEB_SEARCH_PROMPT_TEMPLATE
from ..schemas import WebSearchResult


def WebSearchNode(state: dict) -> dict:
    """
    Выполняет поиск нужной информации в интернете

    args:
        state (dict): Словарь, содержащий:
            - "question": Вопрос для ответа.

    returns:
        dict: Словарь, содержащий:
            - "content": найденная агрегированная информация
            - "question": Исходный вопрос.
    """
    question = state["question"]

    # Сначала формируем поисковый запрос через LLM
    web_search_chain = create_node_chain(
        node_schema=WebSearchResult,
        node_prompt_template=WEB_SEARCH_PROMPT_TEMPLATE,
        input_variables=["question"],
    )
    logger.info("Начинаем поиск в интернете")
    search_output = web_search_chain.invoke({"question": question})
    query = search_output.query
    logger.info(f"Поисковой запрос: {query}")

    # Затем вызываем TravilySearch
    search_tool = get_search_tool()
    results = search_tool.invoke({"query": query})

    context = "\n\n".join(
        f"Источник {i+1}:\n{item.get('content', '')}"
        for i, item in enumerate(results)
        if item.get("content")
    )

    logger.info(f"Результаты поиска: {context}")

    return {
        "query": query,
        "results": results,
        "context": context,
        "question": question,
    }
