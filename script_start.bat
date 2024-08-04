@echo off
cd /d "%~dp0"
start cmd /k "python Server_menu.py"
start cmd /k "python Sender_process.py"
start cmd /k "python Receiver_rdt.py"