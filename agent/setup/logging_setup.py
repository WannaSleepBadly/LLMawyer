import os

from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler


def setup_langfuse() -> (Langfuse, CallbackHandler):
    """
    Подключение логирования состояний агента в Langfuse
    :return: Клиент и обработчик Langfuse
    """
    Langfuse(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ["LANGFUSE_BASE_URL"],
        timeout=20,
    )

    langfuse = get_client()
    langfuse_handler = CallbackHandler()

    return langfuse, langfuse_handler
