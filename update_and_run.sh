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
cd xenosynth/ || exit

# Pull latest code
git pull

# Optional: make or build commands
make all

# Switch LED to green
led_green

# Run Python script
python3 main.py

# When done, turn off LED
led_off