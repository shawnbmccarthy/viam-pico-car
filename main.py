from ws_socket import WSServer
import pico_4wd as car


def init(ssid, pw):
    ws_server = WSServer(wf=ssid, pw=pw)
    ws_server.start()
    return ws_server


def main(ws_server):
    while True:
        ws_server.loop()


if __name__ == '__main__':
    print('(II) starting car')
    try:
        main(init(ssid='SSID_HERE', pw='SSID_PW_HERE'))
    except Exception as e:
        print(f'(EE) {e}')
    finally:
        print('(II) shutting down')
        car.move('stop')
