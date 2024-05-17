#!/bin/bash
xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/$USER/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/$USER/.config/chromium/Default/Preferences


/usr/bin/chromium-browser --noerrdialogs --disable-infobars --app="http://localhost:8000/screen" --user-data-dir=$(mktemp -d) --enable-features=OverlayScrollbar  --disable-pinch --kiosk &

while true; do
   #xdotool keydown ctrl+Next; xdotool keyup ctrl+Next;
   sleep 10
done