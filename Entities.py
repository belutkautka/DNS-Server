class Question:
    def __init__(self, name, type, _class):
        self.NAME = '.'.join(list(word.decode('utf-8') for word in name))
        self.TYPE = type
        self.СLASS = _class


class Answer:
    def __init__(self, name, type, _class, ttl, length, rdata):
        self.NAME = ".".join(list(word.decode('utf-8') for word in name))
        self.TYPE = type
        self.CLASS = _class
        self.TTL = ttl
        self.length = length
        self.rdata = rdata
        self.DATA = None
        if self.TYPE == 1:# DNS_TYPE_A
            self.data = '.'.join(list(str(part) for part in bytearray(self.rdata)))
        if self.TYPE == 2:# DNS_TYPE_NS
            self.data = '.'.join(list(part.decode('utf-8') for part in self.rdata[1]))


class Package:
    def __init__(self, headers, questions, answers, authorities, additionals):
        self.header = headers
        self.questions = questions
        self.answers = answers
        self.authorities = authorities
        self.additional = additionals