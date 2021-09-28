import time
from socket import *
import argparse
import pickle
from threading import Thread


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', nargs='?', default='localhost')
    parser.add_argument('port', nargs='?', default=8888)
    return parser


def true_choise(true_answer, presence):
    while True:
        start = input('Ваш выбор ')
        if start in true_answer:
            if start == 'M':
                message = input('Введите ваше сообщение: ')
                presence['action'] = 'send_all'
                presence['message'] = message
            elif start == 'G':
                group_choise = input('Введите 4-значный номер группы ')
                message = input('Ваше сообщение группе ')
                presence['action'], presence['group'] = 'send_group',
                group_choise
                presence['message'] = message
            elif start == 'EG':
                group_number = input('Введите номер группы ')
                presence['action'], presence['group'] = 'enter a group',
                group_number
            break
        else:
            print('Вы ввели некорректные данные попробуйте еще раз')

    return presence


def send_data(s, data):

    return s.send(pickle.dumps(data))


def get_data(s):
    while True:

        print(pickle.loads(s.recv(1024)))


def main():
    true_answer = ['M', 'G', 'EG']
    presence = {
        "action": 'action',
        "time": time.ctime(time.time()),
        "type": "status",
        "user": 'john',
        'group': None,
        'message': None
    }

    parser = create_parser()
    namespace = parser.parse_args()
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((namespace.addr, namespace.port))
    th = Thread(target=get_data, args=(s,))
    th.daemon = True
    th.start()
    print('Клиент запущен')
    while True:
        print("Выберите что хотите сделать:"
              " M - отправить сообщение всем пользователям;"
              " G - отправить сообщение группе; EG - вступить в группу")
        choise = true_choise(true_answer, presence)
        send_data(s, choise)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Ошибка: ', e)
