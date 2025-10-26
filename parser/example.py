"""
Пример использования парсера законов с PostgreSQL.

Этот файл демонстрирует, как:
1. Подключиться к базе данных
2. Запустить парсинг закона
3. Проверить сохраненные данные
"""

import os
import sys
from datetime import date
from sqlalchemy.orm import Session

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.database import SessionLocal, LawRepository, Law, LawChapter, LawPart, LawParagraph
from parser.config import DatabaseConfig, setup_database
from parser.law_parser import parse_and_save_law


def check_database_connection():
    """Проверка подключения к базе данных"""
    print("🔍 Проверка подключения к базе данных...")
    
    try:
        db = SessionLocal()
        repo = LawRepository(db)
        
        # Простой запрос для проверки подключения
        result = db.execute("SELECT 1 as test")
        test_value = result.scalar()
        
        if test_value == 1:
            print("✅ Подключение к базе данных успешно")
            return True
        else:
            print("❌ Ошибка подключения к базе данных")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    finally:
        db.close()


def show_database_stats():
    """Показать статистику базы данных"""
    print("\n📊 Статистика базы данных:")
    
    try:
        db = SessionLocal()
        
        # Подсчет записей
        laws_count = db.query(Law).count()
        chapters_count = db.query(LawChapter).count()
        parts_count = db.query(LawPart).count()
        paragraphs_count = db.query(LawParagraph).count()
        
        print(f"   📋 Законов: {laws_count}")
        print(f"   📖 Глав: {chapters_count}")
        print(f"   📄 Частей: {parts_count}")
        print(f"   📝 Пунктов: {paragraphs_count}")
        
        # Показать активные законы
        laws = db.query(Law).all()
        print(f"\n📋 Законы в базе данных:")
        for law in laws:
            print(f"   - {law.law_name}")
            print(f"     Код: {law.law_code}")
            print(f"     Загружен: {law.created_at}")
            
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
    finally:
        db.close()


def show_law_structure(law_code: str = "38-FZ"):
    """Показать структуру закона"""
    print(f"\n📚 Структура закона {law_code}:")
    
    try:
        db = SessionLocal()
        
        # Найти закон
        law = db.query(Law).filter(Law.law_code == law_code).first()
        
        if not law:
            print(f"❌ Закон {law_code} не найден")
            return
        
        print(f"📋 Закон: {law.law_name}")
        print(f"📅 Загружен: {law.created_at}")
        
        # Показать главы
        chapters = db.query(LawChapter).filter(
            LawChapter.law_id == law.id
        ).order_by(LawChapter.chapter_number).all()
        
        for chapter in chapters:
            print(f"\n📖 {chapter.title}")
            
            # Показать части главы
            parts = db.query(LawPart).filter(
                LawPart.chapter_id == chapter.id
            ).order_by(LawPart.part_number).all()
            
            for part in parts:
                print(f"   📄 {part.title}")
                print(f"      Номер: {part.part_number}")
                print(f"      URL: {part.source_url}")
                
                # Показать пункты части
                paragraphs = db.query(LawParagraph).filter(
                    LawParagraph.part_id == part.id
                ).order_by(LawParagraph.paragraph_number).all()
                
                for paragraph in paragraphs:
                    print(f"      📝 Пункт {paragraph.paragraph_number}: {paragraph.content[:100]}...")
                
    except Exception as e:
        print(f"❌ Ошибка получения структуры: {e}")
    finally:
        db.close()


def search_in_law_content(search_term: str, law_code: str = "38-FZ"):
    """Поиск по содержимому закона"""
    print(f"\n🔍 Поиск '{search_term}' в законе {law_code}:")
    
    try:
        db = SessionLocal()
        
        # Найти закон
        law = db.query(Law).filter(Law.law_code == law_code).first()
        
        if not law:
            print(f"❌ Закон {law_code} не найден")
            return
        
        # Поиск в пунктах
        paragraphs = db.query(LawParagraph).filter(
            LawParagraph.law_id == law.id,
            LawParagraph.content.contains(search_term)
        ).all()
        
        if paragraphs:
            print(f"📝 Найдено в {len(paragraphs)} пунктах:")
            for paragraph in paragraphs:
                print(f"   - Пункт {paragraph.paragraph_number}")
                # Показать фрагмент текста
                content = paragraph.content
                start = content.lower().find(search_term.lower())
                if start != -1:
                    start = max(0, start - 50)
                    end = min(len(content), start + 100)
                    fragment = content[start:end]
                    print(f"     ...{fragment}...")
        else:
            print("❌ Ничего не найдено")
            
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
    finally:
        db.close()


def main():
    """Основная функция демонстрации"""
    print("🚀 Демонстрация парсера законов с PostgreSQL")
    print("=" * 60)
    
    # 1. Проверка подключения
    if not check_database_connection():
        print("\n❌ Не удалось подключиться к базе данных")
        print("💡 Убедитесь, что:")
        print("   1. PostgreSQL запущен")
        print("   2. База данных создана")
        print("   3. Настройки в .env корректны")
        return
    
    # 2. Показать статистику
    show_database_stats()
    
    # 3. Показать структуру закона (если есть данные)
    show_law_structure()
    
    # 4. Пример поиска
    search_in_law_content("реклама")
    
    print("\n🎉 Демонстрация завершена!")
    print("\n📋 Доступные команды:")
    print("   - python -m parser.config  # Настройка БД и тестовые данные")
    print("   - python -m parser.law_parser  # Запуск парсинга")


if __name__ == "__main__":
    main()
