#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Downloads Sorter v1.2
Автоматический сортировщик файлов с улучшенной обработкой PDF
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
        self.version = "1.2"
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
                "extensions": [".doc", ".docx", ".txt", ".odt", ".rtf"],
                "name_contains": [],
                "regex": []
            },
            "Spreadsheets": {
                "folder": "Documents/Spreadsheets",
                "extensions": [".xls", ".xlsx", ".csv", ".ods"],
                "name_contains": [],
                "regex": []
            },
            "Presentations": {
                "folder": "Documents/Presentations",
                "extensions": [".ppt", ".pptx", ".odp"],
                "name_contains": [],
                "regex": []
            },
            "PDF_Books": {
                "folder": "PDF/Books",
                "extensions": [".pdf"],
                "name_contains": ["book", "книга", "учебник", "tutorial", "guide", "manual"],
                "regex": ["(?i)(book|guide|tutorial|manual|учебник)"],
                "size_min_mb": 5
            },
            "PDF_Articles": {
                "folder": "PDF/Articles",
                "extensions": [".pdf"],
                "name_contains": ["article", "статья", "paper", "journal"],
                "regex": ["(?i)(article|paper|journal|статья)"],
                "size_max_mb": 5
            },
            "PDF_Scans": {
                "folder": "PDF/Scans",
                "extensions": [".pdf"],
                "name_contains": ["scan", "скан", "copy", "копия"],
                "regex": ["(?i)(scan|скан|copy)"]
            },
            "PDF_Forms": {
                "folder": "PDF/Forms",
                "extensions": [".pdf"],
                "name_contains": ["form", "форма", "заявление", "договор", "contract", "invoice", "receipt"],
                "regex": ["(?i)(form|заявка|заявление|договор|contract|invoice|receipt|счет)"]
            },
            "PDF_Other": {
                "folder": "PDF/Other",
                "extensions": [".pdf"],
                "name_contains": [],
                "regex": [],
                "is_default_pdf": True
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
                "extensions": [".exe", ".msi", ".app", ".dmg", ".deb", ".rpm", ".apk"],
                "name_contains": [],
                "regex": []
            },
            "Code": {
                "folder": "Code",
                "extensions": [".py", ".js", ".html", ".css", ".cpp", ".java", ".c", ".h", ".php", ".sql", ".json", ".xml", ".yaml"],
                "name_contains": [],
                "regex": []
            }
        }
        
        # PDF-специфичные настройки
        self.pdf_settings = {
            "enable_smart_pdf": True,
            "pdf_size_analysis": True,
            "pdf_name_patterns": True,
            "create_monthly_folders": False
        }
        
        self.load_rules()
        self.load_settings()
        
    def load_settings(self):
        """Загружает настройки программы"""
        settings_file = "settings.json"
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.pdf_settings.update(saved_settings.get('pdf_settings', {}))
        except Exception as e:
            print(f"⚠️ Не удалось загрузить настройки: {e}")
            
    def save_settings(self):
        """Сохраняет настройки программы"""
        settings_file = "settings.json"
        try:
            settings = {
                'pdf_settings': self.pdf_settings,
                'version': self.version
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print(f"✅ Настройки сохранены")
        except Exception as e:
            print(f"❌ Ошибка при сохранении настроек: {e}")
        
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
            
    def get_file_size_mb(self, filepath):
        """Получает размер файла в мегабайтах"""
        try:
            return os.path.getsize(filepath) / (1024 * 1024)
        except:
            return 0
            
    def check_file_match(self, filename, filepath, rule):
        """Проверяет, соответствует ли файл правилу"""
        file_lower = filename.lower()
        
        # Проверка размера файла (для PDF)
        if 'size_min_mb' in rule or 'size_max_mb' in rule:
            size_mb = self.get_file_size_mb(filepath)
            if 'size_min_mb' in rule and size_mb < rule['size_min_mb']:
                return False
            if 'size_max_mb' in rule and size_mb > rule['size_max_mb']:
                return False
        
        # Пропускаем default PDF правило при первом проходе
        if rule.get('is_default_pdf'):
            return False
            
        # Проверка расширения
        extension_match = False
        for ext in rule.get("extensions", []):
            if file_lower.endswith(ext.lower()):
                extension_match = True
                break
                
        if not extension_match and rule.get("extensions"):
            return False
            
        # Для PDF файлов с умными правилами
        if extension_match and file_lower.endswith('.pdf') and self.pdf_settings['enable_smart_pdf']:
            # Если есть специфичные паттерны для PDF
            if rule.get("name_contains") or rule.get("regex"):
                name_match = False
                
                # Проверка содержания в имени
                for text in rule.get("name_contains", []):
                    if text.lower() in file_lower:
                        name_match = True
                        break
                        
                # Проверка регулярных выражений
                if not name_match:
                    for pattern in rule.get("regex", []):
                        try:
                            if re.search(pattern, filename):
                                name_match = True
                                break
                        except re.error:
                            print(f"⚠️ Неверное регулярное выражение: {pattern}")
                            
                return name_match
            else:
                # Если нет специфичных паттернов, принимаем по расширению
                return True
        
        # Для не-PDF файлов стандартная проверка
        if extension_match:
            # Если есть дополнительные условия
            if rule.get("name_contains") or rule.get("regex"):
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
            else:
                return True
                
        return False
        
    def analyze_pdf(self, filename, filepath):
        """Анализирует PDF файл для умной сортировки"""
        file_lower = filename.lower()
        size_mb = self.get_file_size_mb(filepath)
        
        # Анализ по размеру
        if size_mb > 50:
            return "PDF_Books", "Большой PDF (>50MB) - вероятно книга"
        elif size_mb < 1:
            return "PDF_Forms", "Маленький PDF (<1MB) - вероятно форма или документ"
            
        # Анализ по паттернам в имени
        if any(word in file_lower for word in ['invoice', 'receipt', 'счет', 'чек', 'квитанция']):
            return "PDF_Forms", "Обнаружены ключевые слова для форм/документов"
        elif any(word in file_lower for word in ['presentation', 'slides', 'презентация']):
            return "PDF_Other", "Возможно презентация в PDF"
            
        return None, None
        
    def sort_downloads(self, dry_run=False):
        """Сортирует файлы в папке Загрузки"""
        if not os.path.exists(self.downloads_path):
            print(f"❌ Папка {self.downloads_path} не найдена!")
            return
            
        print(f"\n{'='*60}")
        print(f"🚀 Начинаем сортировку папки: {self.downloads_path}")
        print(f"📄 PDF Intelligence: {'Включен' if self.pdf_settings['enable_smart_pdf'] else 'Выключен'}")
        if dry_run:
            print("📋 ТЕСТОВЫЙ РЕЖИМ - файлы не будут перемещены")
        print(f"{'='*60}\n")
        
        moved_count = 0
        error_count = 0
        pdf_count = 0
        
        try:
            files = [f for f in os.listdir(self.downloads_path) 
                    if os.path.isfile(os.path.join(self.downloads_path, f))]
            
            if not files:
                print("📭 В папке Загрузки нет файлов для сортировки")
                return
                
            print(f"Найдено файлов: {len(files)}")
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            if pdf_files:
                print(f"Из них PDF: {len(pdf_files)}\n")
            else:
                print()
            
            # Сначала обрабатываем не-default правила
            for filename in files:
                source_path = os.path.join(self.downloads_path, filename)
                moved = False
                
                for category, rule in self.rules.items():
                    if not rule.get('is_default_pdf') and self.check_file_match(filename, source_path, rule):
                        folder_name = rule.get("folder", category)
                        
                        # Добавляем месячную папку если включено
                        if self.pdf_settings.get('create_monthly_folders') and filename.lower().endswith('.pdf'):
                            month_folder = datetime.now().strftime("%Y-%m")
                            folder_name = os.path.join(folder_name, month_folder)
                        
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
                                if filename.lower().endswith('.pdf'):
                                    print(f"📄 {filename} → {folder_name}/")
                                    pdf_count += 1
                                else:
                                    print(f"✅ {filename} → {folder_name}/")
                                moved_count += 1
                                moved = True
                                break
                                
                            except Exception as e:
                                print(f"❌ Ошибка при перемещении {filename}: {e}")
                                error_count += 1
                        else:
                            if filename.lower().endswith('.pdf'):
                                size_mb = self.get_file_size_mb(source_path)
                                print(f"📄 {filename} ({size_mb:.1f}MB) → {folder_name}/ (тест)")
                                pdf_count += 1
                            else:
                                print(f"📋 {filename} → {folder_name}/ (тест)")
                            moved_count += 1
                            moved = True
                            break
                
                # Если PDF не подошел под специфичные правила, используем default
                if not moved and filename.lower().endswith('.pdf'):
                    for category, rule in self.rules.items():
                        if rule.get('is_default_pdf'):
                            folder_name = rule.get("folder", category)
                            
                            if self.pdf_settings['pdf_size_analysis']:
                                # Умный анализ PDF
                                suggested_category, reason = self.analyze_pdf(filename, source_path)
                                if suggested_category and suggested_category in self.rules:
                                    folder_name = self.rules[suggested_category].get("folder", suggested_category)
                                    if dry_run:
                                        print(f"🤖 AI: {reason}")
                            
                            dest_folder = os.path.join(self.downloads_path, folder_name)
                            
                            if not dry_run:
                                try:
                                    os.makedirs(dest_folder, exist_ok=True)
                                    dest_path = os.path.join(dest_folder, filename)
                                    
                                    # Обработка дубликатов
                                    if os.path.exists(dest_path):
                                        base, ext = os.path.splitext(filename)
                                        counter = 1
                                        while os.path.exists(dest_path):
                                            new_filename = f"{base}_{counter}{ext}"
                                            dest_path = os.path.join(dest_folder, new_filename)
                                            counter += 1
                                    
                                    shutil.move(source_path, dest_path)
                                    print(f"📄 {filename} → {folder_name}/")
                                    moved_count += 1
                                    pdf_count += 1
                                    moved = True
                                except Exception as e:
                                    print(f"❌ Ошибка при перемещении {filename}: {e}")
                                    error_count += 1
                            else:
                                size_mb = self.get_file_size_mb(source_path)
                                print(f"📄 {filename} ({size_mb:.1f}MB) → {folder_name}/ (тест)")
                                moved_count += 1
                                pdf_count += 1
                                moved = True
                            break
                            
                if not moved and not filename.lower().endswith('.pdf'):
                    print(f"⏭️  {filename} - правило не найдено")
                    
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            
        print(f"\n{'='*60}")
        print(f"✅ Сортировка завершена!")
        print(f"📊 Статистика:")
        print(f"   • Перемещено файлов: {moved_count}")
        if pdf_count > 0:
            print(f"   • Из них PDF: {pdf_count}")
        print(f"   • Пропущено файлов: {len(files) - moved_count - error_count}")
        print(f"   • Ошибок: {error_count}")
        print(f"{'='*60}\n")
        
    def pdf_menu(self):
        """Меню настроек PDF"""
        while True:
            print("\n=== НАСТРОЙКИ PDF ===")
            print(f"1. Smart PDF: {'✅ Включен' if self.pdf_settings['enable_smart_pdf'] else '❌ Выключен'}")
            print(f"2. Анализ размера: {'✅ Включен' if self.pdf_settings['pdf_size_analysis'] else '❌ Выключен'}")
            print(f"3. Месячные папки: {'✅ Включены' if self.pdf_settings['create_monthly_folders'] else '❌ Выключены'}")
            print("4. Показать PDF правила")
            print("5. Добавить PDF правило")
            print("0. Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "1":
                self.pdf_settings['enable_smart_pdf'] = not self.pdf_settings['enable_smart_pdf']
                self.save_settings()
                print(f"Smart PDF {'включен' if self.pdf_settings['enable_smart_pdf'] else 'выключен'}")
            elif choice == "2":
                self.pdf_settings['pdf_size_analysis'] = not self.pdf_settings['pdf_size_analysis']
                self.save_settings()
                print(f"Анализ размера {'включен' if self.pdf_settings['pdf_size_analysis'] else 'выключен'}")
            elif choice == "3":
                self.pdf_settings['create_monthly_folders'] = not self.pdf_settings['create_monthly_folders']
                self.save_settings()
                print(f"Месячные папки {'включены' if self.pdf_settings['create_monthly_folders'] else 'выключены'}")
            elif choice == "4":
                self.show_pdf_rules()
            elif choice == "5":
                self.add_pdf_rule()
            elif choice == "0":
                break
                
    def show_pdf_rules(self):
        """Показывает PDF правила"""
        print("\n=== PDF ПРАВИЛА ===")
        for category, rule in self.rules.items():
            if '.pdf' in rule.get('extensions', []):
                print(f"\n📄 {category} → {rule['folder']}/")
                if rule.get('name_contains'):
                    print(f"   Ключевые слова: {', '.join(rule['name_contains'])}")
                if rule.get('size_min_mb'):
                    print(f"   Минимальный размер: {rule['size_min_mb']} MB")
                if rule.get('size_max_mb'):
                    print(f"   Максимальный размер: {rule['size_max_mb']} MB")
                if rule.get('is_default_pdf'):
                    print(f"   📌 Правило по умолчанию для PDF")
                    
    def add_pdf_rule(self):
        """Добавляет новое PDF правило"""
        print("\n=== ДОБАВЛЕНИЕ PDF ПРАВИЛА ===")
        category = input("Название категории (например, PDF_Contracts): ").strip()
        
        if not category:
            print("❌ Название не может быть пустым")
            return
            
        folder = input(f"Папка (Enter для 'PDF/{category}'): ").strip() or f"PDF/{category}"
        
        keywords = input("Ключевые слова через запятую: ").strip()
        keywords_list = [k.strip() for k in keywords.split(",") if k.strip()]
        
        min_size = input("Минимальный размер в MB (Enter - пропустить): ").strip()
        max_size = input("Максимальный размер в MB (Enter - пропустить): ").strip()
        
        rule = {
            "folder": folder,
            "extensions": [".pdf"],
            "name_contains": keywords_list,
            "regex": []
        }
        
        if min_size:
            try:
                rule["size_min_mb"] = float(min_size)
            except ValueError:
                print("⚠️ Неверный размер, пропускаем")
                
        if max_size:
            try:
                rule["size_max_mb"] = float(max_size)
            except ValueError:
                print("⚠️ Неверный размер, пропускаем")
                
        self.rules[category] = rule
        self.save_rules()
        print(f"✅ PDF правило '{category}' добавлено!")
        
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
        
        # Группируем правила
        pdf_rules = []
        other_rules = []
        
        for category, rule in self.rules.items():
            if '.pdf' in rule.get('extensions', []):
                pdf_rules.append((category, rule))
            else:
                other_rules.append((category, rule))
        
        # Показываем обычные правила
        if other_rules:
            print("\n📁 ОБЩИЕ ПРАВИЛА:")
            for category, rule in other_rules:
                print(f"\n  {category} → {rule['folder']}/")
                if rule['extensions']:
                    print(f"    Расширения: {', '.join(rule['extensions'])}")
                    
        # Показываем PDF правила
        if pdf_rules:
            print("\n📄 PDF ПРАВИЛА:")
            for category, rule in pdf_rules:
                print(f"\n  {category} → {rule['folder']}/")
                if rule.get('name_contains'):
                    print(f"    Ключевые слова: {', '.join(rule['name_contains'][:3])}...")
                if rule.get('size_min_mb') or rule.get('size_max_mb'):
                    size_str = []
                    if rule.get('size_min_mb'):
                        size_str.append(f"мин: {rule['size_min_mb']}MB")
                    if rule.get('size_max_mb'):
                        size_str.append(f"макс: {rule['size_max_mb']}MB")
                    print(f"    Размер: {', '.join(size_str)}")
                if rule.get('is_default_pdf'):
                    print(f"    📌 По умолчанию для остальных PDF")
                
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
            
    def show_statistics(self):
        """Показывает статистику папки загрузок"""
        if not os.path.exists(self.downloads_path):
            print(f"❌ Папка {self.downloads_path} не найдена!")
            return
            
        print(f"\n=== СТАТИСТИКА ПАПКИ ЗАГРУЗОК ===")
        print(f"📁 Путь: {self.downloads_path}\n")
        
        try:
            files = [f for f in os.listdir(self.downloads_path) 
                    if os.path.isfile(os.path.join(self.downloads_path, f))]
            
            # Подсчет по типам
            stats = {}
            total_size = 0
            pdf_stats = {
                'count': 0,
                'total_size': 0,
                'categories': {}
            }
            
            for filename in files:
                filepath = os.path.join(self.downloads_path, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                file_size = self.get_file_size_mb(filepath)
                total_size += file_size
                
                if file_ext not in stats:
                    stats[file_ext] = {'count': 0, 'size': 0}
                stats[file_ext]['count'] += 1
                stats[file_ext]['size'] += file_size
                
                # Специальная статистика для PDF
                if file_ext == '.pdf':
                    pdf_stats['count'] += 1
                    pdf_stats['total_size'] += file_size
                    
                    # Определяем категорию
                    for category, rule in self.rules.items():
                        if '.pdf' in rule.get('extensions', []) and self.check_file_match(filename, filepath, rule):
                            if category not in pdf_stats['categories']:
                                pdf_stats['categories'][category] = 0
                            pdf_stats['categories'][category] += 1
                            break
            
            # Вывод общей статистики
            print(f"📊 Всего файлов: {len(files)}")
            print(f"💾 Общий размер: {total_size:.1f} MB\n")
            
            # Вывод по типам
            if stats:
                print("📈 По типам файлов:")
                sorted_stats = sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)
                for ext, data in sorted_stats[:10]:  # Топ 10
                    print(f"  {ext}: {data['count']} файлов ({data['size']:.1f} MB)")
                    
            # PDF статистика
            if pdf_stats['count'] > 0:
                print(f"\n📄 PDF СТАТИСТИКА:")
                print(f"  Всего PDF: {pdf_stats['count']}")
                print(f"  Общий размер: {pdf_stats['total_size']:.1f} MB")
                print(f"  Средний размер: {pdf_stats['total_size']/pdf_stats['count']:.1f} MB")
                
                if pdf_stats['categories']:
                    print("\n  Распределение по категориям:")
                    for cat, count in pdf_stats['categories'].items():
                        print(f"    {cat}: {count} файлов")
                        
        except Exception as e:
            print(f"❌ Ошибка при подсчете статистики: {e}")
            
    def run(self):
        """Главное меню программы"""
        print(f"""
╔════════════════════════════════════════════╗
║     Smart Downloads Sorter v{self.version}         ║
║     Умный сортировщик с PDF Intelligence  ║
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
            print("7. 📄 PDF настройки")
            print("8. 📊 Статистика")
            print("9. 📁 Изменить папку загрузок")
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
                    self.pdf_menu()
                elif choice == "8":
                    self.show_statistics()
                elif choice == "9":
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
