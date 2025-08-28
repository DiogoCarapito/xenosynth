# xenosynth

[![Github Actions Workflow](https://github.com/DiogoCarapito/xenosynth/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/xenosynth/actions/workflows/main.yaml)

raspberry pi based digital synth to explore xentonal tones and scales

Python version: 3.11

## raspberry pi setup

### update and upgrade

```bash
sudo apt update
sudo apt upgrade
```

### enable GPIO, I2C, SPI

```bash
sudo raspi-config
```

### install git python and python-venv

```bash
sudo apt install git
```

### git clone

```bash
git clone https://github.com/DiogoCarapito/xenosynth.git
```

### install python 3.12 (optional)

```bash
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
libffi-dev libbz2-dev liblzma-dev tk-dev wget

cd /usr/src
sudo wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
sudo tar xvf Python-3.12.0.tgz
cd Python-3.12.0
sudo ./configure --enable-optimizations
sudo make -j$(nproc)
sudo make altinstall
```

### setup a starting bash script wiht RGB led indicator, update and run

```bash
touch update_and_run.sh
nano update_and_run.sh
```

```sh
#!/bin/bash

# GPIO pins
RED=22
GREEN=23
BLUE=24

# Set up GPIO (using sysfs)
echo "$RED" > /sys/class/gpio/export
echo "$GREEN" > /sys/class/gpio/export
echo "$BLUE" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio$RED/direction
echo "out" > /sys/class/gpio/gpio$GREEN/direction
echo "out" > /sys/class/gpio/gpio$BLUE/direction

# Helper functions
led_off() {
    echo 0 > /sys/class/gpio/gpio$RED/value
    echo 0 > /sys/class/gpio/gpio$GREEN/value
    echo 0 > /sys/class/gpio/gpio$BLUE/value
}

led_yellow() {
    echo 1 > /sys/class/gpio/gpio$RED/value
    echo 1 > /sys/class/gpio/gpio$GREEN/value
    echo 0 > /sys/class/gpio/gpio$BLUE/value
}

led_green() {
    echo 0 > /sys/class/gpio/gpio$RED/value
    echo 1 > /sys/class/gpio/gpio$GREEN/value
    echo 0 > /sys/class/gpio/gpio$BLUE/value
}

# --- Start blinking yellow while updating ---
led_yellow

# Navigate to your repo
cd xenosynth || exit

# Pull latest code
git pull

# Optional: make or build commands
make all

# Switch LED to green
led_green

# Activate Python virtual environment
source .venv/bin/activate

# Run Python script
python3 main.py

# When done, turn off LED
led_off
```

```bash
chmod +x update_and_run.sh
```

### activate and create venv

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### run

```bash
python main.py
```
