#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Downloads Sorter v1.1
Автоматический сортировщик файлов в папке Загрузки
"""

import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
import sys
import time

class SmartSorter:
    def __init__(self):
        self.downloads_path = str(Path.home() / "Downloads")
        self.rules_file = "rules.json"
        self.version = "1.1"
        self.default_rules = {
            "Images": {
                "folder": "Images",
                "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
                "name_contains": [],
                "regex": []
            },
            "Videos": {
                "folder": "Videos",
                "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
                "name_contains": [],
                "regex": []
            },
            "Documents": {
                "folder": "Documents",
                "extensions": [".pdf", ".doc", ".docx", ".txt", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
                "name_contains": [],
                "regex": []
            },
            "Archives": {
                "folder": "Archives",
                "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
                "name_contains": [],
                "regex": []
            },
            "Audio": {
                "folder": "Audio",
                "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
                "name_contains": [],
                "regex": []
            },
            "Programs": {
                "folder": "Programs",
                "extensions": [".exe", ".msi", ".app", ".dmg", ".deb", ".rpm"],
                "name_contains": [],
                "regex": []
            }
        }
        self.load_rules()
        
    def load_rules(self):
        """Загружает правила из файла или создает файл с правилами по умолчанию"""
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
                print(f"✅ Правила загружены из {self.rules_file}")
            else:
                self.rules = self.default_rules
                self.save_rules()
                print(f"📝 Создан файл правил {self.rules_file}")
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке правил: {e}")
            print("Используются правила по умолчанию")
            self.rules = self.default_rules
            
    def save_rules(self):
        """Сохраняет правила в файл"""
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=4, ensure_ascii=False)
            print(f"✅ Правила сохранены в {self.rules_file}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении правил: {e}")
            
    def check_file_match(self, filename, rule):
        """Проверяет, соответствует ли файл правилу"""
        file_lower = filename.lower()
        
        # Проверка расширения
        for ext in rule.get("extensions", []):
            if file_lower.endswith(ext.lower()):
                return True
                
        # Проверка содержания в имени
        for text in rule.get("name_contains", []):
            if text.lower() in file_lower:
                return True
                
        # Проверка регулярных выражений
        for pattern in rule.get("regex", []):
            try:
                if re.search(pattern, filename):
                    return True
            except re.error:
                print(f"⚠️ Неверное регулярное выражение: {pattern}")
                
        return False
        
    def sort_downloads(self, dry_run=False):
        """Сортирует файлы в папке Загрузки"""
        if not os.path.exists(self.downloads_path):
            print(f"❌ Папка {self.downloads_path} не найдена!")
            return
            
        print(f"\n{'='*50}")
        print(f"🚀 Начинаем сортировку папки: {self.downloads_path}")
        if dry_run:
            print("📋 ТЕСТОВЫЙ РЕЖИМ - файлы не будут перемещены")
        print(f"{'='*50}\n")
        
        moved_count = 0
        error_count = 0
        
        try:
            files = [f for f in os.listdir(self.downloads_path) 
                    if os.path.isfile(os.path.join(self.downloads_path, f))]
            
            if not files:
                print("📭 В папке Загрузки нет файлов для сортировки")
                return
                
            print(f"Найдено файлов: {len(files)}\n")
            
            for filename in files:
                source_path = os.path.join(self.downloads_path, filename)
                moved = False
                
                for category, rule in self.rules.items():
                    if self.check_file_match(filename, rule):
                        folder_name = rule.get("folder", category)
                        dest_folder = os.path.join(self.downloads_path, folder_name)
                        
                        if not dry_run:
                            try:
                                # Создаем папку если её нет
                                os.makedirs(dest_folder, exist_ok=True)
                                
                                # Обрабатываем дубликаты
                                dest_path = os.path.join(dest_folder, filename)
                                if os.path.exists(dest_path):
                                    base, ext = os.path.splitext(filename)
                                    counter = 1
                                    while os.path.exists(dest_path):
                                        new_filename = f"{base}_{counter}{ext}"
                                        dest_path = os.path.join(dest_folder, new_filename)
                                        counter += 1
                                
                                # Перемещаем файл
                                shutil.move(source_path, dest_path)
                                print(f"✅ {filename} → {folder_name}/")
                                moved_count += 1
                                moved = True
                                break
                                
                            except Exception as e:
                                print(f"❌ Ошибка при перемещении {filename}: {e}")
                                error_count += 1
                        else:
                            print(f"📋 {filename} → {folder_name}/ (тест)")
                            moved_count += 1
                            moved = True
                            break
                            
                if not moved:
                    print(f"⏭️  {filename} - правило не найдено")
                    
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            
        print(f"\n{'='*50}")
        print(f"✅ Сортировка завершена!")
        print(f"📊 Статистика:")
        print(f"   • Перемещено файлов: {moved_count}")
        print(f"   • Пропущено файлов: {len(files) - moved_count - error_count}")
        print(f"   • Ошибок: {error_count}")
        print(f"{'='*50}\n")
        
    def add_rule(self):
        """Добавляет новое правило сортировки"""
        print("\n=== Добавление нового правила ===")
        category = input("Название категории: ").strip()
        
        if not category:
            print("❌ Название категории не может быть пустым")
            return
            
        folder = input(f"Название папки (Enter для '{category}'): ").strip() or category
        
        # Расширения
        extensions_input = input("Расширения через запятую (например: .txt,.pdf): ").strip()
        extensions = [ext.strip() for ext in extensions_input.split(",") if ext.strip()]
        
        # Добавляем точку если забыли
        extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
        
        self.rules[category] = {
            "folder": folder,
            "extensions": extensions,
            "name_contains": [],
            "regex": []
        }
        
        self.save_rules()
        print(f"✅ Правило '{category}' добавлено!")
        
    def show_rules(self):
        """Показывает текущие правила"""
        print("\n=== Текущие правила сортировки ===")
        for category, rule in self.rules.items():
            print(f"\n📁 {category} → {rule['folder']}/")
            if rule['extensions']:
                print(f"   Расширения: {', '.join(rule['extensions'])}")
            if rule.get('name_contains'):
                print(f"   Содержит в имени: {', '.join(rule['name_contains'])}")
            if rule.get('regex'):
                print(f"   Regex: {', '.join(rule['regex'])}")
                
    def delete_rule(self):
        """Удаляет правило"""
        self.show_rules()
        category = input("\nКакое правило удалить? ").strip()
        
        if category in self.rules:
            del self.rules[category]
            self.save_rules()
            print(f"✅ Правило '{category}' удалено")
        else:
            print(f"❌ Правило '{category}' не найдено")
            
    def reset_rules(self):
        """Сбрасывает правила к значениям по умолчанию"""
        confirm = input("Вы уверены? Все пользовательские правила будут удалены (y/n): ")
        if confirm.lower() == 'y':
            self.rules = self.default_rules
            self.save_rules()
            print("✅ Правила сброшены к значениям по умолчанию")
            
    def run(self):
        """Главное меню программы"""
        print(f"""
