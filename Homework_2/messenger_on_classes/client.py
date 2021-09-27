from socket import *
import pickle
import argparse
import time
import dis


class ClientVerifer(type):
    def __init__(self, clsname, bases, clsdict):
        """ Проверка на отсутствие сокетов на уровне классов """
        for key, value in clsdict.items():
            if isinstance(value, socket):
                raise ValueError('В атрибутах класса не должно быть сокетов')
            check = dis.get_instructions(value)
            for i in check:
                if i.argval == 'accept' or i.argval == 'listen':
                    raise ValueError(' Таких методов не должно быть в клиенте')
                elif i.argval in [
                    'SOCK_DGRAM',
                    'SOCK_RAW',
                    'SOCK_RDM',
                    'SOCK_SEQPACKET'
                ]:
                    raise ValueError('Вы должны работать по протоколу TCP ')
        type.__init__(self, clsname, bases, clsdict)


class Client(metaclass=ClientVerifer):

    def __init__(self):
        self.s = socket(AF_INET, SOCK_STREAM)

    def create_parser(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('addr', nargs='?', default='localhost')
        self.parser.add_argument('port', nargs='?', default=8888)
        self.namespace = self.parser.parse_args()
        return self.namespace

    def connect(self):
        self.x = self.create_parser()
        self.s.connect((self.x.addr, self.x.port))
        print('Вы подключились к серверу')

    def true_choise(self, true_answer, presence):
        print('enter a choise')
        self.true_answer = true_answer
        self.presence = presence
        while True:
            self.start = input('Ваш выбор ')
            if self.start in self.true_answer:
                if self.start == 'M':
                    self.message = input('Введите ваше сообщение: ')
                    self.presence['action'] = 'send_all'
                    self.presence['message'] = self.message
                elif self.start == 'G':
                    self.group_choise = input('Введите 4-значный\
                    номер группы ')
                    self.message = input('Ваше сообщение группе ')
                    self.presence['action'], presence['group'] = 'send_group',
                    self.group_choise
                    self.presence['message'] = self.message
                elif self.start == 'EG':
                    self.group_number = input('Введите номер группы ')
                    self.presence['action'], presence['group'] = 'enter a group',
                    self.group_number
                break
            else:
                print('Вы ввели некорректные данные попробуйте еще раз')
        return self.presence

    def send_data(self, data):
        self.data = data
        return self.s.send(pickle.dumps(data))

    def get_data(self):
        # while True:
        print(pickle.loads(self.s.recv(1024)))

    def main(self):
        self.true_answer = ['M', 'G', 'EG']
        self.presence = {
            "action": 'action',
            "time": time.ctime(time.time()),
            "type": "status",
            "user": 'john',
            'group': None,
            'message': None
        }
        self.connect()
        while True:
            print("Выберите что хотите сделать:"
                  " M - отправить сообщение всем пользователям;"
                  " G - отправить сообщение группе; EG - вступить в группу")
            self.choise = self.true_choise(self.true_answer, self.presence)
            self.send_data(self.choise)
            self.x = self.get_data()


if __name__ == "__main__":
    try:
        first_client = Client()
        first_client.main()
    except Exception as e:
        print('Ошибка: ', e)
