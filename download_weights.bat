@echo off
echo ===================================
echo = Загрузка весов для EVE Online Discovery Bot =
echo ===================================
echo.

:: Проверяем наличие PowerShell
where powershell >nul 2>&1
if errorlevel 1 (
    echo Ошибка: PowerShell не найден.
    echo Для загрузки весов необходима Windows 7 или выше с PowerShell.
    pause
    exit /b 1
)

:: Создаем папку для весов, если её нет
if not exist weights mkdir weights

:: URL для загрузки весов
:: Здесь можно использовать Google Drive, Dropbox, Яндекс.Диск и т.д.
:: Пример URL для модели (замените на ваш)
set WEIGHTS_URL=https://drive.google.com/uc?export=download^&id=YOUR_FILE_ID

echo Начинаем загрузку весов модели...
echo Это может занять некоторое время в зависимости от скорости интернета.

:: Используем PowerShell для загрузки файла
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%WEIGHTS_URL%' -OutFile 'weights/model.pth'}"

if errorlevel 1 (
    echo Ошибка при загрузке весов модели.
    echo Проверьте подключение к интернету и URL.
    echo.
    echo Вы можете загрузить веса вручную по следующей ссылке:
    echo %WEIGHTS_URL%
    echo И поместить их в папку 'weights' с именем 'model.pth'
    pause
    exit /b 1
)

echo.
echo Весы модели успешно загружены!
echo Теперь вы можете запустить приложение с помощью run.bat
echo.

pause
exit /b 0 