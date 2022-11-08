from machine import UART, ADC
import pico_4wd as car
import json


class WSServer(object):
    """
    simple websocket server for pico car demonstration
    """
    def __init__(self, wf, pw, name='simple-car'):
        self.wf = wf
        self.pw = pw
        self.uart = UART(1, 115200, timeout=100, timeout_char=10)
        self._ret = {
            'car': name,
            'status': None,
            'msg': None,
            'data': {}
        }

    def _set(self, cmd, val=None):
        val = '' if not val else val
        self._cmd('SET', cmd, val)
        while True:
            res = self.read(block=True)
            if res.startswith('[ERROR]'):
                raise ValueError(res)
            if res.startswith('[OK]'):
                res = res[4:]
                res = res.strip(' ')
                break
        return res

    def _get(self, cmd):
        self._cmd('GET', cmd)
        return self.read()

    def _cmd(self, mode, cmd, val=None):
        val = '' if not val else val
        self.write(f'{mode}+{cmd}{val}')

    def read(self, block=False):
        buf = ''
        while 1:
            buf = self.uart.readline()
            if buf is None:
                if block:
                    continue
                else:
                    return None
            if buf[0] == 0xff:
                buf = buf[1:]
            buf = buf.decode().replace('\r\n', '')
            if buf.startswith('[DEBUG] '):
                buf.replace('[DEBUG] ', '[ESP866]')
                print(f'[D]{buf}')
            else:
                return buf

    def write(self, value):
        self.uart.write(f'{value}\n'.encode())

    def send_data(self, status, msg, data=None):
        self._ret['status'] = status
        self._ret['msg'] = msg
        self._ret['data'] = {} if not data else data
        self._cmd('WS', json.dumps(self._ret))

    def start(self):
        self._set('SSID', self.wf)
        self._set('PSK', self.pw)
        self._set('MODE', 1)
        self._set('PORT', 8765)
        print('connecting...')
        try:
            ip = self._set('START')
            print(f'ws started on ws://{ip}:8765')
        except ValueError as e:
            print(f'wifi error: {e}')

    def on_receive(self, data):
        if 'op' in data:
            op = data['op']
            if op == 'grayscale':
                values = car.get_grayscale_values()
                self.send_data(
                    status='ok',
                    msg='query successful',
                    data={
                        'left': values[0],
                        'middle': values[1],
                        'right': values[2]
                    }
                )
            elif op == 'sonar':
                value = car.sonar.get_distance()
                self.send_data(
                    status='ok',
                    msg='query successful',
                    data={'distance': value}
                )
            elif op == 'speed':
                value = car.speed()
                self.send_data(
                    status='ok',
                    msg='query successful',
                    data={'speed': value}
                )
            elif op == 'cputemp':
                # the temp sensor measures the Vbe voltage of a bipolar diode (pico micro python docs)
                sensor_temp = ADC(4)
                temperature = 27 - (sensor_temp.read_u16() * (3.3/65535))/0.001721
                self.send_data(
                    status='ok',
                    msg='query successful',
                    data={'temp': temperature}
                )
            else:
                self.send_data(status='error', msg=f'invalid op: {op}')
        elif 'action' in data:
            car.move(data['action'], 70)
            self.send_data(status='ok', msg=f'move({data["action"]}) successful')
        else:
            self.send_data(status='error', msg=f'message missing op')

    def loop(self):
        recv = self.read()
        if recv is None:
            return
        elif recv.startswith('[CONNECTED]'):
            print(f'message: {recv}')
            self.send_data(status='ok', msg='connected', data={'recv': recv})
        elif recv.startswith('[DISCONNECTED]'):
            print(f'message: {recv}')
        else:
            try:
                data = json.loads(recv)
                if isinstance(data, str):
                    data = json.loads(data)
                self.on_receive(data)
            except ValueError as e:
                print(f'[ERROR]: problem loading data - {e}\n')
