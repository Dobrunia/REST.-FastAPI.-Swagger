"""
RAG-ассистент на базе Yandex Cloud.
Отвечает на вопросы используя базу знаний и сохраняет контекст диалога.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
INDEX_PATH = ARTIFACTS_DIR / "index.json"

SYSTEM_PROMPT = """Ты — опытный помощник по Python и DevOps.

Правила ответов:
1. Отвечай строго на основе предоставленной базы знаний.
2. При ответе ОБЯЗАТЕЛЬНО указывай источник информации в формате: Источник: название_файла.md
3. Если в базе знаний нет информации по вопросу — честно скажи об этом и предложи уточнить вопрос.
4. Отвечай на русском языке.
5. Давай конкретные примеры кода где это уместно.
6. Будь лаконичен, но информативен.

Ты помогаешь разработчикам разобраться в технологиях: Git, Docker, Python, FastAPI, pytest, asyncio, SQLAlchemy, Pydantic и других инструментах разработки."""


@dataclass
class AssistantResponse:
    """Ответ ассистента."""
    text: str
    sources: list[str]


class RAGAssistant:
    """RAG-ассистент с поддержкой контекста диалога."""
    
    def __init__(self):
        """Инициализация ассистента."""
        self._sdk: Optional[YCloudML] = None
        self._assistant = None
        self._threads: dict[int, object] = {}  # user_id -> thread
        self._index_id: Optional[str] = None
    
    def _get_sdk(self) -> YCloudML:
        """Получение или создание SDK."""
        if self._sdk is None:
            folder_id = os.getenv("YC_FOLDER_ID")
            api_key = os.getenv("YC_API_KEY")
            
            if not folder_id or not api_key:
                raise ValueError(
                    "Не заданы переменные окружения YC_FOLDER_ID и/или YC_API_KEY"
                )
            
            self._sdk = YCloudML(folder_id=folder_id, auth=api_key)
        
        return self._sdk
    
    def _load_index_id(self) -> str:
        """Загрузка ID индекса из файла."""
        if self._index_id is None:
            if not INDEX_PATH.exists():
                raise FileNotFoundError(
                    f"Файл индекса не найден: {INDEX_PATH}\n"
                    "Сначала выполните:\n"
                    "  python -m src.upload_files\n"
                    "  python -m src.build_index"
                )
            
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._index_id = data["index_id"]
        
        return self._index_id
    
    def _get_assistant(self):
        """Получение или создание ассистента."""
        if self._assistant is None:
            sdk = self._get_sdk()
            index_id = self._load_index_id()
            
            search_index = sdk.search_indexes.get(index_id)
            
            # Создаем инструмент поиска
            search_tool = sdk.tools.search_index(search_index)
            
            # Создаем ассистента
            self._assistant = sdk.assistants.create(
                model="yandexgpt",
                tools=[search_tool],
                instruction=SYSTEM_PROMPT,
                max_tokens=2000,
                temperature=0.3
            )
        
        return self._assistant
    
    def _get_thread(self, user_id: int):
        """Получение или создание thread для пользователя."""
        if user_id not in self._threads:
            sdk = self._get_sdk()
            self._threads[user_id] = sdk.threads.create()
        
        return self._threads[user_id]
    
    def reset_thread(self, user_id: int) -> None:
        """Сброс контекста диалога для пользователя."""
        if user_id in self._threads:
            del self._threads[user_id]
    
    def ask(self, user_id: int, question: str) -> AssistantResponse:
        """
        Отправка вопроса ассистенту.
        
        Args:
            user_id: ID пользователя (для сохранения контекста)
            question: Вопрос пользователя
            
        Returns:
            AssistantResponse: Ответ ассистента с источниками
        """
        assistant = self._get_assistant()
        thread = self._get_thread(user_id)
        
        # Добавляем сообщение в thread
        thread.write(question)
        
        # Запускаем ассистента
        run = assistant.run(thread)
        
        # Ждем результата
        result = run.wait()
        
        # Извлекаем текст ответа
        response_text = ""
        sources = []
        
        for part in result:
            if hasattr(part, 'text'):
                response_text += part.text
            # Извлечение источников из цитат, если они есть
            if hasattr(part, 'citations'):
                for citation in part.citations:
                    if hasattr(citation, 'source'):
                        source_name = getattr(citation.source, 'name', 'unknown')
                        if source_name not in sources:
                            sources.append(source_name)
        
        return AssistantResponse(
            text=response_text.strip(),
            sources=sources
        )
    
    async def ask_async(self, user_id: int, question: str) -> AssistantResponse:
        """
        Асинхронная версия ask.
        Используется для интеграции с асинхронным Telegram ботом.
        """
        # SDK Yandex Cloud пока синхронный, оборачиваем в executor
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.ask, user_id, question)


# Singleton экземпляр ассистента
_assistant_instance: Optional[RAGAssistant] = None


def get_assistant() -> RAGAssistant:
    """Получение singleton экземпляра ассистента."""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = RAGAssistant()
    return _assistant_instance


def main():
    """Тестовый запуск ассистента в консоли."""
    print("=" * 50)
    print("RAG-ассистент по Python/DevOps")
    print("Введите 'выход' для завершения")
    print("Введите 'сброс' для очистки контекста")
    print("=" * 50)
    
    assistant = get_assistant()
    user_id = 1  # Тестовый пользователь
    
    while True:
        try:
            question = input("\nВопрос: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ("выход", "exit", "quit"):
                print("До свидания!")
                break
            
            if question.lower() in ("сброс", "reset"):
                assistant.reset_thread(user_id)
                print("Контекст диалога очищен")
                continue
            
            print("\nОбрабатываю...\n")
            response = assistant.ask(user_id, question)
            
            print(f"Ответ:\n{response.text}")
            
            if response.sources:
                print(f"\nИсточники: {', '.join(response.sources)}")
                
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"\nОшибка: {e}")


if __name__ == "__main__":
    main()
