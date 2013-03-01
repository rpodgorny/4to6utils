setlocal

rd /s /q build
rd /s /q dist

set PYTHONPATH=../pylib;../libsh

del *.pyc

python setup.py py2exe
;rem python setup.py bdist_egg

del *.pyc

rd /s /q build
del dist\w9xpopen.exe

copy dist\*.exe .\

rd /s /q dist