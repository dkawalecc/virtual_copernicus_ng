import os

from .base import TkDevice, SingletonMeta
from .base import PreciseMockTriggerPin, PreciseMockFactory, PreciseMockChargingPin, MockMCP3002
from gpiozero import Device
from gpiozero.pins.mock import MockPWMPin
from PIL import ImageEnhance, Image, ImageTk
from sounddevice import play, stop
import numpy
import scipy.signal
from tkinter import Tk, Frame, Label, Button, Scale, HORIZONTAL, VERTICAL, CENTER, Canvas
from threading import Thread, Timer
from sys import path, exit
from pathlib import Path
from math import sqrt, cos, sin
import random
from time import sleep

class TkCircuit(metaclass=SingletonMeta):
    def __init__(self, setup):
        # Device.pin_factory = PreciseMockFactory(pin_class=MockPWMPin)
        Device.pin_factory = PreciseMockFactory()

        path.insert(0, str(Path(__file__).parent.absolute()))

        default_setup = {
            "name": "Virtual GPIO",
            "width": 500, "height": 500,
            "leds":[], "buzzers":[], "buttons":[],
            "servos":[], "mcp3002s": []
        }

        default_setup.update(setup)
        setup = default_setup

        self._root = Tk()
        self._root.title(setup["name"])
        self._root.geometry("%dx%d" % (setup["width"], setup["height"]))
        self._root.resizable(False, False)
        self._root["background"] = "white"

        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)

        background_label = Canvas(self._root, width=setup["width"], height=setup["height"])
        if "sheet" in setup.keys():
            current_folder = str(Path(__file__).parent.absolute())
            file_path = current_folder + "/images_copernicus/" + setup['sheet']
            background_image = ImageTk.PhotoImage(file=file_path)
            background_label.create_image(0,0,image = background_image, anchor="nw")
            #dirty hack
            self._bk_image = background_image
        background_label.pack()
        self._bg_canvas = background_label

        self._outputs = []
        self._outputs += [self.add_device(TkLED, parameters) for parameters in setup["leds"]]
        self._outputs += [self.add_device(TkBuzzer, parameters) for parameters in setup["buzzers"]]

        for parameters in setup["servos"]:
            parameters.update({"bg_canvas": self._bg_canvas})
            self._outputs += [self.add_device(TkServo, parameters)]

        for parameters in setup["buttons"]:
            self.add_device(TkButton, parameters)

        for parameters in setup["mcp3002s"]:
            self.add_device(TkMCP3002, parameters)


    def add_device(self, device_class, parameters):
        return device_class(self._root, **parameters)

    def run(self, function):
        thread = Thread(target=function, daemon=True)
        thread.start()

        self._root.after(10, self._update_outputs)
        self._root.mainloop()

    def _update_outputs(self):
        for output in self._outputs:
            output.update()

        self._root.after(10, self._update_outputs)

    def update_lcds(self, pins, text):
        for lcds in self._lcds:
            lcds.update_text(pins, text)

    def _on_closing(self):
        exit()

class TkBuzzer(TkDevice):
    SAMPLE_RATE = 44000
    PEAK = 0.1
    DUTY_CICLE = 0.5

    def __init__(self, root, x, y, name, pin, frequency=440):
        super().__init__(root, x, y, name)

        self._pin = Device.pin_factory.pin(pin)
        self._previous_state = None

        self._set_image_for_state("buzzer_on.png", "on", (50, 33))
        self._set_image_for_state("buzzer_off.png", "off", (50, 33))
        self._create_main_widget(Label, "off")

        if frequency != None:
            n_samples = self.SAMPLE_RATE
            t = numpy.linspace(0, 1, int(500 * 440/frequency), endpoint=False)
            wave = scipy.signal.square(2 * numpy.pi * 5 * t, duty=self.DUTY_CICLE)
            wave = numpy.resize(wave, (n_samples,))
            self._sample_wave = (self.PEAK / 2 * wave.astype(numpy.int16))
        else:
            self._sample_wave = numpy.empty(0)

    def update(self):
        if self._previous_state != self._pin.state:
            if self._pin.state == True:
                self._change_widget_image("on")
                if len(self._sample_wave) > 0:
                    play(self._sample_wave, self.SAMPLE_RATE, loop=True)
            else:
                self._change_widget_image("off")
                if len(self._sample_wave) > 0:
                    stop()

            self._previous_state = self._pin.state

            self._redraw()


