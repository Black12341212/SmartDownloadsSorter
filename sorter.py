import os
import shutil
import re
import json
import sys
from pathlib import Path

# Определение базовой директории (работает для .py и .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # Для .exe файла
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Для .py скрипта

# Конфигурация путей
DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
RULES_FILE = os.path.join(BASE_DIR, 'rules.json')

# Базовые категории
BASE_CATEGORIES = {
    'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'heic'],
    'Videos': ['mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'mpeg', 'webm'],
    'Documents': ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'txt', 'rtf', 'odt'],
    'Archives': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2'],
    'Music': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
    'Programs': ['exe', 'msi', 'dmg', 'pkg', 'deb'],
    'Code': ['py', 'js', 'html', 'css', 'json', 'xml', 'java', 'cpp', 'c', 'h'],
    'Others': []
}

def load_rules():
    """Загружает правила из JSON-файла, создаёт при первом запуске"""
    if not os.path.exists(RULES_FILE):
        # Создаём пустой файл правил при первом запуске
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    
    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Ошибка чтения правил. Будет использован пустой список правил.")
        return []

def save_rules(rules):
    """Сохраняет правила в JSON-файл"""
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)

def get_file_category(file_name, rules):
    """Определяет категорию файла с учётом правил"""
    # Применяем пользовательские правила
    for rule in rules:
        pattern = rule['pattern'].lower()
        
        if rule['rule_type'] == 'extension':
            if file_name.lower().endswith(f".{pattern}"):
                return rule['folder']
        
        elif rule['rule_type'] == 'contains':
            if pattern in file_name.lower():
                return rule['folder']
        
        elif rule['rule_type'] == 'regex':
            if re.search(pattern, file_name, re.IGNORECASE):
                return rule['folder']
    
    # Базовые категории по расширению
    ext = Path(file_name).suffix[1:].lower()
    for category, extensions in BASE_CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'Others'

def organize_files(rules):
    """Сортирует файлы по категориям"""
    moved_count = 0
    errors_count = 0
    
    for item in os.listdir(DOWNLOADS_PATH):
        item_path = os.path.join(DOWNLOADS_PATH, item)
        
        # Пропускаем папки и системные файлы
        if os.path.isdir(item_path) or item.startswith('.'):
            continue
        
        # Определяем категорию
        category = get_file_category(item, rules)
        target_dir = os.path.join(DOWNLOADS_PATH, category)
        
        # Создаем папку при необходимости
        os.makedirs(target_dir, exist_ok=True)
        
        # Перемещаем файл
        try:
            shutil.move(item_path, os.path.join(target_dir, item))
            print(f"✓ Перемещён: {item[:30]}... -> {category}")
            moved_count += 1
        except Exception as e:
            print(f"✗ Ошибка при перемещении {item[:30]}...: {str(e)}")
            errors_count += 1
    
    print(f"\nИтого: перемещено {moved_count} файлов, ошибок: {errors_count}")

def create_rule(rules):
    """Интерактивное создание нового правила"""
    print("\n" + "=" * 40)
    print("Создание нового правила сортировки")
    print("=" * 40)
    
    # Выбор типа правила
    rule_types = {
        '1': ('extension', "Расширение файла (например: pdf)"),
        '2': ('contains', "Содержится в имени (например: отчёт)"),
        '3': ('regex', "Регулярное выражение (например: .*иван.*\.docx)")
    }
    
    print("\nВыберите тип правила:")
    for key, (_, desc) in rule_types.items():
        print(f"[{key}] {desc}")
    
    while True:
        choice = input("\nВаш выбор (1-3): ").strip()
        if choice in rule_types:
            rule_type = rule_types[choice][0]
            break
        print("Некорректный выбор, попробуйте снова")
    
    # Ввод паттерна
    print("\n" + "-" * 40)
    pattern = input("Введите значение для правила: ").strip()
    if not pattern:
        print("Отмена создания правила")
        return
    
    # Ввод целевой папки
    print("-" * 40)
    folder = input("Введите название папки для сортировки: ").strip()
    if not folder:
        print("Отмена создания правила")
        return
    
    # Создаем правило
    new_rule = {
        'rule_type': rule_type,
        'pattern': pattern,
        'folder': folder
    }
    
    # Добавляем и сохраняем
    rules.append(new_rule)
    save_rules(rules)
    print("\n" + "=" * 40)
    print(f"Правило успешно создано!")
    print(f"Тип: {rule_type}")
    print(f"Условие: {pattern}")
    print(f"Папка: {folder}")

def show_rules(rules):
    """Показывает текущие правила"""
    if not rules:
        print("\nНет пользовательских правил")
        return
    
    print("\n" + "=" * 60)
    print("Текущие правила сортировки:")
    print("=" * 60)
    for i, rule in enumerate(rules, 1):
        print(f"ПРАВИЛО #{i}")
        print(f"  Тип: {rule['rule_type'].upper()}")
        print(f"  Условие: {rule['pattern']}")
        print(f"  Папка: {rule['folder']}")
        print("-" * 60)

def delete_rule(rules):
    """Удаление существующего правила"""
    if not rules:
        print("\nНет правил для удаления")
        return
    
    show_rules(rules)
    try:
        choice = input("\nНомер правила для удаления (0 - отмена): ").strip()
        if choice == '0':
            return
            
        choice = int(choice)
        if 1 <= choice <= len(rules):
            deleted = rules.pop(choice - 1)
            save_rules(rules)
            print("\n" + "=" * 40)
            print(f"Правило успешно удалено!")
            print(f"Условие: {deleted['pattern']}")
            print(f"Папка: {deleted['folder']}")
        else:
            print("Некорректный номер")
    except ValueError:
        print("Ошибка ввода")

def main_menu():
    """Главное меню программы"""
    rules = load_rules()
    
    while True:
        print("\n" + "=" * 30)
        print(">>> УМНЫЙ СОРТИРОВЩИК ФАЙЛОВ <<<")
        print("=" * 30)
        print("1. Запустить сортировку")
        print("2. Добавить новое правило")
        print("3. Показать все правила")
        print("4. Удалить правило")
        print("5. Выход")
        print("=" * 30)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '1':
            print("\nНачало сортировки...")
            organize_files(rules)
            print("\nСортировка завершена!")
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '2':
            create_rule(rules)
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '3':
            show_rules(rules)
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '4':
            delete_rule(rules)
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '5':
            print("\nДо новых встреч! Ваши файлы теперь в порядке :)")
            break
        else:
            print("Некорректный выбор, попробуйте снова")

if __name__ == "__main__":
    # Проверка папки "Загрузки"
    if not os.path.exists(DOWNLOADS_PATH):
        print(f"ОШИБКА: Папка 'Загрузки' не найдена по пути: {DOWNLOADS_PATH}")
        print("Проверьте существование папки и попробуйте снова")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)