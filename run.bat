@echo off
:: --- Логика запуска ---
:: Устанавливаем кодировку для корректного отображения кириллицы
chcp 65001 >nul
if "%1"=="hidden" goto HIDDEN

title EVE Discovery Bot Loader
cls

echo Загрузка бота...
timeout /t 1 /nobreak > nul

:: Запускаем в скрытом режиме
start "" "%~dp0invisible.vbs" "%~dpnx0" hidden
exit

:HIDDEN
:: Проверяем наличие виртуального окружения
if not exist .venv (
    echo Error: Virtual environment not found. > error_log.txt
    exit /b 1
)

:: Запускаем приложение
call .venv\Scripts\activate.bat
python launcher.py
call .venv\Scripts\deactivate.bat

exit /b 0 