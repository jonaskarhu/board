#!/bin/bash

sudo cp /home/pi/board/autostart_board.sh /etc/init.d/
pushd /etc/rc5.d >/dev/null
sudo ln -sf ../init.d/autostart_board.sh /etc/rc5.d/S99autostart_board.sh
popd >/dev/null
echo "Done."

exit 0
