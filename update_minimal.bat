@echo off
chcp 65001 >nul
echo ===================================
echo = Минимальное обновление EVE Online Discovery Bot =
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

echo Копируем код и скрипты из репозитория...
cd ..

:: Удаляем только Python файлы и батники, не трогая изображения и данные
echo Удаляем старые Python файлы...
del *.py /q

echo Удаляем старые батники (кроме текущих update_*.bat)...
for %%F in (*.bat) do (
    if /i not "%%~nxF"=="update_files.bat" if /i not "%%~nxF"=="update_minimal.bat" del "%%F"
)

:: Копируем только Python файлы
echo Копируем Python файлы...
cd temp_update
copy *.py .. /y

:: Копируем батники, кроме update_*.bat
echo Копируем батники...
for %%F in (*.bat) do (
    if /i not "%%~nxF:~0,7"=="update_" (
        echo Копируем %%~nxF...
        copy "%%F" .. /y
    )
)

:: Обновляем только модули
echo Обновляем модули...
if not exist ..\modules mkdir ..\modules
del /q ..\modules\*.py
if exist modules (
    echo Копируем файлы модулей...
    xcopy modules\*.py ..\modules\ /s /e /y
)

:: Восстанавливаем настройки
echo Восстанавливаем настройки...
cd ..
if exist backups\config.json.bak copy backups\config.json.bak config.json /y
if exist backups\settings.json.bak copy backups\settings.json.bak settings.json /y

echo.
echo Код и скрипты успешно обновлены!
echo Изображения и другие файлы не были затронуты.
echo Теперь вы можете запустить приложение с помощью run.bat
echo.

pause
exit /b 0 