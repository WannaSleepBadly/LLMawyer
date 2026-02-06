from ..agent_dependencies import create_node_chain, logger
from ..prompts.rewrite import REWRITE_PROMPT_TEMPLATE
from ..schemas import RewriteQuestion


def RewriteNode(state):
    """
    Переформулирует вопрос для оптимизации поиска в векторном хранилище.

    args:
        state (dict): Словарь с исходным вопросом, ключ "question".

    returns:
        dict: Словарь с переформулированным вопросом под ключом "question".
    """

    question = state["question"]

    logger.info("Переформулируем вопрос.")

    question_rewriter = create_node_chain(
        node_schema=RewriteQuestion,
        node_prompt_template=REWRITE_PROMPT_TEMPLATE,
        input_variables=["question"],
    )

    result = question_rewriter.invoke({"question": question})
    new_question = result.rewritten_question
    logger.info(f"Новый вопрос: {new_question}")
    return {"question": new_question}
