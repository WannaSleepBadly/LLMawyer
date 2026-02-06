from pydantic import BaseModel, Field


class IsGroundedOnFacts(BaseModel):
    """
    Схема вывода для проверки, является ли вопрос галлюцинацией (узел answer_validation)
    """

    grounded_on_facts: bool = Field(
        description="Ответ основан на фактах, 'да' или 'нет'"
    )
    explanation: str = Field(
        description="Объяснение, почему вопрос не основан на фактах"
    )


class FullAnswer(BaseModel):
    """
    Схема вывода для проверки полноты полученного ответа (узел answer_validation)
    """

    is_answered: bool = Field(description="Двоичный результат: был ли вопрос отвечен")
    explanation: str = Field(description="Объяснение, почему вопрос не отвечен")


class QuestionAnswer(BaseModel):
    """
    Схема вывода для проверки, можно ли ответить на вопрос из предоставленных фактов (узел direct_answer)
    """

    can_be_answered: bool = Field(
        description="Двоичный результат: можно ли полностью ответить на вопрос"
    )
    explanation: str = Field(
        description="Объяснение, почему на вопрос можно или нельзя полностью ответить"
    )


class QuestionAnswerFromContext(BaseModel):
    """
    Схема вывода цепочки размышлений над ответом (узел reasoning_chain)
    """

    thoughts: str = Field(description="Цепочка размышлений")
    answer: str = Field(description="Финальный вывод")


class RelevantContent(BaseModel):
    """
    Схема вывода для фильтрации релевантной дополнительной информации (узел relevant_filter)
    """

    relevant_content: str = Field(
        description="Релевантное содержимое из найденных документов, относящееся к запросу."
    )


class RewriteQuestion(BaseModel):
    """
    Схема вывода для переформулированного вопроса (узел rewrite)
    """

    rewritten_question: str = Field(
        description="Улучшенный вопрос, оптимизированный для поиска в векторном хранилище."
    )
    explanation: str = Field(description="Объяснение переформулированного вопроса.")


class SearchDecision(BaseModel):
    """
    Схема вывода для определения, нужен ли поиск в интернете (узел search_required)
    """

    need_web_search: bool = Field(
        description="True, если для ответа нужен поиск в Интернете"
    )
    explanation: str = Field(description="Объяснение решения")


class IsLegalQuestion(BaseModel):
    """
    Схема вывода для валидации, относится ли вопрос к юридической тематике (узел topic_validation)
    """

    is_legal: bool = Field(
        description="True, если вопрос относится к правовой сфере, иначе False"
    )
    explanation: str = Field(
        description="Объяснение, почему вопрос относится или не относится к правовой сфере"
    )


class WebSearchResult(BaseModel):
    """
    Схема вывода для поиска в интернете (узел web_search)
    """

    query: str = Field(
        description="Сформулированный поисковый запрос для поиска законодательства"
    )
    results: str = Field(description="Результаты поиска в сети")


class TavilyInput(BaseModel):
    """Входные данные для поискового запроса."""

    query: str = Field(description="Текст поискового запроса")
