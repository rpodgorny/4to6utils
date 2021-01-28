set p=c:\4to6utils

Echo.%PATH% | findstr /I /C:"%p%">nul && (
	echo %p% already in path
) || (
	echo adding to %p% to path
	setx PATH "%PATH%;%p%" -m
	set "PATH=%PATH%;%p%"
)
