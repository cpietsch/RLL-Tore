# RLL-Tore


## Installation of Hotspot on the Raspberry Pi Bullseye

```bash
sudo apt-get install hostapd dnsmasq
```

```bash
sudo cp linux/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp linux/wlan0 /etc/network/interfaces.d/wlan0
cat linux/hostapd >> /etc/default/hostapd
cat linux/dnsmasq.conf >> /etc/dnsmasq.conf
cat linux/dhcpcd.conf >> /etc/dhcpcd.conf
```

```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
```

```bash
sudo reboot
```

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```

```bash
sudo nano /etc/rc.local
```

Add the following line before `exit 0`:

```bash
iptables-restore < /etc/iptables.ipv4.nat
```

```bash
sudo reboot
```

```bash
sudo apt-get install git
git clone
```

```bash



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
