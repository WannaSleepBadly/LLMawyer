from ..agent_dependencies import create_node_chain, logger
from ..prompts.answer_validation import (
    IS_ANSWERED_PROMPT_TEMPLATE,
    IS_GROUNDED_ON_FACTS_PROMPT_TEMPLATE,
)
from ..schemas import FullAnswer, IsGroundedOnFacts


def AnswerValidationNode(state: dict) -> dict:
    """
    Проверяет, является ли ответ полным и основанным на найденной информации (не галлюцинация)

    args:
        state (dict): - состояние агента
            - "context": Найденная информация, использованная при ответе на вопрос
            - "question": Вопрос пользователя
            - "answer": Сгенерированный ответ

    returns:
        dict: изменённое состояние с ключом "route": ответ прошёл проверки,"useful", или не,"not useful"
    """

    context = state["context"]
    answer = state["answer"]
    question = state["question"]

    logger.info("Проверяем, является ли ответ галлюцинацией")

    is_grounded_on_facts_chain = create_node_chain(
        node_schema=IsGroundedOnFacts,
        node_prompt_template=IS_GROUNDED_ON_FACTS_PROMPT_TEMPLATE,
        input_variables=["context", "answer"],
    )

    result = is_grounded_on_facts_chain.invoke({"context": context, "answer": answer})
    grounded_on_facts = result.grounded_on_facts

    if not grounded_on_facts:
        logger.info(f"Ответ галлюцинация. {result.explanation}")
        route = "hallucination"
    else:
        logger.info(f"Ответ не галлюцинация. {result.explanation}")

        input_data = {"question": question, "answer": answer}

        logger.info("Проверяем, полностью ли ответ покрывает вопрос.")

        is_answered_chain = create_node_chain(
            node_schema=FullAnswer,
            node_prompt_template=IS_ANSWERED_PROMPT_TEMPLATE,
            input_variables=["question", "context"],
        )

        output = is_answered_chain.invoke(input_data)
        is_answered = output.is_answered

        if is_answered:
            logger.info(f"Ответ соответствует вопросу. {output.explanation}")
            route = "useful"
        else:
            logger.info(f"Ответ не соответствует вопросу. {output.explanation}")
            route = "not_useful"

    return {**state, "route": route}
