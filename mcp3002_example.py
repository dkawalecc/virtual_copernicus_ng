# MCP3002

from VirtualCopernicusNG import TkCircuit

configuration = {
    "name": "CopernicusNG Sheet",
    "sheet": "sheet_thermostat.png",
    "width": 311,
    "height": 454,
    "leds": [],
    "buttons": [],
    "buzzers": [],
    "mcp3002s": [
        {"x": 34, "y": 160, "name": "ADC 1", "clock_pin": 11, "mosi_pin": 10, "miso_pin": 9, "select_pin": 8},
        {"x": 172, "y": 230, "name": "ADC 2", "clock_pin": 15, "mosi_pin": 14, "miso_pin": 13, "select_pin": 12}
    ],
    "servos": [
        {"x": 154, "y": 148, "length": 90, "name": "Servo 1", "pin": 17, "min_angle": 0, "max_angle": 159},
        {"x": 156, "y": 318, "length": 45, "name": "Servo 2", "pin": 18, "min_angle": -60, "max_angle": 240}
    ]
}

circuit = TkCircuit(configuration)

@circuit.run
def main():
    from gpiozero import MCP3002, AngularServo
    from time import sleep

    pot1 = MCP3002(1, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)
    pot2 = MCP3002(1, clock_pin=15, mosi_pin=14, miso_pin=13, select_pin=12)

    servo1 = AngularServo(17, min_angle=0, max_angle=159)
    servo1.angle = 0
    servo2 = AngularServo(18, min_angle=-60, max_angle=240)
    servo2.angle = -60

    while True:
        print(f"pot1: value = {pot1.value:0.2f}\tvoltage = {pot1.voltage:0.2f}\traw value = {pot1.raw_value:0.2f}")
        servo1.angle = 159 * pot1.value

        print(f"pot2: value = {pot2.value:0.2f}\tvoltage = {pot2.voltage:0.2f}\traw value = {pot2.raw_value:0.2f}")
        servo2.angle = -60 + 300 * pot2.value

        sleep(0.1)
