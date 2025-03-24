@echo off
chcp 65001 >nul
echo ===================================
echo = Обновление файлов EVE Online Discovery Bot =
echo ===================================
echo.

:: Проверяем наличие PowerShell
where powershell >nul 2>&1
if errorlevel 1 (
    echo Ошибка: PowerShell не найден.
    echo Для обновления файлов необходима Windows 7 или выше с PowerShell.
    pause
    exit /b 1
)

:: Создаем временные папки
echo Создаем временные папки для обновления...
if not exist temp_update mkdir temp_update
if not exist temp_update\zip mkdir temp_update\zip
if not exist temp_update\extract mkdir temp_update\extract

:: URL к ZIP-архиву репозитория 
set REPO_URL=https://github.com/репозиторий/eve_discovery_bot/archive/refs/heads/main.zip

:: Скачиваем ZIP архив с помощью PowerShell
echo Скачиваем файлы проекта...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%REPO_URL%', 'temp_update\zip\repo.zip')"
if errorlevel 1 (
    echo Ошибка при скачивании файлов.
    echo Проверьте подключение к интернету и URL репозитория.
    rmdir /s /q temp_update
    pause
    exit /b 1
)

:: Распаковываем ZIP архив
echo Распаковываем архив...
powershell -Command "Expand-Archive -Path 'temp_update\zip\repo.zip' -DestinationPath 'temp_update\extract' -Force"
if errorlevel 1 (
    echo Ошибка при распаковке архива.
    rmdir /s /q temp_update
    pause
    exit /b 1
)

:: Определяем имя папки после извлечения
for /d %%i in (temp_update\extract\*) do set EXTRACT_DIR=%%i

:: Копируем файлы проекта
echo Копируем файлы проекта...

:: Копируем Python файлы
copy "%EXTRACT_DIR%\*.py" . /y

:: Копируем JSON файлы конфигурации
copy "%EXTRACT_DIR%\*.json" . /y

:: Копируем MD файлы
copy "%EXTRACT_DIR%\*.md" . /y

:: Копируем JPG файлы
copy "%EXTRACT_DIR%\*.jpg" . /y

:: Копируем PNG файлы
copy "%EXTRACT_DIR%\*.png" . /y

:: Копируем BAT файлы (кроме текущего)
for %%f in ("%EXTRACT_DIR%\*.bat") do (
    if not "%%~nxf"=="update_files_no_git.bat" copy "%%f" . /y
)

:: Создаем папку assets, если её нет
if not exist assets mkdir assets

:: Копируем содержимое папки assets
if exist "%EXTRACT_DIR%\assets" (
    xcopy "%EXTRACT_DIR%\assets\*" assets\ /s /e /y
)

:: Удаляем временные файлы
echo Удаляем временные файлы...
rmdir /s /q temp_update

echo.
echo Файлы успешно обновлены!
echo Теперь вы можете запустить приложение с помощью run.bat
echo.

pause
exit /b 0 