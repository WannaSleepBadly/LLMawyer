import aiohttp
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from urllib.parse import urljoin, urlparse, urlunparse

import asyncio
import re
import json
from typing import List, Dict, Optional, Tuple


class LegalContentScraper:
    """
    Парсер КонсультантПлюс для получения текстов законов
    """

    def __init__(self, timeout_sec: int = 20, max_retries: int = 3):
        self.timeout = timeout_sec
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self.seen_urls = set()

    async def _create_session(self) -> aiohttp.ClientSession:
        """Создаёт HTTP‑сеанс с рандомным User‑Agent"""

        headers = {
            "User-Agent": UserAgent().random,
            "Accept-Language": "ru-RU,ru;q=0.9",
        }
        return aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout))

    async def _request(self, url: str) -> str:
        """Выполняет HTTP‑запрос с повторными попытками"""

        if not self._session:
            self._session = await self._create_session()

        for attempt in range(self.max_retries):
            try:
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                await asyncio.sleep((attempt + 1) * 1.0)

    def _extract_nav_structure(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Формирует дерево глав и статей из навигационных ссылок"""

        chapters = []
        current_chapter = None

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if not href.startswith("/document/cons_doc_LAW_"):
                continue

            title = " ".join(link.get_text(" ", strip=True).split())
            if not title:
                continue

            url = urljoin(base_url, href.split("#")[0])

            # Нормализуем url
            parsed = urlparse(url.lower())
            # Удаляем якоря и несущественные параметры
            clean_path = parsed.path.rstrip("/")
            normalized_url = urlunparse((parsed.scheme, parsed.netloc, clean_path, "", "", ""))

            if normalized_url in self.seen_urls:
                continue
            self.seen_urls.add(normalized_url)

            # Если это глава
            if title.startswith("Глава"):
                # Добавляем в закон новую главу
                current_chapter = {
                    "title": title,
                    "source_url": url,
                    "articles": [],
                }
                chapters.append(current_chapter)
            # Если это статья
            elif title.startswith("Статья"):
                # В законе нет глав
                if not current_chapter:
                    current_chapter = {
                        # TODO: При выводе сообщения бота учесть, что Глава 0 - это заглушка
                        "title": "Глава 0. Общие положения",
                        "source_url": base_url,
                        "articles": [],
                    }
                    chapters.append(current_chapter)
                # Добавляем в статью новые главы
                current_chapter["articles"].append({"title": title, "source_url": url})
            # TODO: Обработка изменяющих законов и обзора изменений

        return chapters

    @staticmethod
    def _sanitize_node(node: Tag, remove_tags: List[str], remove_classes: List[str]) -> None:
        """Удаляет нежелательные элементы из DOM‑узла"""

        for selector in remove_classes:
            for el in node.select(selector):
                el.decompose()
        for tag in remove_tags:
            for el in node.find_all(tag):
                el.decompose()

    def _clean_text_content(self, node: Tag) -> str:
        """Очищает текст от лишних тэгов"""

        self._sanitize_node(
            node,
            remove_tags=["script", "style", "noscript"],
            remove_classes=[
                ".info-link",
                ".document__insert",
                ".document__edit",
                ".dnk-button-dummy",
                ".document-page__balloon",
                ".full-text",
                ".document-page__banner-middle",
            ],
        )
        lines = [line.strip() for line in node.get_text("\n").split("\n") if line.strip()]
        return "\n".join(lines).strip()

    @staticmethod
    def _split_into_paragraphs(text: str) -> List[Dict[str, str]]:
        """Разделение текста статьи на пункты и подпункты"""

        paragraphs = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        current_paragraph = None  # номер текущего основного пункта (например, "4")
        current_content = []  # накапливаемый текст основного пункта (до появления подпунктов)
        subitems = []  # список подпунктов: [{"number": "4.1", "content": "..."}, ...]

        # Регулярное выражение для основного пункта:
        # - начинается с начала строки
        # - содержит цифры, точки, дефисы (например, 3.13-1, 4.1, 5)
        # - после номера идёт точка и пробел/текст
        main_paragraph_pattern = r'^(?!\s*[#.).]\s*)(\d+(?:[.\-]\d+)*)\.\s+(.*)'
        #main_paragraph_pattern = r'^\s*(\d+(?:[.\-]\d+)*)\.\s+(.*)'

        # Регулярное выражение для подпункта:
        # - начинается с начала строки
        # - содержит номер/букву + скобку (1), а), i))
        subitem_pattern = r'^\s*([0-9]+)\)\s+(.*?)\s*$'
        #subitem_pattern = r'^\s*([а-яА-Я0-9]+)\)\s+(.*)'

        for line in lines:
            main_match = re.match(main_paragraph_pattern, line)
            subitem_match = re.match(subitem_pattern, line)
            if main_match:
                # Новый основной пункт — сохраняем всё предыдущее
                if current_paragraph is not None:
                    if subitems:
                        paragraphs.extend(subitems)
                    else:
                        current_content = " ".join(current_content).strip()
                        paragraphs.append({
                            "number": current_paragraph,
                            "content": current_content
                        })

                # Начинаем новый основной пункт
                current_paragraph = main_match.group(1)
                current_content = [main_match.group(2)] if main_match.group(2) else []
                subitems = []  # сбрасываем подпункты

            elif subitem_match:
                # Обрабатываем текущий подпункт
                subitem_num = subitem_match.group(1)
                subitem_text = subitem_match.group(2)

                # Определяем порядковый номер подпункта (1, 2, 3... или а, б, в...)
                try:
                    subitem_idx = int(subitem_num)  # если число — используем как индекс
                except ValueError:
                    subitem_idx = ord(subitem_num.lower()) - ord('а') + 1  # для букв: а→1, б→2...

                # Делаем номер подпункта составным
                subitem_full_number = f"{current_paragraph}. Подпункт {subitem_idx}"

                # Для каждого подпункта записываем текст главного пункта
                subitem_text = " ".join(current_content).strip() + subitem_text
                subitems.append({
                    "number": subitem_full_number,
                    "content": subitem_text
                })

            else:
                # Продолжение текста (не начало нового пункта/подпункта)
                if current_paragraph is not None:
                    if subitems:
                        # Добавляем к последнему подпункту
                        if subitems[-1]["content"]:
                            subitems[-1]["content"] += " " + line
                        else:
                            subitems[-1]["content"] = line
                    else:
                        # Добавляем к основному пункту
                        current_content.append(line)

        # Сохраняем последний пункт/подпункты
        if current_paragraph is not None:
            if subitems:
                paragraphs.extend(subitems)
            else:
                current_content = " ".join(current_content).strip()
                paragraphs.append({
                    "number": current_paragraph,
                    "content": current_content
                })

        # В тексте статьи нет подпунктов
        if not paragraphs:
            lines = [line for line in lines if 'Статья' not in line]
            lines = " ".join(lines)
            paragraphs = [
                {"number": "",
                 "content": lines}
            ]
        return paragraphs

    async def scrape_article(self, article_url: str) -> Dict[str, str]:
        """Парсинг отдельной статьи"""

        html = await self._request(article_url)
        soup = BeautifulSoup(html, "lxml")

        content_root = soup.select_one(".document-page__content") or soup

        text = self._clean_text_content(content_root)

        return {
            "text": text,
            "source_url": article_url,
        }

    async def scrape_law(self, law_url: str) -> list[dict[str, str | list[dict]]]:
        """Парсинг одного закона."""

        print(f"[INFO] Обработка закона: {law_url}")
        html = await self._request(law_url)
        soup = BeautifulSoup(html, "lxml")

        # Определение названия закона
        title_el = soup.select_one(".document-page__content .doc-style h1")
        title = title_el.get_text(" ", strip=True) if title_el else (
            soup.title.get_text(" ", strip=True) if soup.title else law_url)
        title = title.replace(" \ КонсультантПлюс", "")

        # Определение номера закона
        pattern = r'N\s*(\d+-ФЗ)'
        match = re.search(pattern, title, re.IGNORECASE)
        code = match.group(1) if match else None

        # TODO сохранение аннотации закона (текст перед главами и статьями)
        law = {"title": title,
               "source_url": law_url,
               "code": code}

        structure = self._extract_nav_structure(soup=soup, base_url=law_url)
        for chapter in structure:
            print(f"  → Глава: {chapter['title']}")
            articles = []
            for article in chapter["articles"]:
                print(f"    ➜ Статья: {article['title']}")
                if 'утратила силу' not in article['title'].lower():
                    a_data = await self.scrape_article(article["source_url"])
                    paragraphs = self._split_into_paragraphs(a_data["text"])
                    article['paragraphs'] = paragraphs
                    articles.append(article)

            chapter["articles"] = articles

        structure = [chapter for chapter in structure if not 'утратила силу' in chapter['title'].lower()]
        law['chapters'] = structure

        print(f"[SUCCESS] Закон {law_url} обработан.\n")
        return [law]

    async def scrape_multiple_laws(self, urls: List[str]) -> List[Dict]:
        """Асинхронно обрабатывает несколько законов."""

        print(f"[INFO] Запущен парсинг {len(urls)} законов.")
        tasks = [self.scrape_law(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Фильтруем исключения
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[ERROR] Ошибка при парсинге {urls[i]}: {result}")
            else:
                valid_results.extend(result)

        return valid_results

    async def close(self):
        """Закрывает HTTP‑сеанс."""
        if self._session:
            await self._session.close()
            self._session = None


async def main():
    """Точка входа: запускает парсер и обрабатывает заданные URL."""
    # TODO Добавить ФЗ о СМИ, банкротстве, перрсональных данных
    urls = [
         "https://www.consultant.ru/document/cons_doc_LAW_58968/",  # О рекламе
         "https://www.consultant.ru/document/cons_doc_LAW_305/",    # О защите прав потребителей
         "https://www.consultant.ru/document/cons_doc_LAW_61763/",  # О защите конкуренции
         "https://www.consultant.ru/document/cons_doc_LAW_61798/",  # Об информации, ИТ и защите информации
    ]

    scraper = LegalContentScraper(timeout_sec=25, max_retries=4)
    try:
        results = await scraper.scrape_multiple_laws(urls)
        print(f"\n[DONE] Обработано законов: {len(results)}")

        with open("laws.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[FATAL] Ошибка: {e}")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
