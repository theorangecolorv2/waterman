@echo off
chcp 65001 >nul
echo ===================================
echo = Создание ярлыка EVE Online Discovery Bot =
echo ===================================
echo.

:: Получаем полный путь к текущей папке
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:~0,-1%

:: Создаем VBS скрипт для создания ярлыка
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo sLinkFile = "%CURRENT_DIR%\EVE Online Discovery Bot.lnk" >> "%TEMP%\create_shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\create_shortcut.vbs"
echo oLink.TargetPath = "%CURRENT_DIR%\run.bat" >> "%TEMP%\create_shortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Description = "EVE Online Discovery Bot" >> "%TEMP%\create_shortcut.vbs"
echo If oWS.FileExists("%CURRENT_DIR%\assets\icon.ico") Then >> "%TEMP%\create_shortcut.vbs"
echo    oLink.IconLocation = "%CURRENT_DIR%\assets\icon.ico" >> "%TEMP%\create_shortcut.vbs"
echo End If >> "%TEMP%\create_shortcut.vbs"
echo oLink.Save >> "%TEMP%\create_shortcut.vbs"

:: Запускаем VBS скрипт
cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo Ярлык "EVE Online Discovery Bot.lnk" успешно создан!
echo Теперь вы можете запускать бота, используя этот ярлык.
echo.

pause
exit /b 0 