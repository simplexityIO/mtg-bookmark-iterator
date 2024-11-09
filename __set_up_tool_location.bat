:: Initialize environment
@echo off
setlocal enabledelayedexpansion


:: Initialize variables
set tool_name=mtg_bookmark_iterator
set pretty_tool_name=MTG Bookmark Iterator
set packaging_flag=packaging
set are_packaging=false


:: Handle flags
if "%~1" == "%packaging_flag%" set are_packaging=true
if %are_packaging% == true (
    rem echo --------------------------------------------------
    rem echo Packaging %pretty_tool_name% tool
    rem echo --------------------------------------------------
    rem echo/
    set tool_location=.\dist\%tool_name%
    rem ::echo "%tool_location%"
    rem echo/
    goto Set_Up_Tool_Location
)

:: Todo O: Remove
:: pause && exit



:Prompt_For_Tool_Location

:: Prompt for location to set up tool
echo Enter the location at which to set up the %pretty_tool_name% tool:
set /p tool_location=


:: Verify the tool location given is valid and prompt again if it isn't
if exist %tool_location%\* goto Set_Up_Tool_Location
echo Location does not exist. Please enter a valid location.
echo/
goto Prompt_For_Tool_Location


:Set_Up_Tool_Location

:: Copy the below folders/files to tool location
:: Note: The below logic creates one list ('items_list') and transforms it into a different type that can be traversed in a simpler fashion ('items')
set items_list[0]=__set_up_tool_location.bat
set items_list[1]=%tool_name%.py
set items_list[2]=urls
set items_list[3]=config.json
set items_list[4]=urls.txt
set items_list[5]=excluded_urls.txt
set items_list[6]=mtg_bookmark_iterator.bat
set items_list[7]=check_for_duplicates.bat
set items_list[8]=convert_urls_to_scryfall.bat

if %are_packaging% == true (
    set first_item_idx=0
) else (
    set first_item_idx=1
)

set items_len=%first_item_idx%
:Items_Len_Loop
if defined items_list[%items_len%] (
   set /a "items_len+=1"
   goto Items_Len_Loop
)

set items=
for /L %%I in (%first_item_idx%,1,%items_len%) do call set items=%%items%%;%%items_list[%%I]%%

for %%X in (%items%) do ( 
    set item=%%X
    if exist !item!\* (
        echo Copying folder !item!...
        xcopy "!item!" "%tool_location%\!item!" /h /i /c /k /e /r /y /z
        echo/
    ) else if exist !item! (
        echo Copying file !item!...
        xcopy "!item!" "%tool_location%" /c /k /r /y /z
        echo/
    )
)


:: Only create shortcuts back to python environment and wait for user to continue when not packaging
if %are_packaging% == true goto Finished

:: Create tool's python environment shortcut
echo Creating tools_python_environment.lnk...
echo/
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%tool_location%\tools_python_environment.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "%CD%" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript /nologo create_shortcut.vbs
del create_shortcut.vbs


:: Create shortcut to tool executable    
echo Creating %tool_name%.exe.lnk...
echo/
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%tool_location%\%tool_name%.exe.lnk" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "C:\Windows\System32\cmd.exe" >> create_shortcut.vbs
echo oLink.Arguments = "/c ""%CD%\mtg_bookmark_iterator.exe --location %%CD%%""" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%tool_location%" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs
cscript /nologo create_shortcut.vbs
del create_shortcut.vbs


:: Print out that successfully set up the tool location and keep window open
echo/
echo/
echo %pretty_tool_name% tool has been successfully set up at %tool_location%
echo/
pause


:Finished