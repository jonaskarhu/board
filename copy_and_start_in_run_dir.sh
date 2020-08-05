#!/bin/bash

LOG="/etc/init.d/autostart_board.log"
DISPLAY="XAUTHORITY=/home/pi/.Xauthority DISPLAY=:0.0"

sudo echo "Copy board to /run/board and start from there" | tee -a $LOG

while [ ! -d /run ]; do
    sudo echo "/run not created yet" | tee -a $LOG
    sleep 2
done

sudo mkdir -p /run/board 2>&1 | tee -a $LOG
sudo chown pi /run/board 2>&1 | tee -a $LOG
cp -r /home/pi/board/* /run/board/ 2>&1 | tee -a $LOG
sudo chown -R pi /run/board 2>&1 | tee -a $LOG

while ! pgrep lxpanel; do
    sudo echo "DISPLAY not set ..." | tee -a $LOG
    sleep 2
done
sleep 5

eval "$DISPLAY" sudo xset s off 2>&1 | tee -a $LOG
eval "$DISPLAY" sudo xset -dpms 2>&1 | tee -a $LOG
eval "$DISPLAY" sudo xset s noblank 2>&1 | tee -a $LOG

eval "$DISPLAY" /run/board/board_gui.py 2>&1 | tee -a $LOG

exit 0
