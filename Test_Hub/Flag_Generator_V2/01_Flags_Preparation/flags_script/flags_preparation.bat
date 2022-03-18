@echo off


REM The purpose of this script is to normalize a series of flag images to be used by the flag generator Python addon. 


REM The %~dp0 command designates the script path. I'm pointing to the ffmpeg script's relative path from this active script.
set ffmpegpath=%~dp0..\ffmpeg\bin\ffmpeg.exe

REM The %1 command designates the item that is dragged and dropped onto this script
set inputPath=%1
set resolution=512

REM Creating a loop for each file in the texture folder

REM Technically this means : for every file (the * is essential) in the inputPath, do...

for %%f in (%inputPath%\*) do call :process %%f

PAUSE 

:process
    REM Storing needed variables
    ECHO File found
    set file_path=%~1
    set file_fullname=%~nx1
    set file_name=%~n1
  
    REM Process the image
    "%ffmpegpath%" -i %file_path% -vf scale=%resolution%:%resolution% %inputPath%\%file_name%_reduced_converted.jpg

    REM Delete the original image
    del %file_path%

    REM Rename the new image
    ren "%inputPath%\%file_name%_reduced_converted".jpg "%file_name%".jpg

EXIT /B Q

