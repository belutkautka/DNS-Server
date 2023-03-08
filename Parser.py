from Entities import Question
from Entities import Package
from Entities import Answer

def parse_package(package):
    data = bytearray(package)

    request_id = int.from_bytes(data[:2], byteorder='big')
    flags = data[2:4]
    qdcount = int.from_bytes(data[4:6], byteorder='big')
    ancount = int.from_bytes(data[6:8], byteorder='big')
    nscount = int.from_bytes(data[8:10], byteorder='big')
    arcount = int.from_bytes(data[10:12], byteorder='big')
    header = {
        'ID': request_id,
        'FLAGS': flags,
        'QDCOUNT': qdcount,
        'ANCOUNT': ancount,
        'NSCOUNT': nscount,
        'ARCOUNT': arcount
    }
    index = 12
    questions = list()
    for i in range(qdcount):
        index, q_name = parse_name(data, package, index)
        q_type = int.from_bytes(data[index:index + 2], byteorder="big")
        index += 2
        q_class = int.from_bytes(data[index:index + 2], byteorder="big")
        index += 2
        questions.append(Question(q_name, q_type, q_class))
    answers = list()
    for i in range(ancount):
        index, answer = parse_data(data, package, index)
        answers.append(answer)
    authority = list()
    for i in range(nscount):
        index, answer = parse_data(data, package, index)
        authority.append(answer)
    additional = list()
    for i in range(arcount):
        index, answer = parse_data(data, package, index)
        additional.append(answer)
    return Package(header, questions, answers, authority, additional)

def parse_name(data, package, index):
    name, new_index = [], 0
    while True:
        data_len = data[index]
        index += 1
        if data_len < 64:
            name.append(package[index:index + data_len])
            index += data_len
        else:
            if new_index == 0:
                new_index = index + 1
            index = (data_len % 64) + data[index]
            continue
        if data[index] == 0:
            break
    index += 1
    if new_index == 0:
        new_index = index
    return new_index, name

def parse_data(data, package, index):
    new_index, a_name = parse_name(data, package, index)
    type = int.from_bytes(data[new_index:new_index + 2], byteorder='big')
    new_index += 2
    _class = int.from_bytes(data[new_index:new_index + 2], byteorder='big')
    new_index += 2
    ttl = int.from_bytes(data[new_index:new_index + 4], byteorder='big')
    new_index += 4
    length = int.from_bytes(data[new_index:new_index + 2], byteorder='big')
    new_index += 2
    rdata = data[new_index:new_index + length]
    if type == 2:
        rdata = parse_name(data, package, new_index)
    new_index += length
    return new_index, Answer(a_name, type, _class, ttl, length, rdata)