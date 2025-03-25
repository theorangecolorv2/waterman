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
    echo Для обновления необходимо установить Git.
    echo Скачать: https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Создаем резервные копии
echo Создаем резервные копии...
if not exist backups mkdir backups
if exist config.json copy config.json backups\config.json.bak /y
if exist settings.json copy settings.json backups\settings.json.bak /y

:: Удаляем временную папку
echo Очищаем временную папку...
if exist temp_update rd /s /q temp_update
mkdir temp_update
cd temp_update

:: Скачиваем репозиторий
echo Скачиваем файлы из репозитория...
git clone https://github.com/theorangecolorv2/waterman .
if errorlevel 1 (
    echo Ошибка при скачивании.
    cd ..
    pause
    exit /b 1
)

:: Удаляем старые файлы
echo Удаляем старые файлы...
cd ..
del *.py /q
del *.json /q
del *.md /q
del *.jpg /q
del *.png /q
del *.vbs /q
del *.txt /q
for %%F in (*.bat) do (
    if /i not "%%~nxF"=="update_files_clean.bat" del "%%F"
)

:: Копируем новые файлы
echo Копируем новые файлы...
cd temp_update
for %%F in (*.*) do (
    if /i not "%%~nxF"=="update_files_clean.bat" (
        copy "%%F" .. /y
    )
)

:: Обрабатываем модули
echo Обновляем модули...
if not exist ..\modules mkdir ..\modules
del /q ..\modules\*.*
if exist modules xcopy modules\*.* ..\modules\ /s /e /y

:: Обрабатываем assets
echo Обновляем assets...
if not exist ..\assets mkdir ..\assets
del /q ..\assets\*.*
if exist assets xcopy assets\*.* ..\assets\ /s /e /y

:: Копируем другие директории
echo Обновляем другие директории...
for /d %%D in (*) do (
    if /i not "%%~nxD"=="modules" if /i not "%%~nxD"=="assets" if /i not "%%~nxD"==".git" (
        if not exist "..\%%~nxD" mkdir "..\%%~nxD"
        xcopy "%%D\*.*" "..\%%D\" /s /e /y
    )
)

:: Восстанавливаем настройки
echo Восстанавливаем настройки...
cd ..
if exist backups\config.json.bak copy backups\config.json.bak config.json /y
if exist backups\settings.json.bak copy backups\settings.json.bak settings.json /y

echo.
echo Файлы успешно обновлены!
echo Теперь вы можете запустить приложение с помощью run.bat
echo.

pause
exit /b 0
