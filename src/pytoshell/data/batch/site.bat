:: The basic library included all routines that needs by pytoshell

:PYTSVint.__add__
set /a "@PYTSR=%1 + %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__sub__
set /a "@PYTSR=%1 - %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__mul__
set /a "@PYTSR=%1 * %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__truediv__
set /a "@PYTSR=%1 / %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__mod__
set /a "@PYTSR=%1 % %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__lshift__
set /a "@PYTSR=%1 << %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__rshift__
set /a "@PYTSR=%1 >> %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__or__
set /a "@PYTSR=%1 | %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__and__
set /a "@PYTSR=%1 & %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%

:PYTSVint.__xor__
set /a "@PYTSR=%1 ^ %2"
echo set "@PYTSR-T=%%%1-T%%%" > __PYTSTEMP_EXEC.BAT & call __PYTSTEMP_EXEC.BAT
exit /b %ERRORLEVEL%
