"""
Скрипт для загрузки файлов базы знаний в Yandex Cloud.
Загружает все .md файлы из data/knowledge_base/ и сохраняет их ID в artifacts/uploaded_files.json
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
UPLOADED_FILES_PATH = ARTIFACTS_DIR / "uploaded_files.json"


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


def load_existing_uploads() -> dict:
    """Загрузка информации о ранее загруженных файлах."""
    if UPLOADED_FILES_PATH.exists():
        with open(UPLOADED_FILES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_uploads(uploads: dict) -> None:
    """Сохранение информации о загруженных файлах."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(UPLOADED_FILES_PATH, "w", encoding="utf-8") as f:
        json.dump(uploads, f, ensure_ascii=False, indent=2)


def get_md_files() -> list[Path]:
    """Получение списка markdown файлов из базы знаний."""
    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Директория базы знаний не найдена: {KNOWLEDGE_BASE_DIR}"
        )
    
    files = list(KNOWLEDGE_BASE_DIR.glob("*.md"))
    if not files:
        raise FileNotFoundError(
            f"Не найдены .md файлы в директории: {KNOWLEDGE_BASE_DIR}"
        )
    
    return sorted(files)


def upload_files() -> dict:
    """
    Загрузка файлов в Yandex Cloud.
    
    Returns:
        dict: Словарь {filename: file_id} загруженных файлов
    """
    print("=" * 50)
    print("Загрузка файлов в Yandex Cloud")
    print("=" * 50)
    
    sdk = get_sdk()
    print("SDK инициализирован")
    
    md_files = get_md_files()
    print(f"Найдено {len(md_files)} файлов для загрузки")
    
    existing_uploads = load_existing_uploads()
    uploads = {}
    
    for file_path in md_files:
        filename = file_path.name
        
        # Проверка, был ли файл уже загружен
        if filename in existing_uploads:
            print(f"  ⏭ {filename} уже загружен (ID: {existing_uploads[filename]['file_id']})")
            uploads[filename] = existing_uploads[filename]
            continue
        
        print(f"  ⬆ Загрузка: {filename}...", end=" ")
        
        try:
            # Загрузка файла
            uploaded_file = sdk.files.upload(
                file_path,
                ttl_days=7,
                expiration_policy="static"
            )
            
            uploads[filename] = {
                "file_id": uploaded_file.id,
                "name": filename,
                "path": str(file_path.relative_to(BASE_DIR))
            }
            
            print(f"(ID: {uploaded_file.id})")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            raise
    
    # Сохранение результатов
    save_uploads(uploads)
    
    print("=" * 50)
    print(f"Загружено файлов: {len(uploads)}")
    print(f"Результаты сохранены в: {UPLOADED_FILES_PATH}")
    print("=" * 50)
    
    return uploads


def main():
    """Точка входа."""
    try:
        upload_files()
    except Exception as e:
        print(f"\nОшибка: {e}")
        exit(1)


if __name__ == "__main__":
    main()
