from socket import *
import argparse
import select
import pickle

# Группа 1111 для примера
group = {'1111': []}


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', nargs='?', default='localhost')
    parser.add_argument('port', nargs='?', default=8888)
    return parser


def read_requests(r_clients, all_clients):
    responses = {}
    for sock in r_clients:
        try:
            data = pickle.loads(sock.recv(1024))
            responses[sock] = data
        except:
            print('Клиент 1 {} {} отключился'.format(sock.fileno(),
                  sock.getpeername()))
            all_clients.remove(sock)

    return responses


def write_responses(requests, w_clients, all_clients):
    for sock in w_clients:
        if sock in requests:
            # Если надо отправить всем
            if requests[sock]['action'] == 'send_all':
                try:
                    m = requests[sock]['message']
                    n = requests[sock]['user']
                    resp = f'Новое Сообщение от {n}: {m}'
                    resp = pickle.dumps(resp)
                    for i in all_clients:
                        i.send(resp)
                except:
                    print('Клиент 2 {} {} отключился'.format(sock.fileno(),
                          sock.getpeername()))
                    sock.close()
                    all_clients.remove(sock)
            # Если надо отправить группе
            elif requests[sock]['action'] == 'send_group':
                try:
                    # Если группа существует
                    if requests[sock]['group'] in group:
                        gr_numb = requests[sock]['group']
                        group_members = group[gr_numb]
                        m = requests[sock]['message']
                        n = requests[sock]['user']
                        resp = f'Новое Сообщение от {n}: {m}'
                        resp = pickle.dumps(resp)
                        if len(group_members) > 0:
                            # Отправляем всем ее участникам
                            for member in group_members:
                                member.send(resp)
                        else:
                            sock.send(pickle.dumps('В группе никого нет'))
                    else:
                        sock.send(pickle.dumps('В группе никого нет'))
                except:
                    print('Клиент 3  {} {} отключился'.format(sock.fileno(),
                          sock.getpeername()))
                    sock.close()
                    all_clients.remove(sock)
            # Если надо вступить в группу
            elif requests[sock]['action'] == 'enter a group':
                try:
                    gr_numb = requests[sock]['group']
                    if gr_numb in group:
                        if sock in group[gr_numb]:
                            sock.send(pickle.dumps(f'Вы уже в группе\
                                        № {gr_numb}'))
                        else:
                            # Если группа уже существует,то вступаем
                            group_members = group[gr_numb]
                            group_members.append(sock)
                            sock.send(pickle.dumps(f'Вы вступили в \
                                        группу {gr_numb}'))
                    else:
                        # Если группы нет - создаем
                        group[gr_numb] = []
                        group[gr_numb].append(sock)
                        sock.send(pickle.dumps(f'Создана группа №  {gr_numb}'))
                        print(group)
                except:
                    print('Клиент  {} {} отключился'.format(sock.fileno(),
                          sock.getpeername()))
                    sock.close()
                    all_clients.remove(sock)


def main():
    clients = []
    parser = create_parser()
    namespace = parser.parse_args()
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((namespace.addr, namespace.port))
    s.listen(5)
    s.settimeout(0.2)
    print('Сервер запущен')
    while True:
        try:
            client, addr = s.accept()
        except OSError as e:
            pass
        else:
            print("Получен запрос на соединение от %s" % str(addr))
            clients.append(client)
        finally:
            wait = 10
            r = []
            w = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except:
                pass
            requests = read_requests(r, clients)
            if requests:
                write_responses(requests, w, clients)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)

