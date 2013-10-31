@echo off
cd %~dp0assets\textures
call :convert mercury.jpg mercury_small.jpg 1024x512
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
call :convert moons\io.jpg moons\io_small.jpg 1024x512
call :convert moons\europa.jpg moons\europa_small.jpg 1024x512
call :convert moons\ganymede.jpg moons\ganymede_small.jpg 1024x512
call :convert moons\callisto.jpg moons\callisto_small.jpg 1024x512
call :convert moons\titan.jpg moons\titan_small.jpg 1024x512
call :convert moons\rhea.jpg moons\rhea_small.jpg 1024x512
call :convert moons\iapetus.jpg moons\iapetus_small.jpg 1024x512
call :convert moons\dione.jpg moons\dione_small.jpg 1024x512
call :convert moons\tethys.jpg moons\tethys_small.jpg 1024x512
call :convert moons\enceladus.jpg moons\enceladus_small.jpg 1024x512
call :convert moons\mimas.jpg moons\mimas_small.jpg 1024x512
goto :eof

:convert
echo Converting %1 to %2, size %3...
if not exist %2 gm convert %1 -resize %3 %2
