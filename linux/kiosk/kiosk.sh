#!/bin/bash
xset s noblank
xset s off
xset -dpms

DISPLAY=:0 xrandr --output HDMI-2 --same-as HDMI-1 &

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/$USER/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/$USER/.config/chromium/Default/Preferences


/usr/bin/chromium-browser --noerrdialogs --disable-infobars --app="http://localhost/screen.html" --user-data-dir=$(mktemp -d) --enable-features=OverlayScrollbar --disable-pinch --kiosk &

while true; do
#   xdotool keydown ctrl+Tab; xdotool keyup ctrl+Tab;
  sleep 10
done