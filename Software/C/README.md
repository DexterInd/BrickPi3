# BrickPi3 C Library

## Requirements

- A Raspberry Pi with the BrickPi3 attached
- `g++` installed (`sudo apt install g++`)
- SPI enabled on the Raspberry Pi (`sudo raspi-config` → Interface Options → SPI → Enable)

## Files

| File | Description |
|------|-------------|
| `BrickPi3.h` | BrickPi3 C header |
| `BrickPi3.cpp` | BrickPi3 C library |
| `Examples/info.c` | Read and print BrickPi3 hardware info |
| `Examples/motors.c` | Run motors |
| `Examples/sensors_ev3.c` | Read EV3 sensors |
| `Examples/sensors_nxt.c` | Read NXT sensors |

## Compiling

Navigate to the `Examples` folder first, since the examples include `BrickPi3.cpp` via a relative path:

```bash
cd Examples
```

Then compile the example you want:

```bash
g++ -o info info.c
g++ -o motors motors.c
g++ -o sensors_ev3 sensors_ev3.c
g++ -o sensors_nxt sensors_nxt.c
```

## Running

```bash
./info
./motors
./sensors_ev3
./sensors_nxt
```
