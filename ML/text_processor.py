import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)

class TextProcessor:
    """Класс для обработки транскрибированного текста"""
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "Привет! Рад вас слышать!",
                "Здравствуйте! Как дела?",
                "Привет! Что у вас нового?",
                "Добро пожаловать! Чем могу помочь?"
            ],
            "question": [
                "Интересный вопрос! Дай-ка подумаю...",
                "Хороший вопрос! Сейчас разберусь.",
                "Понял ваш вопрос. Ищу ответ...",
                "Отличный вопрос! Анализирую..."
            ],
            "thanks": [
                "Пожалуйста! Рад был помочь!",
                "Не за что! Обращайтесь еще!",
                "Всегда пожалуйста!",
                "Рад помочь! Удачи!"
            ],
            "default": [
                "Понял вас! Обрабатываю информацию...",
                "Спасибо за сообщение! Анализирую...",
                "Интересно! Работаю над ответом...",
                "Понял! Формирую ответ..."
            ]
        }
    
    def analyze_text(self, text: str) -> str:
        """
        Анализирует транскрибированный текст и определяет тип сообщения
        
        Args:
            text (str): Транскрибированный текст
            
        Returns:
            str: Тип сообщения для выбора соответствующего ответа
        """
        text_lower = text.lower().strip()
        
        # Ключевые слова для определения типа сообщения
        greeting_words = ["привет", "здравствуйте", "добро", "добрый", "hi", "hello"]
        question_words = ["как", "что", "где", "когда", "почему", "зачем", "?", "вопрос"]
        thanks_words = ["спасибо", "благодарю", "thanks", "thank you"]
        
        if any(word in text_lower for word in greeting_words):
            return "greeting"
        elif any(word in text_lower for word in question_words):
            return "question"
        elif any(word in text_lower for word in thanks_words):
            return "thanks"
        else:
            return "default"
    
    def generate_response(self, transcribed_text: str) -> str:
        """
        Генерирует ответ на основе транскрибированного текста
        
        Args:
            transcribed_text (str): Транскрибированный текст
            
        Returns:
            str: Сгенерированный ответ
        """
        try:
            # Анализируем текст
            text_type = self.analyze_text(transcribed_text)
            
            # Выбираем случайный ответ соответствующего типа
            response = random.choice(self.responses[text_type])
            
            logger.info(f"Сгенерирован ответ типа '{text_type}' для текста: {transcribed_text[:50]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return random.choice(self.responses["default"])
    
    def format_transcription_response(self, transcribed_text: str, response: str) -> str:
        """
        Форматирует ответ с транскрипцией
        
        Args:
            transcribed_text (str): Транскрибированный текст
            response (str): Сгенерированный ответ
            
        Returns:
            str: Отформатированный ответ
        """
        return f"🎤 **Транскрипция:** {transcribed_text}\n\n🤖 **Ответ:** {response}"

# Глобальный экземпляр процессора текста
text_processor = TextProcessor()
