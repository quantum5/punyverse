@echo off
cd %~dp0assets\textures
call :convert earth.jpg earth_medium.jpg 2048x1024
call :convert earth.jpg earth_small.jpg 1024x512
call :convert moon.jpg moon_medium.jpg 2048x1024
call :convert moon.jpg moon_small.jpg 1024x512
call :convert mars.jpg mars_medium.jpg 2048x1024
call :convert mars.jpg mars_small.jpg 1024x512
call :convert jupiter.jpg jupiter_medium.jpg 2048x1024
call :convert jupiter.jpg jupiter_small.jpg 1024x512
call :convert saturn.jpg saturn_medium.jpg 2048x1024
call :convert saturn.jpg saturn_small.jpg 1024x512
goto :eof

:convert
echo Converting %1 to %2, size %3...
if not exist %2 gm convert %1 -resize %3 %2
