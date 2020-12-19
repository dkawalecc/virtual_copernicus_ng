# MCP3002

from VirtualCopernicusNG import TkCircuit

# initialize the circuit inside the

configuration = {
    "name": "CopernicusNG Sheet",
    "sheet": "sheet_thermostat.png",
    "width": 311,
    "height": 454,
    "leds": [
        # {"x": 112, "y": 70, "name": "LED 1", "pin": 23},
        # {"x": 71, "y": 141, "name": "LED 2", "pin": 22}
    ],
    "buttons": [
        # {"x": 242, "y": 146, "name": "Button 1", "pin": 11},
        # {"x": 200, "y": 217, "name": "Button 2", "pin": 12},
    ],
    "buzzers": [
        # {"x": 277, "y": 9, "name": "Buzzer", "pin": 16, "frequency": 440},
    ],
    "mcp3002s": [
        {"x": 100, "y": 160, "name": "ADC 1", "clock_pin": 11, "mosi_pin": 10, "miso_pin": 9, "select_pin": 8},
    ],
    "servos": [
        {"x": 154, "y": 148, "length": 90, "name": "Servo", "pin": 17}
    ]
}

circuit = TkCircuit(configuration)

@circuit.run
def main():
    from gpiozero import MCP3002, AngularServo
    from time import sleep

    pot = MCP3002(1, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)

    servo = AngularServo(17, min_angle=0, max_angle=180)
    servo.angle = 0

    while True:
        print("pot value = ", pot.value)
        # print("pot voltage = ", pot.voltage)
        # print("raw voltage= ", pot.raw_value)
        servo.angle = 159 * pot.value
        sleep(0.1)
