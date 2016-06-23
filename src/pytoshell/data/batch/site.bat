:: The basic library included all routines that needs by pytoshell

:PYTSVtuple.__getitem__
setlocal
    echo set "@PYTSRTEMP_VALUE=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    echo set "@PYTSRTEMP_INDEX=%%%2%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    :: Clear the return variant first
    set "@PYTSR=" & set "@PYTSR-T="
    for /f "tokens=%@PYTSRTEMP_INDEX%" %%a in (%@PYTSRTEMP_VALUE%) do (
        echo set "@PYTSR=%%%%a%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
        echo set "@PYTSR-T=%%%%a-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    )
endlocal & set "@PYTSR=%@PYTSR%" & set "@PYTSR-T=%@PYTSR-T%"
exit /b %ERRORLEVEL%

:PYTSVlen
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
call :PYTSV%@PYTSR-T%.__len__ %1
exit /b %ERRORLEVEL%

:PYTSVstr
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
call :PYTSV%@PYTSR-T%.__str__ %1
exit /b %ERRORLEVEL%

:PYTSVbool
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
call :PYTSV%@PYTSR-T%.__bool__ %1
exit /b %ERRORLEVEL%

:PYTSVprint
echo set "@PYTSRTEMP_VALUE=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
if NOT "%@PYTSRTEMP_VALUE%"=="" (echo %@PYTSRTEMP_VALUE%)
exit /b %ERRORLEVEL%

:PYTSVstr.__bool__
setlocal
    echo set "@PYTSRTEMP_VALUE=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    set "@PYTSR=1"
    if "%@PYTSRTEMP_VALUE%"=="" set "@PYTSR=0"
    set "@PYTSR-T=bool"
endlocal & set "@PYTSR=%@PYTSR%" & set "@PYTSR-T=%@PYTSR-T%"
exit /b %ERRORLEVEL%

:PYTSVstr.__len__
echo set "@PYTSRTEMP_VALUE=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
set "@PYTSR=0"
set "@PYTSR-T=int"

:LABEL_PYTSVstr.__len__0
    if "%@PYTSRTEMP_VALUE%"=="" (goto :LABEL_PYTSVstr.__len__1)
    set /a "@PYTSR +=1"
    set "@PYTSRTEMP_VALUE=%@PYTSRTEMP_VALUE:~1%" ::Remove the first character
goto LABEL_PYTSVstr.__len__0

:LABEL_PYTSVstr.__len__1
exit /b %ERRORLEVEL%

:PYTSVstr.__add__
echo set "@PYTSR=%%%1%%%%%2%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVstr.__mul__
setlocal
    set "@PYTSR="
    echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    echo set "@PYTSRTEMP_VALUE=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    echo set "@PYTSRTEMP_I=%%%2%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT

    :LABEL_PYTSVstr.__mul__0
        if %@PYTSRTEMP_I% LEQ 0 (goto LABEL_PYTSVstr.__mul__1)
        set /a "@PYTSRTEMP_I-=1"
        set "@PYTSR=%@PYTSR%%@PYTSRTEMP_VALUE%"
    goto :LABEL_PYTSVstr.__mul__0

    :LABEL_PYTSVstr.__mul__1
endlocal & set "@PYTSR=%@PYTSR%" & set "@PYTSR-T=%@PYTSR-T%"
exit /b %ERRORLEVEL%

REM String formating
:PYTSVstr.__mod__
setlocal
    echo set "@PYTSRTEMP_RIGHT_T=%%%2-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    if "%@PYTSRTEMP_RIGHT_T%"=="tuple" (
        goto LABEL_PYTSVstr.__mod__parse_tuple
    )
    goto LABEL_PYTSVstr.__mod__normal

    :LABEL_PYTSVstr.__mod__parse_tuple
        echo set "@PYTSRTEMP_STR=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
        echo set "@PYTSRTEMP_STR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
        echo set "@PYTSRTEMP_RIGHT_STR=%%%2%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
        set /a "@PYTSRTEMP_I=0"
        :LABEL_PYTSVstr.__mod__parse_tuple0
            set /a "@PYTSRTEMP_I+=1"
            call :PYTSVtuple.__getitem__ @PYTSRTEMP_RIGHT_STR @PYTSRTEMP_I
            if "%@PYTSR%"=="" goto LABEL_PYTSVstr.__mod__parse_tuple1
            call :PYTSVstr.__mod__ @PYTSRTEMP_STR @PYTSR
            set "@PYTSRTEMP_STR=%@PYTSR%" & set "@PYTSRTEMP_STR-T=%@PYTSR-T%"
        goto LABEL_PYTSVstr.__mod__parse_tuple0

        :LABEL_PYTSVstr.__mod__parse_tuple1
        set "@PYTSR=%@PYTSRTEMP_STR%" & set "@PYTSR-T=%@PYTSRTEMP_STR-T%"
    goto LABEL_PYTSVstr.__mod__exit

    :LABEL_PYTSVstr.__mod__normal
    echo set "@PYTSRTEMP_STR=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    echo set "@PYTSRTEMP_REPLACEMENT=%%%2%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    set "@PYTSRTEMP_CHAR="
    set "@PYTSRTEMP_LAST_CHAR="
    set "@PYTSR="
    set "@PYTSR-T=str"

    :LABEL_PYTSVstr.__mod__0
        if "%@PYTSRTEMP_STR%"=="" (goto LABEL_PYTSVstr.__mod__exit)
        set "@PYTSRTEMP_CHAR=%@PYTSRTEMP_STR:~0,1%" ::Get the first character
        set "@PYTSRTEMP_STR=%@PYTSRTEMP_STR:~1%" ::Remove the first character
        if "%@PYTSRTEMP_LAST_CHAR%"=="%%" (
            if "%@PYTSRTEMP_CHAR%"=="s" (
                set "@PYTSR=%@PYTSR%%@PYTSRTEMP_REPLACEMENT%%@PYTSRTEMP_STR%"
                goto LABEL_PYTSVstr.__mod__exit
            ) else (
                set "@PYTSR=%@PYTSR%%@PYTSRTEMP_CHAR%"
            )
            set "@PYTSRTEMP_LAST_CHAR="
        ) else (
            if NOT "%@PYTSRTEMP_CHAR%"=="%%" (
                set "@PYTSR=%@PYTSR%%@PYTSRTEMP_CHAR%"
            )
            set "@PYTSRTEMP_LAST_CHAR=%@PYTSRTEMP_CHAR%"
        )
    goto LABEL_PYTSVstr.__mod__0

    :LABEL_PYTSVstr.__mod__exit
