# Viam Pico Car

**todo: create better tutorial & code**

## Requirements
Sunfounder pico car (see reference below)

## Installation

### Setup Pico
1. flash with micro-python
1. add sunfounder libraries according to documentation
1. add ws_socket.py & main.py to pico
1. start process & get ip

### Custom Remotes
1. create virtual environment
1. copy remotes.py & remotes.sh to viam directory
1. update remotes.sh with paths
1. update remotes.py with IP address of pico car
1. configure viam to use remote and manage process
1. start viam 

# References

## Documents
1. [Pico Car](https://docs.sunfounder.com/projects/pico-4wd-car/en/latest/)
1. [schmatic](https://raw.githubusercontent.com/sunfounder/sf-pdf/master/schematic/pico-rdp.pdf)
1. [micropython](https://docs.micropython.org/en/latest/)
1. [Getting Started with Raspberry Pi Pico C/C++](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf)
1. [Getting Started with MicroPythong on Pi Pico](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf)

## Code Repositories
1. [Sun Founder Pico 4wd Car](https://github.com/sunfounder/pico_4wd_car): contains various code for the pico car
1. [esp8266 uart wsserver](https://github.com/sunfounder/esp8266-uart-wsserver)
1. [wyze](https://github.com/nblavoie/wyzecam-api)