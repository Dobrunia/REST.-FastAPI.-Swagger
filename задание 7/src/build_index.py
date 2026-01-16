"""
Скрипт для создания search index в Yandex Cloud.
Создает гибридный поисковый индекс из загруженных файлов.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import (
    HybridSearchIndexType,
    StaticIndexChunkingStrategy,
)

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
UPLOADED_FILES_PATH = ARTIFACTS_DIR / "uploaded_files.json"
INDEX_PATH = ARTIFACTS_DIR / "index.json"


def get_sdk() -> YCloudML:
    """Инициализация SDK с проверкой credentials."""
    folder_id = os.getenv("YC_FOLDER_ID")
    api_key = os.getenv("YC_API_KEY")
    
    if not folder_id or not api_key:
        raise ValueError(
            "Не заданы переменные окружения YC_FOLDER_ID и/или YC_API_KEY. "
            "Скопируйте env.example в .env и заполните значения."
        )
    
    return YCloudML(folder_id=folder_id, auth=api_key)


def load_uploaded_files() -> dict:
    """Загрузка информации о загруженных файлах."""
    if not UPLOADED_FILES_PATH.exists():
        raise FileNotFoundError(
            f"Файл с загруженными файлами не найден: {UPLOADED_FILES_PATH}\n"
            "Сначала выполните: python -m src.upload_files"
        )
    
    with open(UPLOADED_FILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_existing_index() -> dict | None:
    """Загрузка информации о существующем индексе."""
    if INDEX_PATH.exists():
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_index_info(index_info: dict) -> None:
    """Сохранение информации об индексе."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_info, f, ensure_ascii=False, indent=2)


def wait_for_operation(operation, description: str, timeout: int = 300) -> None:
    """Ожидание завершения операции с индикацией прогресса."""
    print(f"{description}...", end="", flush=True)
    start_time = time.time()
    
    while not operation.done:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Операция превысила таймаут {timeout}с")
        print(".", end="", flush=True)
        time.sleep(2)
    
    print(" ✓")


def build_index() -> dict:
    """
    Создание поискового индекса.
    
    Returns:
        dict: Информация о созданном индексе
    """
    print("=" * 50)
    print("Создание поискового индекса")
    print("=" * 50)
    
    # Инициализация SDK
    sdk = get_sdk()
    print("✓ SDK инициализирован")
    
    # Загрузка информации о файлах
    uploaded_files = load_uploaded_files()
    file_ids = [info["file_id"] for info in uploaded_files.values()]
    print(f"✓ Найдено {len(file_ids)} файлов для индексации")
    
    # Проверка существующего индекса
    existing_index = load_existing_index()
    if existing_index:
        print(f"Найден существующий индекс: {existing_index['index_id']}")
        print("  Для создания нового индекса удалите artifacts/index.json")
        return existing_index
    
    print("\nСоздание индекса:")
    
    # Создание операции индекса
    operation = sdk.search_indexes.create_deferred(
        file_ids,
        index_type=HybridSearchIndexType(
            chunking_strategy=StaticIndexChunkingStrategy(
                max_chunk_size_tokens=800,
                chunk_overlap_tokens=100
            )
        )
    )
    
    # Ожидание создания индекса
    wait_for_operation(operation, "Создание структуры индекса")
    
    # Получение созданного индекса
    index = operation.result
    print(f"Индекс создан: {index.id}")
    
    # Сохранение информации
    index_info = {
        "index_id": index.id,
        "files_count": len(file_ids),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_index_info(index_info)
    
    print("=" * 50)
    print(f"Индекс успешно создан!")
    print(f"ID индекса: {index.id}")
    print(f"Проиндексировано файлов: {len(file_ids)}")
    print(f"Информация сохранена в: {INDEX_PATH}")
    print("=" * 50)
    
    return index_info


def main():
    """Точка входа."""
    try:
        build_index()
    except Exception as e:
        print(f"\nОшибка: {e}")
        exit(1)


if __name__ == "__main__":
    main()