class TkLED(TkDevice):
    on_image = None

    def __init__(self, root, x, y, name, pin):
        super().__init__(root, x, y, name)

        self._pin = Device.pin_factory.pin(pin)

        self._previous_state = None

        TkLED.on_image = self._set_image_for_state("led_on.png", "on")
        self._set_image_for_state("led_off.png", "off")

        self._create_main_widget(Label, "off")

        self._widget.config(borderwidth=0, highlightthickness=0, background="white")

    def update(self):
        #print("LED updated!")
        if self._previous_state != self._pin.state:
            if isinstance(self._pin.state, float):
                converter = ImageEnhance.Color(TkLED.on_image)
                desaturated_image = converter.enhance(self._pin.state)
                self._change_widget_image(desaturated_image)
            elif self._pin.state == True:
                self._change_widget_image("on")
            else:
                self._change_widget_image("off")

            self._previous_state = self._pin.state

            self._redraw()


class TkButton(TkDevice):
    def __init__(self, root, x, y, name, pin):
        super().__init__(root, x, y, name)

        self._pin = Device.pin_factory.pin(pin)

        self._set_image_for_state("button_pressed.png", "on", (15, 15))
        self._set_image_for_state("button_released.png", "off", (15, 15))
        self._create_main_widget(Button, "off")
        self._widget.config(borderwidth=0,highlightthickness = 0,background="white")
        self._widget.bind("<ButtonPress>", self._on_press)
        self._widget.bind("<ButtonRelease>", self._on_release)

    def _on_press(self, botao):
        self._change_widget_image("on")

        thread = Thread(target=self._change_pin, daemon=True, args=(True,))
        thread.start()

    def _on_release(self, botao):
        self._change_widget_image("off")

        thread = Thread(target=self._change_pin, daemon=True, args=(False,))
        thread.start()

    def _change_pin(self, is_press):
        if is_press:
            self._pin.drive_low()
        else:
            self._pin.drive_high()

class TkServo(TkDevice):
    on_image = None

    def __init__(self, root, x, y, name, pin, bg_canvas, length, min_angle=-90, max_angle=90):
        super().__init__(root, x, y, name)

        self.pin = pin
        self._pin = Device.pin_factory.pin(pin, pin_class=MockPWMPin)
        self._bg_canvas = bg_canvas
        self._length = length
        self._min_angle = min_angle
        self._max_angle = max_angle

    def update(self):

        angle = ((self._pin.state-0.05) / 0.05) * (self._max_angle - self._min_angle) + self._min_angle
        angle = angle/180 * 3.14

        self._bg_canvas.delete(f"servo:{self.pin}")
        self._bg_canvas.create_line(self._x, self._y, cos(angle)*self._length*-1 + self._x, sin(angle)*self._length*-1 + self._y, tags=f"servo:{self.pin}", fill="red", width=3)

        self._redraw()

class TkMCP3002(TkDevice):
    def __init__(self, root, x, y, name, clock_pin, mosi_pin, miso_pin, select_pin, max_voltage=3.3):
        super().__init__(root, x, y, name)

        self.mock = MockMCP3002(max_voltage=max_voltage, clock_pin=clock_pin, mosi_pin=mosi_pin, miso_pin=miso_pin, select_pin=select_pin)
        self.mock.channels[1] = 0
        self.max_voltage = max_voltage

        self._create_main_widget(Scale, None)
        self._widget.config(from_=0, to=100, orient=HORIZONTAL, showvalue=False, command=self.update)

    def update(self, event):
        value = self._widget.get()
        self.mock.channels[1] = (value / 100) * self.max_voltage