╔════════════════════════════════════════════╗
║     Smart Downloads Sorter v{self.version}         ║
║     Умный сортировщик файлов              ║
╚════════════════════════════════════════════╝
        """)
        
        while True:
            print("\n=== ГЛАВНОЕ МЕНЮ ===")
            print("1. 🚀 Сортировать загрузки")
            print("2. 📋 Тестовый прогон (без перемещения)")
            print("3. 👀 Показать правила")
            print("4. ➕ Добавить правило")
            print("5. ❌ Удалить правило")
            print("6. 🔄 Сбросить правила")
            print("7. 📁 Изменить папку загрузок")
            print("0. 🚪 Выход")
            
            try:
                choice = input("\nВыберите действие: ").strip()
                
                if choice == "1":
                    self.sort_downloads()
                elif choice == "2":
                    self.sort_downloads(dry_run=True)
                elif choice == "3":
                    self.show_rules()
                elif choice == "4":
                    self.add_rule()
                elif choice == "5":
                    self.delete_rule()
                elif choice == "6":
                    self.reset_rules()
                elif choice == "7":
                    new_path = input(f"Текущая папка: {self.downloads_path}\nНовая папка: ").strip()
                    if os.path.exists(new_path):
                        self.downloads_path = new_path
                        print(f"✅ Папка изменена на: {new_path}")
                    else:
                        print("❌ Папка не существует")
                elif choice == "0":
                    print("\n👋 До свидания!")
                    break
                else:
                    print("❌ Неверный выбор")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Программа прервана. До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    sorter = SmartSorter()
    sorter.run()
