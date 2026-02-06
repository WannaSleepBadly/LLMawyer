from ..agent_dependencies import create_node_chain, logger
from ..prompts.reasoning_chain import QUESTION_ANSWER_COT_PROMPT_TEMPLATE
from ..schemas import QuestionAnswerFromContext


def ReasoningChainNode(state: dict) -> dict:
    """
    Отвечает на вопрос, используя предоставленный контекст и цепочку рассуждений.

    args:
        state (dict): Словарь, содержащий:
            - "question": Вопрос для ответа.
            - "context": Контекст для ответа.

    returns:
        dict: Словарь, содержащий:
            - "answer": Ответ на вопрос на основе контекста.
            - "context": Использованный контекст.
            - "question": Исходный вопрос.
    """

    question = state["question"]
    context = state.get("context", "")

    input_data = {"question": question, "context": context}

    logger.info("Отвечаем на вопрос, используя извлечённый контекст...")

    question_answer_from_context_cot_chain = create_node_chain(
        node_schema=QuestionAnswerFromContext,
        node_prompt_template=QUESTION_ANSWER_COT_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    output = question_answer_from_context_cot_chain.invoke(input_data)
    answer = output.answer
    thoughts = output.thoughts

    logger.info(f"Полученный цепочкой рассуждений ответ: {answer}")

    return {
        "answer": answer,
        "thoughts": thoughts,
        "context": context,
        "question": question,
    }
