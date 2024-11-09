:: NOTE: To unzip the created zip file, need to use 7-Zip or tar (only available on Windows 10 and up). The default Windows extracter does not like the resulting zip that tar creates.
::       If using tar to unzip, make sure the destination folder exists and then use the following command: tar.exe -xvf TOOL_NAME.zip -C DESTINATION_PATH

@echo off
set tool_name=mtg_bookmark_iterator
set pretty_tool_name=MTG Bookmark Iterator
set divider=------------------------------------------------------------
echo %divider%
echo Packaging %pretty_tool_name% tool...
echo %divider%
pyinstaller %tool_name%.py
echo/
echo/
echo %divider%
echo Copying files over to packaged location...
echo %divider%
call __set_up_tool_location.bat packaging
echo/
echo/
echo %divider%
echo Creating %tool_name%.zip...
echo %divider%
tar.exe -a -cvf %tool_name%.zip -C .\dist\%tool_name% .
echo/
echo/
echo %pretty_tool_name% tool has been successfully packaged into %tool_name%.zip
echo/
pause
