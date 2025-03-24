@echo off
chcp 65001 >nul
echo ===================================
echo = Первоначальная настройка EVE Online Discovery Bot =
echo ===================================
echo.

:: Проверяем, установлен ли Python
python --version > nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден.
    echo Пожалуйста, установите Python 3.7 или выше и добавьте его в PATH.
    echo Скачать Python можно с сайта: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Проверяем наличие виртуального окружения
if not exist .venv (
    echo Создание виртуального окружения...
    python -m venv .venv
    if errorlevel 1 (
        echo Ошибка при создании виртуального окружения.
        pause
        exit /b 1
    )
)

:: Активируем виртуальное окружение
call .venv\Scripts\activate.bat

:: Устанавливаем базовые зависимости
echo Установка базовых зависимостей...
pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка при установке зависимостей из requirements.txt.
        pause
        exit /b 1
    )
) else (
    echo Файл requirements.txt не найден.
    echo Загружаем необходимые файлы проекта...
    
    where powershell >nul 2>&1
    if errorlevel 1 (
        echo Ошибка: PowerShell не найден.
        echo Для загрузки файлов необходима Windows 7 или выше с PowerShell.
        pause
        exit /b 1
    )
    
    :: Здесь можно добавить код для загрузки файлов проекта
    :: (аналогично update_files_no_git.bat)
)

:: Устанавливаем Detectron2 из исходников
echo Установка Detectron2 из исходников...
pip install 'git+https://github.com/facebookresearch/detectron2.git'
if errorlevel 1 (
    echo Ошибка при установке Detectron2.
    echo Проверьте подключение к интернету и наличие Git.
    pause
    exit /b 1
)

:: Создаем необходимые папки
if not exist weights mkdir weights
if not exist accs mkdir accs
if not exist logs mkdir logs

:: Запускаем скрипты для загрузки файлов проекта и весов
echo.
echo Установка базовых компонентов завершена.
echo.

:: Деактивируем виртуальное окружение
deactivate

echo Для загрузки файлов проекта выполните:
echo   update_files.bat (если у вас установлен Git)
echo   или update_files_no_git.bat (без Git)
echo.
echo Для загрузки весовых файлов модели выполните:
echo   download_weights.bat
echo.
echo После завершения всех этапов установки вы сможете запустить бота:
echo   run.bat
echo.

pause
exit /b 0 