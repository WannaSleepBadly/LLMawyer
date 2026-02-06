from typing import TypedDict

from langgraph.graph import END, StateGraph

from .nodes.answer_validation import AnswerValidationNode
from .nodes.direct_answer import DirectAnswerNode
from .nodes.legal_search import LegalSearchNode
from .nodes.reasoning_chain import ReasoningChainNode
from .nodes.relevant_filter import RelevantFilterNode
from .nodes.rewrite import RewriteNode
from .nodes.search_required import SearchRequiredNode
from .nodes.topic_validation import RejectionNode, TopicValidationNode
from .nodes.web_search import WebSearchNode


# Состояние графа
class RetievalAnswerState(TypedDict):
    question: str  # Вопрос пользователя
    context: str  # Агрегированная релевантная вопросу информация
    answer: str  # Ответ агента в данном узле
    retrieved_docs: list  # Список документов с метаданными
    route: str  # Маршрут для условных переходов


def create_agent_graph():
    answer_workflow = StateGraph(RetievalAnswerState)

    # Добавление в граф узлов

    answer_workflow.add_node("TopicValidationNode", TopicValidationNode)

    answer_workflow.add_node("RejectionNode", RejectionNode)

    answer_workflow.add_node("SearchRequiredNode", SearchRequiredNode)

    answer_workflow.add_node("WebSearchNode", WebSearchNode)

    answer_workflow.add_node("LegalSearchNode", LegalSearchNode)

    answer_workflow.add_node("RelevantFilterNode", RelevantFilterNode)

    answer_workflow.add_node("DirectAnswerNode", DirectAnswerNode)

    answer_workflow.add_node("ReasoningChainNode", ReasoningChainNode)

    answer_workflow.add_node("RewriteNode", RewriteNode)

    answer_workflow.add_node("AnswerValidationNode", AnswerValidationNode)

    # Обработка запроса начинается с валидации
    answer_workflow.set_entry_point("TopicValidationNode")

    # Добавление в граф переходов

    answer_workflow.add_conditional_edges(
        "TopicValidationNode",
        lambda state: state["route"],
        {"is_legal": "SearchRequiredNode", "not_legal": "RejectionNode"},
    )

    answer_workflow.add_conditional_edges(
        "SearchRequiredNode",
        lambda state: state["route"],
        {
            "websearch_needed": "WebSearchNode",
            "websearch_not_needed": "LegalSearchNode",
        },
    )

    answer_workflow.add_edge("WebSearchNode", "RelevantFilterNode")

    answer_workflow.add_edge("LegalSearchNode", "RelevantFilterNode")

    answer_workflow.add_edge("RelevantFilterNode", "DirectAnswerNode")

    answer_workflow.add_conditional_edges(
        "DirectAnswerNode",
        lambda state: state["route"],
        {"can_be_answered": "ReasoningChainNode", "can_not_be_answered": "RewriteNode"},
    )

    answer_workflow.add_edge("RewriteNode", "SearchRequiredNode")

    answer_workflow.add_edge("ReasoningChainNode", "AnswerValidationNode")

    answer_workflow.add_conditional_edges(
        "AnswerValidationNode",
        lambda state: state["route"],
        {
            "hallucination": "ReasoningChainNode",
            "not_useful": "RewriteNode",
            "useful": END,
        },
    )

    # Компиляция графа
    agent = answer_workflow.compile()
    return agent
