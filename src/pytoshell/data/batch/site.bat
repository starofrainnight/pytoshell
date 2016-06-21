:: The basic library included all routines that needs by pytoshell

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
