import struct
import cachetools.func

def make_header_and_question(name, req_id, flags_and_below=b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'):
    request = bytearray()
    request += struct.pack('!H', req_id) + flags_and_below
    request+=make_question(name)
    return request

@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)  #кеширование с учётом времени жизни
def make_question(name):
    request = bytearray()
    for part in name.split('.'):
        request += struct.pack('!B', len(part.encode()))
        request += part.encode()
    request += struct.pack('!B2H', 0, 1, 1)
    return request

def make_answer(name, req_id, ip):
    answer = make_header_and_question(name, req_id, b'\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00')
    answer+=make_part_of_answer(name, ip)
    return answer

@cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60) #кеширование с учётом времени жизни
def make_part_of_answer(name, ip):
    answer=bytearray()
    ip_data = struct.pack('!4B', *[int(part) for part in ip.split('.')])
    for word in name.split('.'):
        answer += struct.pack('!B', len(word.encode()))
        answer += word.encode()
    answer += struct.pack('!B2HIH', 0, 1, 1, 60, len(ip_data)) + ip_data
    return answer