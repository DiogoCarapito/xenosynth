# xenosynth

[![Github Actions Workflow](https://github.com/DiogoCarapito/xenosynth/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/xenosynth/actions/workflows/main.yaml)

raspberry pi based digital synth to explore xentonal tones and scales

Python version: 3.11

## raspberry pi setup

### enable GPIO, I2C, SPI

```bash
sudo raspi-config
```

### update and upgrade

```bash
sudo apt update
sudo apt upgrade
```

### install git python and python-venv

```bash
sudo apt install git
```

### git clone

```bash
git clone https://github.com/DiogoCarapito/xenosynth.git && cd xenosynth
```

### set crontab

```bash
chmod +x xenosynth/update_and_run.sh
```

```bash
sudo crontab -e
```

```nano
@reboot /usr/bin/python3 xenosynth/main.py
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

### activate and create venv

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### prepare dependencies

```bash
sudo apt update
sudo apt install -y python3-dev python3-pip build-essential
sudo apt install -y portaudio19-dev libportaudio2 libportaudiocpp0
```

### run make all

```bash
make all

### run

```bash
python main.py
```
