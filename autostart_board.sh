#!/bin/bash

### BEGIN INIT INFO
# Provides:          board
# Required-Start:
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Python GUI
# Description:       Shows Västrafik Bus info for a specific stop,
#                    as well as wather from SMHI and current temp.
#                    Needs internet connection.
### END INIT INFO

# Author: Jonas Karhu <jonas.m.karhu@gmail.com>

start() {
    LOG="/etc/init.d/autostart_board.log"
    sudo echo "Starting board" | tee $LOG
    sudo /home/pi/board/copy_and_start_in_run_dir.sh &
}

stop() {
    echo "Stopping board"
}

case "$1" in
    start)
       start
       ;;
    stop)
       stop
       ;;
    restart)
       stop
       start
       ;;
    *)
       echo "Usage: $0 {start|stop|restart}"
esac

exit 0
