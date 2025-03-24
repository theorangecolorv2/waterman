@echo off
:: Скрытый запуск приложения
if "%1"=="hidden" goto HIDDEN
start "" /b wscript.exe "%~dp0invisible.vbs" "%~dpnx0" hidden
exit

:HIDDEN
:: Проверяем наличие виртуального окружения
if not exist .venv (
    start "" cmd /c "echo Ошибка: Виртуальное окружение не найдено. & echo Пожалуйста, убедитесь, что проект установлен правильно. & pause"
    exit /b 1
)

:: Активируем виртуальное окружение и запускаем приложение
call .venv\Scripts\activate.bat
python launcher.py
call .venv\Scripts\deactivate.bat
exit /b 0 