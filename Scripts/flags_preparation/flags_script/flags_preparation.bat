REM The purpose of this script is to normalize a series of flag images to be used by the flag generator Python addon. 


REM The %~dp0 command designates the script path. I'm pointing to the ffmpeg script's relative path from this active script.
set ffmpegpath=%~dp0..\ffmpeg\bin\ffmpeg.exe

REM The %1 command designates the item that is dragged and dropped onto this script
set inputPath=%1
set resolution=512

REM Creating a loop for each file in the texture folder

REM Technically this means : for every file (the * is essential) in the inputPath, do...

for %%f in (%inputPath%\*) do (
    REM echo file found
    REM echo fullname : %%f

    REM The name of the image below (for some reason can't store it in a variable)
    echo %%~nf


    REM Process the image
    "%ffmpegpath%" -i %%f -vf scale=%resolution%:%resolution% %inputPath%\%%~nf_reduced_converted.jpg

    REM Delete the original image
    del %%f

    REM Rename the new image
    ren "%inputPath%\%%~nf_reduced_converted".jpg "%%~nf".jpg

    

)


REM Use this if debug needed
@REM pause

