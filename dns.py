import concurrent.futures
import os
import socket
from Result_Converter import make_answer
from Result_Converter import make_header_and_question
import cachetools.func
from Parser import parse_package

class DNSServer:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

    def start(self):
        self.server.bind(self.addr)
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as client: #параллельное использование
            while True:
                data, addr = self.server.recvfrom(4096)
                client.submit(self.client, data, addr)

    def client(self, data, addr):
        package = parse_package(data) #парсинг пакета
        question = package.questions[0]
        request_id = package.header['ID']
        if 'multiply' in question.NAME:
            answer = make_answer(question.NAME, request_id, multiply(question.NAME))
            self.server.sendto(answer, addr)
            return
        answer = find_ip(question.NAME, request_id)
        self.server.sendto(answer, addr)
        return

@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60) #кеширование с учётом времени жизни
def multiply(name): #multiply
    result = 1
    for number in name[:name.find('.multiply')].split('.'):
        result = (result * int(number)) % 256
    return '127.0.0.' + str(result)


def find_ip(name, request_id):
        ip = '198.41.0.4' #коренной сервер
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ips = list()
        while True:
            request = make_header_and_question(name, request_id)
            my_socket.sendto(request, (ip, 53))

            response, addr = my_socket.recvfrom(4096)
            package = parse_package(response)
            for answer in package.answers:
                if answer.TYPE == 1:
                    return response

            empty_additional = True
            for additional in package.additional:
                if additional.TYPE == 1:
                    ips.append(additional.data)
                    empty_additional = False

            if empty_additional:
                for authority in package.authorities:
                    if authority.TYPE == 2:
                        ips.append(authority.data)

            if len(ips) == 0:
                break
            ip = ips.pop(0)


def main():
    dns_server = DNSServer('127.0.0.1', 53)
    dns_server.start()

if __name__ == '__main__':
    main()