endlocal & set "@PYTSR=%@PYTSR%" & set "@PYTSR-T=%@PYTSR-T%"
exit /b %ERRORLEVEL%

:PYTSVint.__bool__
setlocal
    echo set "@PYTSRTEMP_VALUE=%%%1%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
    set "@PYTSR=1"
    if %@PYTSRTEMP_VALUE% EQU 0 set "@PYTSR=0"
    set "@PYTSR-T=bool"
endlocal & set "@PYTSR=%@PYTSR%" & set "@PYTSR-T=%@PYTSR-T%"
exit /b %ERRORLEVEL%

:PYTSVint.__add__
set /a "@PYTSR=%1 + %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__sub__
set /a "@PYTSR=%1 - %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__mul__
echo set "@PYTSR-T=%%%2-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
if %@PYTSR-T%*==str* (call :PYTSVstr.__mul__ %2 %1 & exit /b %ERRORLEVEL%)

set /a "@PYTSR=%1 * %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__truediv__
set /a "@PYTSR=%1 / %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__mod__
set /a "@PYTSR=%1 %% %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__lshift__
set /a "@PYTSR=%1 << %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__rshift__
set /a "@PYTSR=%1 >> %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__or__
set /a "@PYTSR=%1 | %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__and__
set /a "@PYTSR=%1 & %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__xor__
set /a "@PYTSR=%1 ^ %2"
echo set "@PYTSR-T=%%%1-T%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%
