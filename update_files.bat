@echo off
chcp 65001 >nul
echo ===================================
echo = Обновление файлов EVE Online Discovery Bot =
echo ===================================
echo.

:: Проверяем, установлен ли Git
where git >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Git не найден.
    echo Для обновления файлов необходимо установить Git.
    echo Скачать Git можно с сайта: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Создаем временную папку для обновления...
if not exist temp_update mkdir temp_update
cd temp_update

:: Клонируем или обновляем репозиторий
if not exist .git (
    echo Клонируем репозиторий...
    git clone https://github.com/theorangecolorv2/waterman .
    if errorlevel 1 (
        echo Ошибка при клонировании репозитория.
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Обновляем репозиторий...
    git pull
    if errorlevel 1 (
        echo Ошибка при обновлении репозитория.
        cd ..
        pause
        exit /b 1
    )
)

echo Копируем файлы проекта...

:: Копируем Python файлы
copy *.py .. /y

:: Копируем JSON файлы конфигурации
copy *.json .. /y

:: Копируем MD файлы
copy *.md .. /y

:: Копируем JPG файлы
copy *.jpg .. /y

:: Копируем PNG файлы
copy *.png .. /y

:: Создаем папку assets, если её нет
if not exist ..\assets mkdir ..\assets

:: Копируем содержимое папки assets
if exist assets (
    xcopy assets\* ..\assets\ /s /e /y
)

:: Возвращаемся в корневую папку
cd ..

echo.
echo Файлы успешно обновлены!
echo Теперь вы можете запустить приложение с помощью run.bat
echo.

pause
exit /b 0 