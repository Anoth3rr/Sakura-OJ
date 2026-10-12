if [ -f "solution.ts" ]; then
	cp /opt/newjudge/include/nc_structure.ts nc_structure.ts
	tsc main.ts solution.ts nc_structure.ts
else
	tsc main.ts
fi