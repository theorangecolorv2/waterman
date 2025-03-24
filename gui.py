import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import os
import threading
import sys
import json
from PIL import Image, ImageTk, UnidentifiedImageError
import datetime
import time
import subprocess
import platform
import webbrowser
import tempfile
import re

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

# Импортируем модули для запуска бота
from config import LAUNCHER_PATH, ACCOUNTS_FOLDER, CURRENT_ACCOUNT, LOOP_LIMIT, RANDOM_ACTIONS
import importlib
from modules.find_image import exists

from swap_accounts import swap_accounts


class BotConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EVE Online Discovery Bot")
        self.root.geometry("1280x720")
        self.root.resizable(True, True)
        
        # Переменные для хранения значений конфигурации
        self.launcher_path_var = tk.StringVar(value=LAUNCHER_PATH)
        self.accounts_folder_var = tk.StringVar(value=ACCOUNTS_FOLDER)
        self.current_account_var = tk.IntVar(value=CURRENT_ACCOUNT)
        self.loop_limit_var = tk.IntVar(value=LOOP_LIMIT)
        self.random_actions_var = tk.BooleanVar(value=RANDOM_ACTIONS)
        
        # Настройки конфигурации
        self.config_file = "bot_config.json"
        self.load_config()
        
        # Настраиваем стили
        self.configure_styles()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Статус бота
        self.bot_running = False
        self.bot_thread = None
    
    def configure_styles(self):
        """Настраивает стили для виджетов"""
        style = ttk.Style()
        
        # Проверяем доступные шрифты
        available_fonts = font.families()
        
        # Выбираем шрифт
        if "Roboto" in available_fonts:
            button_font = ("Roboto", 12, "bold")
            header_font = ("Roboto", 12, "bold")
        elif "Open Sans" in available_fonts:
            button_font = ("Open Sans", 12, "bold")
            header_font = ("Open Sans", 12, "bold")
        else:
            # Используем стандартный шрифт, если Roboto и Open Sans недоступны
            button_font = ("Arial", 12, "bold")
            header_font = ("Arial", 12, "bold")
        
        # Настраиваем стили для кнопок
        style.configure("TButton", font=button_font, padding=(10, 8))
        style.configure("Accent.TButton", font=button_font, padding=(20, 12))
        
        # Стиль для заголовков
        style.configure("Header.TLabel", font=header_font)

    def create_widgets(self):
        # Основной фрейм с отступами
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем контейнер с двумя колонками
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка для элементов управления
        left_frame = ttk.Frame(content_frame, padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Правая колонка для изображения
        right_frame = ttk.Frame(content_frame, padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        # === НАСТРОЙКИ ПУТЕЙ ===
        path_frame = ttk.LabelFrame(left_frame, text="Настройки путей", padding=10)
        path_frame.pack(fill=tk.X, pady=5)
        
        # Путь к лаунчеру
        ttk.Label(path_frame, text="Путь к лаунчеру:").grid(row=0, column=0, sticky=tk.W, pady=5)
        launcher_entry = ttk.Entry(path_frame, textvariable=self.launcher_path_var, width=50)
        launcher_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Button(path_frame, text="Обзор", command=self.browse_launcher_path).grid(row=0, column=2, padx=5)
        
        # Путь к папке с аккаунтами
        ttk.Label(path_frame, text="Путь к папке с аккаунтами:").grid(row=1, column=0, sticky=tk.W, pady=5)
        accounts_entry = ttk.Entry(path_frame, textvariable=self.accounts_folder_var, width=50)
        accounts_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Button(path_frame, text="Обзор", command=self.browse_accounts_folder).grid(row=1, column=2, padx=5)
        
        # === НАСТРОЙКИ БОТА ===
        bot_frame = ttk.LabelFrame(left_frame, text="Настройки бота", padding=10)
        bot_frame.pack(fill=tk.X, pady=5)
        
        # Номер текущего аккаунта
        ttk.Label(bot_frame, text="Текущий аккаунт:").grid(row=0, column=0, sticky=tk.W, pady=5)
        account_spinbox = ttk.Spinbox(bot_frame, from_=1, to=10, textvariable=self.current_account_var, width=10)
        account_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Ограничение количества циклов
        ttk.Label(bot_frame, text="Лимит циклов:").grid(row=1, column=0, sticky=tk.W, pady=5)
        limit_spinbox = ttk.Spinbox(bot_frame, from_=1, to=1000, textvariable=self.loop_limit_var, width=10)
        limit_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Рандомные действия
        ttk.Label(bot_frame, text="Рандомные действия:").grid(row=2, column=0, sticky=tk.W, pady=5)
        random_actions_check = ttk.Checkbutton(bot_frame, variable=self.random_actions_var)
        random_actions_check.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # === КНОПКИ УПРАВЛЕНИЯ ===
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=15)
        
        # Кнопка "Ниче не понятно" (помощь)
        help_button = ttk.Button(
            control_frame,
            text="Ниче не понятно",
            command=self.open_readme,
            style="TButton"
        )
        help_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Кнопка сохранения настроек
        ttk.Button(
            control_frame, 
            text="Сохранить настройки", 
            command=self.save_config
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Кнопка запуска бота
        self.start_button = ttk.Button(
            control_frame, 
            text="Начать грести баксы",
            command=self.start_bot,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Кнопка остановки бота
        self.stop_button = ttk.Button(
            control_frame, 
            text="Зачилл",
            command=self.stop_bot,
            style="TButton",
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # === ЛЕГО ВЫВОДА ===
        ttk.Label(left_frame, text="Массажка:", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 5))
        
        # Текстовое поле для вывода лога
        self.log_text = tk.Text(left_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для текстового поля
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Заблокируем редактирование текстового поля
        self.log_text.config(state=tk.DISABLED)

        # === ДОБАВЛЕНИЕ ИЗОБРАЖЕНИЯ ===
        # Создаем фрейм для изображения в правой колонке
        image_frame = ttk.LabelFrame(right_frame, text="пацаны смотрите какой мэмчик нашел", padding=0)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=0)

        # Место для отображения изображения
        self.image_container = ttk.Frame(image_frame, width=280, height=280)
        self.image_container.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)
        
        # Загружаем статическое изображение
        self.load_meme_image()
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Бот не запущен")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_meme_image(self):
        """Загружает изображение для отображения в интерфейсе"""
        # Очищаем контейнер от предыдущих виджетов
        for widget in self.image_container.winfo_children():
            widget.destroy()
            
        # Фиксированный путь к изображению
        meme_path = "meme.jpg"
            
        # Проверяем существование файла изображения
        if os.path.exists(meme_path) and os.path.getsize(meme_path) > 0:
            try:
                # Загружаем изображение с помощью PIL
                original_image = Image.open(meme_path)
                
                # Получаем размеры изображения
                width, height = original_image.size
                
                # Не увеличиваем ширину, оставляем исходные размеры
                target_width = width
                target_height = height
                
                # Задаем максимальные размеры контейнера
                max_width = 280
                max_height = 280
                
                # Проверяем, не превышает ли изображение размеры контейнера
                if target_width > max_width or target_height > max_height:
                    # Вычисляем коэффициент масштабирования, чтобы изображение целиком поместилось в контейнер
                    width_ratio = max_width / target_width
                    height_ratio = max_height / target_height
                    scale_ratio = min(width_ratio, height_ratio)
                    
                    # Вычисляем новые размеры с учетом масштабирования
                    new_width = int(target_width * scale_ratio)
                    new_height = int(target_height * scale_ratio)
                    
                    # Изменяем размер изображения с сохранением пропорций
                    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
                else:
                    # Если изображение меньше контейнера, оставляем как есть
                    resized_image = original_image
                    
                # Преобразуем в формат для Tkinter
                self.meme_image = ImageTk.PhotoImage(resized_image)
                
                # Создаем метку для отображения изображения
                image_label = ttk.Label(self.image_container, image=self.meme_image)
                image_label.pack(padx=0, pady=0, anchor=tk.CENTER)
                
                # Выводим информацию о размерах
                self.log(f"Загружено изображение: размер {resized_image.width}x{resized_image.height}")

            except (UnidentifiedImageError, IOError, Exception) as e:
                # Если возникла ошибка при загрузке изображения
                error_label = ttk.Label(
                    self.image_container, 
                    text=f"Ошибка загрузки изображения: {type(e).__name__}\n{str(e)}",
                    wraplength=280
                )
                error_label.pack(padx=5, pady=30, anchor=tk.CENTER)
                self.log(f"Ошибка загрузки изображения {meme_path}: {str(e)}")
        else:
            # Если изображение не найдено, показываем сообщение
            not_found_label = ttk.Label(
                self.image_container, 
                text="Изображение meme.jpg не найдено или пустое.\nПоместите файл meme.jpg в корневую папку проекта.",
                wraplength=280
            )
            not_found_label.pack(padx=5, pady=50, anchor=tk.CENTER)
            self.log("Изображение meme.jpg не найдено или пустое")

    def browse_launcher_path(self):
        """Открывает диалог выбора файла для пути к лаунчеру"""
        path = filedialog.askopenfilename(
            title="Выберите файл лаунчера",
            filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
        )
        if path:
            self.launcher_path_var.set(path)
    
    def browse_accounts_folder(self):
        """Открывает диалог выбора папки для аккаунтов"""
        path = filedialog.askdirectory(title="Выберите папку с изображениями аккаунтов")
        if path:
            self.accounts_folder_var.set(path)
            
    def save_config(self):
        """Сохраняет текущие настройки в файл конфигурации и обновляет глобальные переменные"""
        # Создаем конфигурацию для сохранения
        config = {
            "launcher_path": self.launcher_path_var.get(),
            "accounts_folder": self.accounts_folder_var.get(),
            "current_account": self.current_account_var.get(),
            "loop_limit": self.loop_limit_var.get(),
            "random_actions": self.random_actions_var.get()
        }
        
        # Сохраняем конфигурацию в файл
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Обновляем модуль config.py
            self.update_config_module(config)
            

            self.log("Настройки успешно сохранены")
        except Exception as e:
            self.log(f"Ошибка сохранения настроек: {str(e)}")
    
    def update_config_module(self, config):
        """Обновляет глобальные переменные в модуле config.py"""
        try:
            # Открываем файл с явным указанием кодировки UTF-8
            with open("config.py", 'w', encoding='utf-8') as f:
                f.write('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n\n')
                f.write('"""\nФайл с глобальными настройками для бота\n"""\n\n')
                f.write('import os\n\n')
                f.write(f'# Путь к лаунчеру EVE Online\n')
                f.write(f'# Используем переменную среды LOCALAPPDATA для получения пути к локальным данным приложений\n')
                f.write(f'LAUNCHER_PATH = r"{config["launcher_path"]}"\n\n')
                f.write(f'# Путь к папке с изображениями аккаунтов\n')
                f.write(f'# Используем путь относительно текущей рабочей директории\n')
                f.write(f'ACCOUNTS_FOLDER = r"{config["accounts_folder"]}"\n\n')
                f.write(f'# Текущий аккаунт\n')
                f.write(f'CURRENT_ACCOUNT = {config["current_account"]}\n\n')
                f.write(f'# Лимит повторений цикла\n')
                f.write(f'LOOP_LIMIT = {config["loop_limit"]}\n\n')
                f.write(f'# Выполнять рандомные действия\n')
                f.write(f'RANDOM_ACTIONS = {config["random_actions"]}\n')
                f.write(f' #pidorsi\n')
            
            # Перезагружаем модуль
            import config
            importlib.reload(config)
        except Exception as e:
            self.log(f"Ошибка обновления config.py: {str(e)}")
    
    def load_config(self):
        """Загружает настройки из файла конфигурации"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Устанавливаем значения переменных из конфигурации
                self.launcher_path_var.set(config.get("launcher_path", LAUNCHER_PATH))
                self.accounts_folder_var.set(config.get("accounts_folder", ACCOUNTS_FOLDER))
                self.current_account_var.set(config.get("current_account", CURRENT_ACCOUNT))
                self.loop_limit_var.set(config.get("loop_limit", LOOP_LIMIT))
                self.random_actions_var.set(config.get("random_actions", RANDOM_ACTIONS))
        except Exception as e:
            self.log(f"Ошибка загрузки настроек: {str(e)}")
    
    def start_bot(self):
        """Запускает бота в отдельном потоке"""
        if self.bot_running:
            self.log("Бот уже запущен")
            return
        
        # Перед запуском сохраняем текущие настройки
        self.save_config()
        
        # Запускаем бота в отдельном потоке
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        # Обновляем статус и кнопки
        self.bot_running = True
        self.status_var.set("Бот запущен")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Записываем в лог текущее время и сообщение о запуске
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"[{current_time}] Бот запущен")
    
    def stop_bot(self):
        """Останавливает работу бота"""
        if not self.bot_running:
            return
        
        # Устанавливаем флаг для остановки бота
        self.bot_running = False
        self.status_var.set("Останавливаем бота...")
        self.log("Останавливаем бота...")
        
        # Ждем завершения потока
        if self.bot_thread and self.bot_thread.is_alive():
            self.bot_thread.join(timeout=2)
        
        # Обновляем статус и кнопки
        self.status_var.set("Бот остановлен")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"[{current_time}] Бот остановлен")
    
    def run_bot(self):
        """Функция для запуска бота в отдельном потоке"""
        try:
            self.log("Начинаем работу бота...")
            
            # Перенаправляем стандартный вывод, чтобы логировать сообщения от бота
            original_stdout = sys.stdout
            sys.stdout = self
            
            # Импортируем и запускаем код бота
            try:
                # Перезагружаем модули, чтобы учесть изменения в конфигурации
                import main
                import config
                import research
                importlib.reload(config)
                importlib.reload(research)
                importlib.reload(main)
                
                # Запускаем основную функцию бота
                from research import account_process
                from swap_accounts import swap_accounts
                
                # Записываем отчет о запуске
                self.log(f"Настройки бота: Лаунчер={config.LAUNCHER_PATH}, Аккаунты={config.ACCOUNTS_FOLDER}, Аккаунт #{config.CURRENT_ACCOUNT}, Лимит={config.LOOP_LIMIT}, Рандомные действия={'Вкл' if config.RANDOM_ACTIONS else 'Выкл'}")
                
                # Флаг для продолжения работы с аккаунтами
                continue_processing = True
                
                while continue_processing and self.bot_running:
                    current_account = config.CURRENT_ACCOUNT
                    
                    # Проверяем, нужно ли предварительно запустить игру
                    if not exists("./assets/demarcate.png"):
                        self.log(f"Запускаем игру для аккаунта #{current_account}")
                        swap_accounts(launcher_path=config.LAUNCHER_PATH, current_account=current_account)
                        time.sleep(2)  # Даем время на запуск игры
                    
                    # Запускаем бота и получаем результат
                    self.log(f"Запускаем обработку для аккаунта #{current_account}")
                    result = account_process()
                    
                    # Обрабатываем различные результаты
                    if result == "missing_assets":
                        self.log("ОШИБКА: Отсутствуют необходимые изображения в папке assets")
                        self.log("Проверьте наличие всех необходимых изображений в папке assets")
                        continue_processing = False
                    elif result == "reference_not_found":
                        self.log("ОШИБКА: Не удалось найти опорную точку на экране")
                        self.log("Убедитесь, что EVE Online запущена и находится в нужном режиме")
                        continue_processing = False
                    elif result == "lim" or result is None:
                        # Достигнут лимит, меняем аккаунт
                        if result == "lim":
                            self.log("Достигнут лимит повторений или дневной лимит")
                        else:
                            self.log("Обработка аккаунта завершена без явного результата")
                        
                        # Увеличиваем номер аккаунта (инкрементация вынесена на уровень выше)
                        new_account = current_account + 1
                        if new_account > 30:  # Предполагаем, что у нас не более 10 аккаунтов
                            self.log("Достигнут максимальный номер аккаунта, завершаем работу")
                            continue_processing = False
                        else:
                            self.log(f"Меняем аккаунт #{current_account} на аккаунт #{new_account}")
                            
                            # Обновляем конфигурацию
                            config.CURRENT_ACCOUNT = new_account
                            self.current_account_var.set(new_account)
                            
                            # Сохраняем изменения в конфигурационном файле
                            self.update_config_module({
                                "launcher_path": config.LAUNCHER_PATH, 
                                "accounts_folder": config.ACCOUNTS_FOLDER,
                                "current_account": new_account,
                                "loop_limit": config.LOOP_LIMIT
                            })
                            
                            # Выполняем смену аккаунта
                            self.log(f"Выполняем смену на аккаунт #{new_account}")
                            swap_accounts(launcher_path=config.LAUNCHER_PATH, current_account=new_account)
                            time.sleep(10)  # Даем время на запуск игры
                    elif result == "error":
                        self.log("Работа завершена из-за ошибки в процессе выполнения")
                        continue_processing = False
                    elif result == "completed":
                        self.log("Работа успешно завершена")
                        continue_processing = False
                    else:
                        self.log(f"Результат работы бота: {result}")
                        continue_processing = False
                    
            except ImportError as e:
                self.log(f"ОШИБКА ИМПОРТА: Не удалось загрузить модуль: {str(e)}")
                self.log("Проверьте, что все необходимые модули установлены и доступны")
            except Exception as e:
                self.log(f"ОШИБКА: {type(e).__name__}: {str(e)}")
                import traceback
                error_traceback = traceback.format_exc()
                for line in error_traceback.split("\n"):
                    if line.strip():
                        self.log(line)
            finally:
                # Восстанавливаем стандартный вывод
                sys.stdout = original_stdout
            
            self.log("Работа бота завершена")
            
        except Exception as e:
            self.log(f"КРИТИЧЕСКАЯ ОШИБКА: {type(e).__name__}: {str(e)}")
            import traceback
            error_traceback = traceback.format_exc()
            for line in error_traceback.split("\n"):
                if line.strip():
                    self.log(line)
        finally:
            # Обновляем статус и кнопки
            self.root.after(0, self.update_ui_after_bot_stop)
    
    def update_ui_after_bot_stop(self):
        """Обновляет UI после остановки бота"""
        self.bot_running = False
        self.status_var.set("Бот остановлен")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def open_readme(self):
        """Открывает файл README.md в браузере в отрендеренном виде"""
        readme_path = os.path.join(os.getcwd(), "README.md")
        
        if not os.path.exists(readme_path):
            messagebox.showerror("Ошибка", "Файл README.md не найден")
            self.log("Ошибка: файл README.md не найден")
            return
        
        try:
            # Открываем README.md и читаем содержимое
            with open(readme_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
                
            # Конвертируем Markdown в HTML
            if MARKDOWN_AVAILABLE:
                # Используем библиотеку markdown для преобразования
                html_content = markdown.markdown(
                    markdown_content,
                    extensions=['tables', 'fenced_code', 'codehilite', 'nl2br']
                )
            else:
                # Базовое форматирование, если библиотека не установлена
                html_content = f"<pre>{markdown_content}</pre>"
                self.log("Предупреждение: Установите библиотеку 'markdown' для лучшего отображения README.md")
            
            # Получаем абсолютный путь к рабочей директории
            work_dir = os.getcwd()
            
            # Заменяем относительные пути к изображениям на абсолютные,
            # включая изображения в корневой директории и в папке assets
            def fix_image_path(match):
                img_path = match.group(1)
                # Если путь не начинается с http или другой схемы URL
                if not re.match(r'^(https?|file|data):', img_path):
                    # Формируем абсолютный путь
                    abs_path = os.path.normpath(os.path.join(work_dir, img_path))
                    # Используем file:// протокол для правильного отображения
                    return f'<img src="file://{abs_path}"'
                return match.group(0)
            
            # Применяем регулярное выражение для замены путей
            html_content = re.sub(r'<img src="([^"]+)"', fix_image_path, html_content)
                
            # Создаём HTML документ с полной структурой и стилями
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>README - EVE Online Discovery Bot</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    h1, h2, h3 {{
                        color: #2c3e50;
                    }}
                    code, pre {{
                        background-color: #f5f5f5;
                        border: 1px solid #ddd;
                        border-radius: 3px;
                        padding: 2px 5px;
                        font-family: Consolas, monospace;
                    }}
                    pre {{
                        padding: 10px;
                        overflow-x: auto;
                    }}
                    img {{
                        max-width: 100%;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 5px;
                    }}
                    blockquote {{
                        border-left: 4px solid #ddd;
                        padding-left: 10px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <h1></h1>
                {html_content}
                <hr>
              
            </body>
            </html>
            """
            
            # Создаём временный HTML файл
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
                f.write(full_html)
                temp_html_path = f.name
                
            # Открываем временный HTML файл в браузере
            webbrowser.open('file://' + temp_html_path)
            
            self.log("Открыта справка README.md в браузере")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть README.md: {str(e)}")
            self.log(f"Ошибка при открытии README.md: {str(e)}")
            
            # Запасной вариант - открыть исходный файл
            try:
                if platform.system() == 'Windows':
                    os.startfile(readme_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', readme_path])
                else:  # Linux и другие Unix-подобные системы
                    subprocess.call(['xdg-open', readme_path])
            except:
                self.log("Не удалось открыть README.md даже запасным способом")
    
    def log(self, message):
        """Добавляет сообщение в лог"""
        self.root.after(0, self._append_to_log, message)
    
    def _append_to_log(self, message):
        """Добавляет сообщение в текстовое поле лога"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def write(self, text):
        """Метод для перехвата стандартного вывода"""
        if text.strip():
            self.log(text.strip())
    
    def flush(self):
        """Необходимый метод для перехвата стандартного вывода"""
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = BotConfigGUI(root)
    root.mainloop() 