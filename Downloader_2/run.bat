@echo off
set timestart="%time%"
py download.py
set timestop="%time%"
echo %timestart% - %timestop% >time.txt
exit