# RLL-Tore


## Installation of Hotspot on the Raspberry Pi Bullseye

```bash
sudo apt-get install hostapd dnsmasq
sudo cp linux/hotspot/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp linux/hotspot/wlan0 /etc/network/interfaces.d/wlan0
cat linux/hotspot/hostapd >> /etc/default/hostapd
cat linux/hotspot/dnsmasq.conf >> /etc/dnsmasq.conf
cat linux/hotspot/dhcpcd.conf >> /etc/dhcpcd.conf
```

```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo reboot
```


## Installation of the Pimoroni Automation HAT

You will have to enable the I2C bus:

```bash
sudo raspi-config nonint do_i2c 0
sudo reboot
```

```bash
git clone https://github.com/pimoroni/automation-hat
cd automation-hat
./install.sh
```


## Installation of the server
    
```bash
source ~/.virtualenvs/pimoroni/bin/activate
git clone https://github.com/cpietsch/RLL-Tore
cd RLL-Tore
pip install -r server/requirements.txt
```
