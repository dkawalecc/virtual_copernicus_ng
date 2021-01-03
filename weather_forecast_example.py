from VirtualCopernicusNG import TkCircuit

# Initialize the virtual circuit

configuration = {
    "name": "CopernicusNG Weather Forecast",
    "sheet": "sheet_forecast.png",
    "width": 343,
    "height": 267,
    "servos": [
        {"x": 170, "y": 150, "length": 90, "name": "Servo 1", "pin": 17, "min_angle": -90, "max_angle": 90}
    ],
    "buttons": [
        {"x": 295, "y": 200, "name": "Button 1", "pin": 11},
        {"x": 295, "y": 170, "name": "Button 2", "pin": 12},
    ]
}

circuit = TkCircuit(configuration)

@circuit.run
def main():
    # Now just write the code you would use on a real Raspberry Pi

    from time import sleep
    from gpiozero import AngularServo

    servo1 = AngularServo(17, min_angle=-90, max_angle=90)

    servo1.angle = -90

    while True:
        for x in range(-90, 90):
            servo1.angle = x
            sleep(0.1)
