:: The basic library included all routines that needs by pytoshell

:: Get the type of an object
:@pytsitype object
setlocal
call :@pytsistr_remove_quotes %1
set "@PYTSV-OBJECT=%@PYTSR%"
for /f "tokens=1 delims=@" %%a in ("%@PYTSV-OBJECT%") do set "@PYTSR=%%a"
endlocal & set "@PYTSR=%@PYTSR%"
exit /b %ERRORLEVEL%

:@pytsistr_remove_quotes self
for /f "useback tokens=*" %%a in ('%1') do set "@PYTSR=%%~a"
endlocal & set "@PYTSR=%@PYTSR%"
exit /b %ERRORLEVEL%
