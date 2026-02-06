from ..agent_dependencies import create_node_chain, logger
from ..prompts.topic_validation import TOPIC_VALIDATION_PROMPT_TEMPLATE
from ..schemas import IsLegalQuestion


def TopicValidationNode(state: dict) -> dict:
    """
    Проверяет, относится ли вопрос к правовой сфере.

    args:
        state (dict): Словарь с ключом "question" (вопрос пользователя)

    returns: словарь с ключом "route", принимающем значение "is_legal" или "not_legal"
    """
    question = state["question"]
    input_data = {"question": question}

    logger.info("Проверяем, относится ли вопрос к правовой сфере.")

    topic_validation_chain = create_node_chain(
        node_schema=IsLegalQuestion,
        node_prompt_template=TOPIC_VALIDATION_PROMPT_TEMPLATE,
        input_variables=["question"],
    )

    output = topic_validation_chain.invoke(input_data)
    route = "is_legal" if output.is_legal else "not_legal"

    res = "Вопрос правовой" if output.is_legal else "Вопрос не является правовым"
    logger.info(res)

    return {**state, "route": route}


def RejectionNode(state):
    """
    Сообщение, выводимое при вопросе не из правовой сферы
    """
    return {
        "message": "Извини, я работаю только с вопросами правовой тематики.",
        "question": state["question"],
    }
