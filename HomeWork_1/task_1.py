import subprocess
import ipaddress

YOUTUBE = '64.233.162.93'
YANDEX = '5.255.255.77'
GOOGLE = '173.194.73.138'
NOT_EXISTS = '132.4.55.11'


def host_ping(ip):
    for i in ip:
        p = subprocess.Popen(['ping', str(ipaddress.ip_address(i))],
                             stdout=subprocess.PIPE)
        res = (p.stdout.read()).decode('cp866')
        if 'данных:\r\nОтвет' in res.split(' '):
            print(f" Узел {i} доступен")
        else:
            print(f" Узел {i} недоступен")
    return 'Работа программы завершена'


if __name__ == '__main__':
    arg = [YOUTUBE, YANDEX, GOOGLE, NOT_EXISTS]
    try:
        host_ping(arg)
    except Exception as e:
        print(e)
