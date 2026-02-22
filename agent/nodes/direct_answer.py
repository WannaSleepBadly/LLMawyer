from ..agent_dependencies import create_node_chain, logger
from ..prompts.direct_answer import CAN_BE_ANSWERED_PROMPT_TEMPLATE
from ..schemas import QuestionAnswer


def DirectAnswerNode(state: dict) -> dict:
    """
    Определяет, можно ли сформировать корректный ответ на вопрос на основе предоставленных данных,
    или нужно повторить поиск

    args:
        state (dict) - состояние агента:
            - "question": вопрос пользователя
            - "context": данные для ответа (локальная база или результаты веб поиска)

    returns: dict: изменённое состояние с ключом "route": "can_be_answered", если дополнительный поиск не нужен,
    или "can_not_be_answered" в противоположном случае
    """
    question = state["question"]
    context = state.get("context", "")

    input_data = {"question": question, "context": context}

    logger.info("Определяем, можно ли дать прямой ответ на вопрос...")

    can_be_answered_chain = create_node_chain(
        node_schema=QuestionAnswer,
        node_prompt_template=CAN_BE_ANSWERED_PROMPT_TEMPLATE,
        input_variables=["question", "context"],
    )

    output = can_be_answered_chain.invoke(input_data)

    route = "can_be_answered" if output.can_be_answered else "can_not_be_answered"

    result = (
        "Можно ответить, поиск не нужен"
        if output.can_be_answered
        else "Ответить нельзя, нужен дополнительный поиск"
    )
    logger.info(f"{result}. {output.explanation}")

    return {**state, "route": route}
