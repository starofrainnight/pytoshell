:: The basic library included all routines that needs by pytoshell

:: Get the type of an object
:@PYTSVTYPE OBJECT
SETLOCAL
CALL :@PYTSVSTR_REMOVE_QUOTES %1
SET "@PYTSV-OBJECT=%@PYTSR%"
FOR /F "tokens=1 delims=@" %%A IN ("%@PYTSV-OBJECT%") DO SET "@PYTSR=%%A"
ENDLOCAL & SET "@PYTSR=%@PYTSR%"
EXIT /B %ERRORLEVEL%

:@PYTSVSTR_REMOVE_QUOTES SELF
FOR /F "useback tokens=*" %%A IN ('%1') DO SET "@PYTSR=%%~A"
ENDLOCAL & SET "@PYTSR=%@PYTSR%"
EXIT /B %ERRORLEVEL%
