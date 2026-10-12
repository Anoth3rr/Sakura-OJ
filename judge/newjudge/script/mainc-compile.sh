clang -Werror=return-type -O2 -c solution.c --include=/opt/newjudge/include/nc_ctools.h
if [ $? -ne 0 ]
then
	exit $?
fi

clang++ -std=c++11 -Werror=return-type -O2 -c main.cpp -I/opt/newjudge/include/
if [ $? -ne 0 ]
then
	exit $?
fi

clang++ -O2 solution.o main.o