#!/bin/sh
if [ -f "Solution.java" ]; then
        file_name=`/opt/judge-client/get_class_name Solution.java`;
        if [ "$file_name" != "Solution" ]; then
        	mv Solution.java $file_name.java;
        fi
fi
javac -encoding utf8 -cp .:/opt/newjudge/include/*:/opt/newjudge/include Main.java