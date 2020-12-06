from gpiozero.pins.mock import MockFactory, MockTriggerPin, MockPWMPin, MockChargingPin, MockSPIDevice
from PIL import ImageTk, Image
from time import sleep, perf_counter
from os import path

class TkDevice():
    _images = {}

    def __init__(self, root, x, y, name):
        self._root = root
        self._name = name
        self._x = x
        self._y = y
        self._widget = None
        self._image_states = {}

    def _redraw(self):
        self._root.update()

    def _create_main_widget(self, widget_class, initial_state=None):
        self._widget = widget_class(self._root)
        self._widget.place(x=self._x, y=self._y)

        if initial_state != None:
            self._change_widget_image(initial_state)

        return self._widget

    def _set_image_for_state(self, image_file_name, state, dimensions=None):
        if image_file_name in TkDevice._images:
            image = TkDevice._images[image_file_name]
        else:
            current_folder = path.dirname(__file__)
            file_path = path.join(current_folder, "images_copernicus/" + image_file_name)

            image = Image.open(file_path)
            if dimensions != None:
                image = image.resize(dimensions, Image.ANTIALIAS)

            TkDevice._images[image_file_name] = image

        self._image_states[state] = image

        return image

    def _change_widget_image(self, image_or_state):
        if self._widget != None:
            if isinstance(image_or_state, str):
                state = image_or_state
                image = self._image_states[state]
            else:
                image = image_or_state

            self._photo_image = ImageTk.PhotoImage(image)
            self._widget.configure(image=self._photo_image)

            self._redraw()


class PreciseMockTriggerPin(MockTriggerPin, MockPWMPin):
    def _echo(self):
        sleep(0.001)
        self.echo_pin.drive_high()

        # sleep(), time() and monotonic() dont have enough precision!
        init_time = perf_counter()
        while True:
            if perf_counter() - init_time >= self.echo_time:
                break

        self.echo_pin.drive_low()


class PreciseMockFactory(MockFactory):
    @staticmethod
    def ticks():
        # time() and monotonic() dont have enough precision!
        return perf_counter()


class PreciseMockChargingPin(MockChargingPin, MockPWMPin):

    def _charge(self):
        init_time = perf_counter()
        while True:
            if perf_counter() - init_time >= self.charge_time:
                break

        try:
            self.drive_high()
        except AssertionError:
            pass
    pass


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# ====

class MockMCP3xxx(MockSPIDevice):
    def __init__(
            self, clock_pin, mosi_pin, miso_pin, select_pin=None,
            channels=8, bits=10):
        super(MockMCP3xxx, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin)
        self.vref = 3.3
        self.channels = [0.0] * channels
        self.channel_bits = 3
        self.bits = bits
        self.state = 'idle'

    def on_start(self):
        super(MockMCP3xxx, self).on_start()
        self.state = 'idle'

    def on_bit(self):
        if self.state == 'idle':
            if self.rx_buf[-1]:
                self.state = 'mode'
                self.rx_buf = []
        elif self.state == 'mode':
            if self.rx_buf[-1]:
                self.state = 'single'
            else:
                self.state = 'diff'
            self.rx_buf = []
        elif self.state in ('single', 'diff'):
            if len(self.rx_buf) == self.channel_bits:
                self.on_result(self.state == 'diff', self.rx_word())
                self.state = 'result'
        elif self.state == 'result':
            if not self.tx_buf:
                self.state = 'idle'
                self.rx_buf = []
        else:
            assert False

    def on_result(self, differential, channel):
        if differential:
            pos_channel = channel
            neg_channel = pos_channel ^ 1
            result = self.channels[pos_channel] - self.channels[neg_channel]
            result = clamp(result, 0, self.vref)
        else:
            result = clamp(self.channels[channel], 0, self.vref)
        result = scale(result, self.vref, self.bits)
        self.tx_word(result, self.bits + 2)

class MockMCP3xx2(MockMCP3xxx):
    def __init__(
            self, clock_pin, mosi_pin, miso_pin, select_pin=None,
            bits=10):
        super(MockMCP3xx2, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=2, bits=bits)
        self.channel_bits = 1


class MockMCP3002(MockMCP3xx2):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3002, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, bits=10)


def clamp(v, min_value, max_value):
    return min(max_value, max(min_value, v))

def scale(v, ref, bits):
    v /= ref
    vmin = -(2 ** bits)
    vmax = -vmin - 1
    vrange = vmax - vmin
    return int(((v + 1) / 2.0) * vrange + vmin)
