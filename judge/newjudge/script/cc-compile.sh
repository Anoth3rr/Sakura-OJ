#!/bin/sh
first_line=`head -n 10 main.cc`

if echo "$first_line" | grep -q "#include \"tools.h\""
then
 	clang++  -std=c++17 -O2 -Werror=return-type -include-pch /opt/newjudge/include/tools.h.gch -I/opt/newjudge/include/ main.cc
else
 	clang++  -std=c++17 -O2 -Werror=return-type -include-pch /opt/newjudge/include/nc_tools.h.gch -I/opt/newjudge/include/ main.cc
fi