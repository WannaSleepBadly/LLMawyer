import logging
import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_milvus import Milvus
from langchain_ollama import ChatOllama

from LLMawyer.agent.embedding_service import EmbeddingService
from LLMawyer.agent.schemas import TavilyInput

logger = logging.getLogger("agent")

llm = None
retriever = None
search_tool = None


def get_retriever():
    """Получить или создать retriever для RAG."""
    global retriever
    if retriever is None:
        embeddings = EmbeddingService()
        embeddings.load_model()

        vectorstore = Milvus(
            embedding_function=embeddings,
            connection_args={
                "uri": os.getenv("MILVUS_URI"),
                "token": os.getenv("MILVUS_TOKEN"),
                "db_name": os.getenv("MILVUS_DB_NAME"),
            },
            collection_name=os.getenv("MILVUS_COLLECTION_NAME"),
            index_params={
                "metric_type": os.getenv("MILVUS_METRIC_TYPE"),
                "index_type": os.getenv("MILVUS_INDEX_TYPE"),
                "params": {"nlist": os.getenv("MILVUS_NLIST")},
            },
        )

        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        )
    return retriever


def get_llm():
    """Получить или создать LLM."""
    global llm
    if llm is None:
        model = os.getenv("OLLAMA_MODEL")
        endpoint = os.getenv("OLLAMA_ENDPOINT")
        api = os.getenv("OLLAMA_API")

        logger.info(
            f"Создание LLM: endpoint={endpoint}, model={model}, "
            f"api_key={'*' * 10 if api else 'не задан'}"
        )

        llm = ChatOllama(endpoint=endpoint, model=model, api=api)
    return llm


def get_search_tool():
    """Получить или создать инструмент поиска."""
    global search_tool
    if search_tool is None:

        search_tool = TavilySearchResults(
            max_results=os.getenv("TAVILY_MAX_RESULTS"),
            api_key=os.getenv("TAVILY_API_KEY"),
            args_schema=TavilyInput,
        )
    return search_tool


def create_node_chain(node_schema, node_prompt_template, input_variables):
    """
    Создать цепочку обработки данных в одном узле графа
    :param node_schema: Схема вывода данных
    :param node_prompt_template: Промпт
    :param input_variables: Переменные для подстановки в промпт
    :return:
    """
    llm = get_llm()

    node_parser = JsonOutputParser(pydantic_object=node_schema)
    node_prompt = PromptTemplate(
        template=node_prompt_template,
        input_variables=input_variables,
        partial_variables={
            "format_instructions": node_parser.get_format_instructions()
        },
    )
    node_chain = (
        node_prompt
        | llm.with_structured_output(node_schema)
        # | node_parser
    )

    return node_chain
