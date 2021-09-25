import subprocess
import ipaddress


def check_data():
    try:
        ip = input('Enter ip-address ')
        ip = ipaddress.ip_address(ip)
    except ValueError:
        print('Вы ввели не ip-адрес !')
        return None
    try:
        oktet = int(input('Enter a last oktet '))
    except ValueError:
        print('Вы ввели не число')
        return None
    finally:
        if oktet > 255:
            print('Максимальный размер октета = 250 !')
            return None
        elif oktet < int(str(ip).split('.')[3]):
            print(" Введенный октет не должен быть меньше,\
             чем октет ip-адреса")
            return None
        else:
            return [str(ip), oktet]


def host_range_ping(data):
    if data is not None:
        ip, oktet = data
        last = int(ip.split('.')[3])
        for i in range(last, (oktet + 1)):
            ip = ip.split('.')
            ip.pop()
            ip.append(str(i))
            ip = ('.').join(ip)
            p = subprocess.Popen(['ping', ip], stdout=subprocess.PIPE)
            res = (p.stdout.read()).decode('cp866')
            if 'данных:\r\nОтвет' in res.split(' '):
                print(f" Узел {ip} доступен")
            else:
                print(f" Узел {ip} недоступен")
        return 'Работа программы завершена'
    else:
        print("Работа программы завершилась некорректно")


if __name__ == '__main__':
    data = check_data()
    host_range_ping(data)
