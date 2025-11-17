import csv

from LLMawyer.ML.llm_api import OllamaClient
from LLMawyer.parser.config import get_db_manager
from LLMawyer.parser.models import Law, LawChapter, LawParagraph, LawPart

OUTPUT_CSV = "tests/qa_dataset.csv"

QUESTIONS_PER_PARAGRAPH = 2
MIN_ROWS = 15


def write_batch_to_csv(batch):
    """Дозапись пачки строк в CSV."""
    file_exists = False
    try:
        with open(OUTPUT_CSV, "r", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(OUTPUT_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "law_id",
                "law_name",
                "chapter_id",
                "chapter_title",
                "part_id",
                "part_title",
                "paragraph_id",
                "paragraph_text",
                "question",
            ],
        )
        if not file_exists:
            writer.writeheader()

        writer.writerows(batch)


def generate_question(context: dict) -> str:
    """
    context = {
        "law_name": ...,
        "chapter_title": ...,
        "part_title": ...,
        "paragraph_text": ...
    }
    """

    prompt = f"""
    Ты — человек без юридического образования, который пытается понять федеральный закон.

    Твоя задача — прочитать информацию о законе ниже и сформулировать один естественный вопрос от лица обычного гражданина.
    Вопрос должен быть:
    - конкретным
    - практическим
    - отражающим реальную проблему или ситуацию
    - не юридическим термином, а человеческим языком
    - не должен быть общим ("что регулирует закон?", "какова цель закона?" — такие вопросы запрещены)
    - если вопрос по конкретному закону, то вопрос должен содержать краткое название закона

    Игнорируй параграфы, которые описывают:
    - цели закона
    - задачи регулирования
    - общие положения
    - предмет регулирования
    - что закон устанавливает или определяет

    Если параграф относится к этим категориям — ответь "SKIP".

    ---
    Название закона: {context['law_name']}
    Глава: {context['chapter_title']}
    Статья: {context['part_title']}
    Текст параграфа: {context['paragraph_text']}

    Ответ: только вопрос или SKIP.
    """

    system_message = {"role": "system", "content": prompt}

    messages = [system_message]

    result = ollama_client.create_chat_completion(messages=messages)

    # удаляем возможные маркеры, точки и т.п.
    return result.replace("\n", " ").strip()


def main():
    # Создаем сессию
    session = db_manager.get_session()

    paragraphs = (
        session.query(LawParagraph)
        .join(LawPart, LawParagraph.part_id == LawPart.part_id)
        .join(LawChapter, LawPart.chapter_id == LawChapter.chapter_id)
        .join(Law, LawChapter.law_id == Law.law_id)
        .all()
    )

    print(f"Всего параграфов в базе: {len(paragraphs)}")

    valid_rows = 0
    batch = []

    for p in paragraphs:
        part = p.part
        chapter = part.chapter
        law = chapter.law

        context = {
            "law_id": law.law_id,
            "law_name": law.name,
            "chapter_id": chapter.chapter_id,
            "chapter_title": chapter.title,
            "part_id": part.part_id,
            "part_title": part.title,
            "paragraph_id": p.paragraph_id,
            "paragraph_text": p.content.strip(),
        }

        for _ in range(QUESTIONS_PER_PARAGRAPH):
            try:
                question = generate_question(context)
            except Exception as e:
                print(f"Ошибка LLM: {e}")
                continue

            if question.upper() == "SKIP":
                continue

            batch.append(
                {
                    "law_id": context["law_id"],
                    "law_name": context["law_name"],
                    "chapter_id": context["chapter_id"],
                    "chapter_title": context["chapter_title"],
                    "part_id": context["part_id"],
                    "part_title": context["part_title"],
                    "paragraph_id": context["paragraph_id"],
                    "paragraph_text": context["paragraph_text"],
                    "question": question,
                }
            )

            valid_rows += 1

            print(f"Question {valid_rows}: {question}")
            print("------------------------------------------")

            if len(batch) == 10:
                # Сохранение
                write_batch_to_csv(batch)
                batch.clear()

        if valid_rows >= MIN_ROWS:
            break

    print(f"Сгенерировано: {valid_rows} записей")
    print(f"CSV сохранён: {OUTPUT_CSV}")


if __name__ == "__main__":
    db_manager = get_db_manager()
    ollama_client = OllamaClient()
    main()
