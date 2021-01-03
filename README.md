# Virtual Copernicus NG

Pakiet do symulacji fizycznych urządzeń elektronicznych poprzez graficzny interfejs użytkownika.

## Instalacja

```sh
# Opcjonalnie stworzenie wirtualnego środowiska do instalowania pakietów
python -m venv venv
source venv/bin/activate

# Zainstalowanie pakietu Virtual Copernicus NG
pip install git+https://github.com/dkawalecc/virtual_copernicus_ng.git
```

## Zasada użycia

```py
from virtual_copernicus_ng import TkCircuit

# Krok 1: definiujemy wirtualny układ poprzez wskazanie
# jakie znajdują się w nim elementy oraz określeniu ich parametrów.

configuration = {
    "name": "CopernicusNG SmartHouse",
    "sheet": "sheet_smarthouse.png",
    "width": 332,
    "height": 300,
    "leds": [
        {"x": 112, "y": 70, "name": "LED 1", "pin": 21}
    ],
    "buttons": [
        {"x": 242, "y": 146, "name": "Button 1", "pin": 11}
    ]
}

# Krok 2: tworzymy wirtualny układ na podstawie powyższej definicji.
# W ten sposób tworzony jest graficzny interfejs użytkownika
# będący reprezentacją rzeczywistego układu.

circuit = TkCircuit(configuration)

@circuit.run
def main():
    # Krok 3: w tym miejscu piszemy program w identyczny sposób
    # co na rzeczywistej płytce Raspberry PI.

    from gpiozero import LED, Button
    from time import sleep

    led1 = LED(21)

    def handle_button1_press():
        print("button 1 pressed!")
        led1.toggle()

    button1 = Button(11)
    button1.when_pressed = handle_button1_press

    while True:
        sleep(0.1)
```

## Przykłady

Kompletne przykłady można znaleźć w katalogu [`examples`](./examples).

## Dostępne wirtualne elementy

### Dioda LED

**Konfiguracja układu**

```py
configuration = {
    # ...
    "leds": [
        {"x": 112, "y": 70, "name": "LED 1", "pin": 21}
    ],
    # ...
}
```

**Obsługa elementu**

```py
from gpiozero import LED

led1 = LED(21)
led1.toggle()
```

### Przycisk

**Konfiguracja układu**

```py
configuration = {
    # ...
    "buttons": [
        {"x": 242, "y": 146, "name": "Button 1", "pin": 11},
    ],
    # ...
}
```

**Obsługa elementu**

```py
from gpiozero import Button

def handle_button1_press():
    print("button 1 pressed!")

button1 = Button(11)
button1.when_pressed = handle_button1_press
```

### Brzęczyk

**Konfiguracja układu**

```py
configuration = {
    # ...
    "buzzers": [
        {"x": 277, "y": 9, "name": "Buzzer", "pin": 16, "frequency": 440},
    ],
    # ...
}
```

**Obsługa elementu**

```py
from gpiozero import Buzzer

buzzer = Buzzer(16)
buzzer.on()
```

### Servo

**Konfiguracja układu**

```py
configuration = {
    # ...
    "servos": [
        {"x": 170, "y": 150, "length": 90, "name": "Servo 1", "pin": 17, "min_angle": 0, "max_angle": 180}
    ],
    # ...
}
```

**Obsługa elementu**

```py
from gpiozero import AngularServo

servo = AngularServo(17, min_angle=0, max_angle=180)
servo.angle = 90
```

### Przetwornik analogowo cyfrowy (MCP3002)

**Konfiguracja układu**

```py
configuration = {
    # ...
    "mcp3002s": [
        {"x": 34, "y": 160, "name": "ADC 1", "clock_pin": 11, "mosi_pin": 10, "miso_pin": 9, "select_pin": 8, "max_voltage": 5},
    ],
    # ...
}
```

**Obsługa elementu**

```py
from gpiozero import MCP3002

pot = MCP3002(1, max_voltage=5, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)

while True:
    print(f"pot: value = {pot.value:0.2f}\tvoltage = {pot.voltage:0.2f}\traw value = {pot.raw_value:0.2f}")

    sleep(0.1)
```
