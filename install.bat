robocopy  %~dp0  %TMP%\damask_gui\  /E
%TMP:~0,2%
cd %TMP%\damask_gui

python setup.py install
python setup.py clean --all
pause