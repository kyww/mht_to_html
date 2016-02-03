#!/usr/bin/python

import sys
import os
import base64

class MHTException(Exception):             

    def __init__(self, value):
        self.value = value

    def __str__(self): 
        return  repr(self.value)

def NotEmptyLine(line):

    if not line or line == '\r' or line == '\n' or line == '\r\n':
        return False

    return True

class MHTReader:

    def __init__(self):
        self.path = None
        self.file = None
        self.first_part = None
        self.boundary = None

    def Open(self, path):
        self.path = path
        self.file = open(path, 'r')
        self.first_part = True

    def __ReadHead(self):

        line = self.file.readline()

        while NotEmptyLine(line):
            if 'boundary=' in line:
                self.boundary = line.split('"')[1]

            line = self.file.readline()
        
        if not self.boundary:
            raise MHTException("boundary not defined.")

    def __ReadPart(self):

        header = {}

        line = self.file.readline()

        while NotEmptyLine(line):

            if self.boundary in line:
                line = self.file.readline()
                continue

            kv_tuple = line.split(':')
            if len(kv_tuple) >= 2:
                header[kv_tuple[0]] = ':'.join(kv_tuple[1:]).replace('\r', '').replace('\n', '')

            line = self.file.readline()

        if not header:
            return None

        print repr(header)

        body_lines = []
    
        while line and self.boundary not in line:

            body_lines.append(line)
            line = self.file.readline()

        body = ''.join(body_lines)

        return (header, body)


    def Read(self):

        if self.first_part == None:
            raise MHTException("file not open.")
        elif self.first_part == True:
            self.__ReadHead()
            self.first_part = False

        return self.__ReadPart()


def SaveToFile(directory, header, body):

    path = 'index.html'
    transfer_encoding = None

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if 'Content-Location' in header and header['Content-Location']:
        path = header['Content-Location']

    if 'Content-Transfer-Encoding' in header and header['Content-Transfer-Encoding']:
        transfer_encoding = header['Content-Transfer-Encoding']

    data = body

    if transfer_encoding == 'base64':
        data = base64.b64decode(body)

    save_path = '{0}/{1}'.format(directory, path)

    save_file = open(save_path, 'wb')
    save_file.write(data)
    save_file.close()

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "Usage:"
        print "  {0} <mht_file> <output_dir>".format(sys.argv[0])
        print "Eg:"
        print "  {0} a.mht a_file".format(sys.argv[0])
        print "  When output done, open a_file/index.html."
        sys.exit(0)

    reader = MHTReader()
    reader.Open(sys.argv[1])

    part = reader.Read()
    while part:
        SaveToFile(sys.argv[2], part[0], part[1])
        part = reader.Read()


