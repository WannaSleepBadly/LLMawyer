from ..agent_dependencies import create_node_chain, logger
from ..prompts.search_required import (
    LEGAL_DB_DESCRIPTION,
    SEARCH_REQUIRED_PROMPT_TEMPLATE,
)
from ..schemas import SearchDecision


def SearchRequiredNode(state: dict) -> dict:
    """
    Решает, поиск будет в интернете или в локальной базе

    args:
        state (dict): Словарь, содержащий:
            - "question": Вопрос для ответа.

    returns:
        dict: Словарь, содержащий:
            - "route": "websearch_needed" для поиска в интернете и "websearch_not_needed" для поиска в локальной базе
            - "question": Исходный вопрос.
    """
    question = state["question"]

    search_required_chain = create_node_chain(
        node_schema=SearchDecision,
        node_prompt_template=SEARCH_REQUIRED_PROMPT_TEMPLATE,
        input_variables=["question", "LEGAL_DB_DESCRIPTION"],
    )

    logger.info("Определяем, где искать информацию для ответа.")
    output = search_required_chain.invoke(
        {"question": question, "LEGAL_DB_DESCRIPTION": LEGAL_DB_DESCRIPTION}
    )

    route = "websearch_needed" if output.need_web_search else "websearch_not_needed"
    result = "Поиск в интернете" if output.need_web_search else "Поиск в локальной базе"
    logger.info(result)
    return {**state, "route": route}
