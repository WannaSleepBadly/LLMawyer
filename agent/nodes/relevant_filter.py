from ..agent_dependencies import create_node_chain, logger
from ..prompts.relevant_filter import RELEVANT_CONTENT_PROMPT_TEMPLATE
from ..schemas import RelevantContent


def RelevantFilterNode(state: dict) -> dict:
    """
    Фильтрует и сохраняет только ту информацию, которая является релевантной вопросу пользователя.

    args:
        state (dict): словарь, содержащий:
            - "question": вопрос пользователя.
            - "context": найденные документы в виде строки.

    returns:
        dict: словарь, содержащий:
            - "relevant_context": отфильтрованный релевантный контент.
            - "context": исходный контекст (документы).
            - "question": исходный вопрос.
    """
    question = state["question"]
    context = state["context"]

    input_data = {"query": question, "retrieved_documents": context}

    logger.info("Оставляю только релевантный контент...")

    relevant_content_chain = create_node_chain(
        node_schema=RelevantContent,
        node_prompt_template=RELEVANT_CONTENT_PROMPT_TEMPLATE,
        input_variables=["query", "retrieved_documents"],
    )

    output = relevant_content_chain.invoke(input_data)
    relevant_content = output.relevant_content
    relevant_content = "".join(relevant_content)

    logger.info(f"Оставленный контент: {relevant_content}")

    return {
        "relevant_context": relevant_content,
        "context": context,
        "question": question,
    }
