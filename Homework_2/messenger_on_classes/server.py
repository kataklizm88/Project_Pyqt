from socket import *
import argparse
import select
import pickle
import dis


class Descriptor:

    def __init__(self, port=None):
        self.port = port if port else 8888

    def __get__(self, instance, instance_type):
        return self.port

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("Значение не может быть меньше 0 ")
        else:
            self.port = value


class ServerVerifer(type):
    def __init__(self, clsname, bases, clsdict):
        for key, value in clsdict.items():
            if key == 'port':
                continue
            check = dis.get_instructions(value)
            for i in check:
                if i.argval in [
                    'SOCK_DGRAM',
                    'SOCK_RAW', 'SOCK_RDM',
                    'SOCK_SEQPACKET'
                ]:
                    raise ValueError('Вы должны работать по протоколу TCP ')
        type.__init__(self, clsname, bases, clsdict)


class Server(metaclass=ServerVerifer):
    port = Descriptor()         # Добавлен дескриптор

    def __init__(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.group = {'1111': []}

    def create_parser(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('addr', nargs='?', default='localhost')
        self.parser.add_argument('port', nargs='?')
        self.namespace = self.parser.parse_args()
        return self.namespace

    def connect(self):
        self.x = self.create_parser()
        self.s.bind((self.x.addr, self.port))           # Проверка дескриптором
        self.s.listen(5)
        self.s.settimeout(0.2)
        print('Соединение установлено')

    def read_requests(self, r_clients, all_clients):
        self.responses = {}
        self.r_clients = r_clients
        self.all_clients = all_clients
        for sock in self.r_clients:
            try:
                self.data = pickle.loads(sock.recv(1024))
                self.responses[sock] = self.data

            except:
                print('Клиент 1 {} {} отключился'.format(sock.fileno(),
                      sock.getpeername()))
                self.all_clients.remove(sock)

        return self.responses

    def write_responses(self, requests, w_clients, all_clients):
        self.requests = requests
        self.w_clients = w_clients
        self.all_clients = all_clients
        for sock in self.w_clients:
            if sock in self.requests:
                # Если надо отправить всем
                if self.requests[sock]['action'] == 'send_all':
                    try:
                        self.m = self.requests[sock]['message']
                        self.n = self.requests[sock]['user']
                        self.resp = f'Новое Сообщение от {self.n}: {self.m}'
                        self.resp = pickle.dumps(self.resp)
                        for i in self.all_clients:
                            i.send(self.resp)
                    except:
                        print('Клиент 2 {} {} отключился'.format(sock.fileno(),
                              sock.getpeername()))
                        sock.close()
                        self.all_clients.remove(sock)
                # Если надо отправить группе
                elif self.requests[sock]['action'] == 'send_group':
                    # Если группа существует
                    if self.requests[sock]['group'] in self.group:
                        self.gr_numb = self.requests[sock]['group']
                        self.group_members = self.group[self.gr_numb]
                        try:
                            self.resp = self.requests[sock]['message']
                            if len(self.group_members) > 0:
                                # Отправляем всем ее участникам
                                for member in self.group_members:
                                    member.send(pickle.dumps(self.resp))
                            else:
                                sock.send(pickle.dumps('В группе никого нет'))
                        except:
                            print('Клиент 3  {} {} отключился'.format(sock.fileno(),
                                  sock.getpeername()))
                            sock.close()
                            self.all_clients.remove(sock)
                    else:
                        print('Такой группы не существует')
                        sock.close()
                        self.all_clients.remove(sock)
                # Если надо вступить в группу
                elif self.requests[sock]['action'] == 'enter a group':
                    try:
                        # Если группа уже существует,то вступаем
                        if self.requests[sock]['group'] in self.group:
                            self.gr_numb = self.requests[sock]['group']
                            self.group_members = self.group[self.gr_numb]
                            self.group_members.append(sock)
                            self.sock.send(pickle.dumps(f'Вы вступили\
                            в группу {self.gr_numb}'))
                        else:  # Если группы нет - создаем
                            self.gr_numb = self.requests[sock]['group']
                            self.group[self.gr_numb] = sock
                            sock.send(pickle.dumps(f'Вы первые в\
                            группе {self.gr_numb}'))
                    except:
                        print('Клиент  {} {} отключился'.format(sock.fileno(),
                              sock.getpeername()))
                        sock.close()
                        self.all_clients.remove(sock)

    def main(self):
        self.clients = []
        self.connect()
        while True:
            try:
                self.client, self.addr = self.s.accept()
            except OSError as e:
                pass
            else:

                print("Получен запрос на соединение от %s" % str(self.addr))
                self.clients.append(self.client)
            finally:
                self.wait = 10
                self.r = []
                self.w = []
                try:
                    self.r, self.w, self.e = select.select(
                        self.clients,
                        self.clients,
                        [],
                        self.wait
                        )
                except:
                    pass
                self.requests = self.read_requests(self.r, self.clients)
                if self.requests:
                    self.write_responses(self.requests, self.w, self.clients)


if __name__ == '__main__':
    try:
        first_server = Server()
        first_server.main()
    except Exception as e:
        print('Ошибка: ', e)
