"""
home remotes for pico bots

TODO:
 1 -> PTZ apis??
 2 -> Client Reset code
 3 -> More actions (line follow, etc.)
"""
import asyncio
import json
import logging
import psutil
import sys
import websocket
from typing import Any, Dict, Mapping, Optional
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.proto.common import Vector3
from viam.rpc.server import Server


def disk_usage_by_partition():
    """
    A simple function to get the disk usage of our
    :return:
    """
    ret = {}
    for d in psutil.disk_partitions():
        if 'snap' not in d.mountpoint:
            usage = psutil.disk_usage(d.mountpoint)
            ret[d.mountpoint] = {'total': usage.total, 'used': usage.used, 'free': usage.free}
    return ret


class LinuxSensor(Sensor):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    async def get_readings(self, **kwargs) -> Mapping[str, Any]:
        ret = {}
        usage = disk_usage_by_partition()
        ret['disk_usage'] = usage
        return ret

    async def do_command(self, command: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass


class PicoSensor(Sensor):
    def __init__(self, name: str, ws: Any) -> None:
        self._ws = ws
        super().__init__(name)

    async def get_readings(self, **kwargs) -> Mapping[str, Any]:
        data = json.dumps({'op': self.name})
        print(f'writing data: {data}')
        self._ws.send(json.dumps({'op': self.name}))
        resp = json.loads(self._ws.recv())
        print(f'resp: {resp}')
        if resp['status'] == 'ok' and resp['data'] != {}:
            return resp['data']
        else:
            return {'status': resp['status'], 'msg': resp['msg']}

    async def do_command(self, command: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass


class PicoBase(Base):
    def __init__(self, name: str, ws: Any) -> None:
        self._ws = ws
        self._is_moving = False
        super().__init__(name)

    async def move_straight(self, distance: int, velocity: float, extra: Optional[Dict[str, Any]] = None, **kwargs):
        raise NotImplementedError('move_straight not implemented yet')

    async def spin(self, angle: float, velocity: float, extra: Optional[Dict[str, Any]] = None, **kwargs):
        raise NotImplementedError('spin not implemented yet')

    async def set_power(self, linear: Vector3, angular: Vector3, extra: Optional[Dict[str, Any]] = None, **kwargs):
        if linear.y != 0:
            self._ws.send(json.dumps({'action': 'forward'})) if linear.y == 1 else self._ws.send(json.dumps({'action': 'backward'}))
            self._is_moving = True
        elif angular.z != 0:
            self._ws.send(json.dumps({'action': 'left'})) if angular.z == 1 else self._ws.send(json.dumps({'action': 'right'}))
            self._is_moving = True
        else:
            self._ws.send(json.dumps({'action': 'stop'}))
            self._is_moving = False

    async def set_velocity(self, linear: Vector3, angular: Vector3, extra: Optional[Dict[str, Any]] = None, **kwargs):
        raise NotImplementedError('spin not implemented yet')

    async def stop(self, extra: Optional[Dict[str, Any]] = None, **kwargs):
        self._ws.send(json.dumps({'action': 'stop'}))
        self._is_moving = False

    async def is_moving(self) -> bool:
        return self._is_moving

    async def do_command(self, command: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        pass


async def main(wsc):
    srv = Server([
        PicoSensor('sonar', wsc),
        PicoSensor('grayscale', wsc),
        PicoSensor('speed', wsc),
        PicoSensor('cputemp', wsc),
        LinuxSensor('hardware'),
        PicoBase('pico-base', wsc)
    ])
    await srv.serve(host='localhost', port=9090, log_level=logging.DEBUG)


if __name__ == '__main__':
    ws_client = None
    try:
        websocket.enableTrace(False)
        ws_client = websocket.WebSocket()
        ws_client.connect('ws://10.0.0.53:8765')
        print(ws_client.recv())
        asyncio.run(main(ws_client))
    except Exception as e:
        print(f'Error occurred: {e}')
        sys.exit(1)
    finally:
        if ws_client:
            ws_client.close()
