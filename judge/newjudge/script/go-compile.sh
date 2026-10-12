cp /opt/newjudge/include/nc_structure.go nc_structure.go
cp /opt/newjudge/include/nc_tools_v2.go nc_tools.go

#兼容之前的代码
sed -i 's/"nc_tools"//g' main.go
sed -i 's/nc_tools.//g' main.go

if [ -f "solution.go" ]; then
	#兼容之前的代码
	sed -i 's/import . "nc_tools"//g' solution.go
fi
go build -o a