pyinstaller main.py -w  --add-data "icons\appIcon.ico;." --icon="icons\appIcon.ico"
robocopy "sfx" "dist\main\sfx" /E /Z /R:5 /W:5
robocopy "icons" "dist\main\icons" /E /Z /R:5 /W:5
cd dist\main
ren "main.exe" "Thingamalogger.exe"