@echo off
echo ===================================
echo = Запуск EVE Online Discovery Bot =
echo ===================================
echo.

:: Проверяем наличие виртуального окружения
if not exist .venv (
    echo Ошибка: Виртуальное окружение не найдено.
    echo Пожалуйста, убедитесь, что проект установлен правильно.
    pause
    exit /b 1
)

:: Активируем виртуальное окружение
call .venv\Scripts\activate.bat

:: Запускаем приложение
echo Запуск EVE Online Discovery Bot...
python launcher.py
if errorlevel 1 (
    echo Произошла ошибка при запуске приложения.
    pause
)

:: Деактивируем виртуальное окружение
deactivate
exit /b 0 