import socket
import socketserver
import time
from threading import Thread
import re

# constants
TIMEOUT = 1
TIMEOUT_RECHARGING = 5
PORT = 3999
HOST = "localhost"
END_SEQ = "\a\b"

# server messages
SERVER_MOVE = "102 MOVE" + END_SEQ
SERVER_TURN_LEFT = "103 TURN LEFT" + END_SEQ
SERVER_TURN_RIGHT = "104 TURN RIGHT" + END_SEQ
SERVER_PICK_UP = "105 GET MESSAGE" + END_SEQ
SERVER_LOGOUT = "106 LOGOUT" + END_SEQ
SERVER_KEY_REQUEST = "107 KEY REQUEST" + END_SEQ
SERVER_OK = "200 OK" + END_SEQ
SERVER_LOGIN_FAILED = "300 LOGIN FAILED" + END_SEQ
SERVER_SYNTAX_ERROR = "301 SYNTAX ERROR" + END_SEQ
SERVER_LOGIC_ERROR = "302 LOGIC ERROR" + END_SEQ
SERVER_KEY_OUT_OF_RANGE_ERROR = "303 KEY OUT OF RANGE" + END_SEQ

# authentication keys
server_keys = [23019, 32037, 18789, 16443, 18189]
client_keys = [32037, 29295, 13603, 29533, 21952]

def name_hash(name):
    """hash client's name"""
    sum = 0
    for i in range(0, len(name)):
        sum = sum + ord(name[i])
    return ((sum * 1000) % 65536)

def hash(hashed_name, server_key):
    """get hash for LOGIN confirmation"""
    return ((hashed_name + server_key) % 65536)

def dehash(get_hashed, client_key):
    """dehash clients confirmation code"""
    return ((get_hashed - client_key) % 65536)

def extract_end_seq(socket):
    """extracts END_SEQ from msg (packet)"""
    i = 0
    while (i+1 <= len(socket)):
        if socket[i] == '\a' and socket[i+1] == '\b':
            break
        i = i + 1
        if i > len(socket):
            break
    return socket[:i]

def check_coor(msg):
    """controls if msg has more spaces than expecter or coors are floating points"""
    if (msg.count(" ") > 2) or ('.' in str(msg)):
        return False
    return True

# https://stackoverflow.com/questions/42751063/python-filter-positive-and-negative-integers-from-string
def extract_coordinates(msg):
    """extracts coordinatines from msg"""
    result = [int(d) for d in re.findall(r'-?\d+', msg)]
    return result[0], result[1]

class Server_TCP(Thread):
    """class for thread -> server communication with client"""
    def __init__(self, conn):
        """constructor"""
        # thread constructor
        Thread.__init__(self)
        self.connection = conn 
        self.packet = ""
        self.running = True
        self.client_name = ""
        self.client_name_ascii = ""
        self.key_id = -1
        self.server_hash = -1
        self.client_hash = -1
    
    def send(self, packet):
        """sends msg to client"""
        # send() may not send all the data you give it
        # sendall() will not return until all data has been sent
        self.connection.sendall(packet.encode())
    
    def recieve(self, byte_cnt):
        """recieve msg from client -> save to build message"""
        byte = self.connection.recv(byte_cnt)
        self.packet += byte.decode("ascii")
        if "RECHARGING\a\b" in self.packet:
            self.recharge(byte_cnt)
    
    def recieve_clear(self, byte_cnt):
        """recieve msg from client -> save to new message"""
        byte = self.connection.recv(byte_cnt)
        self.packet = byte.decode("ascii")
        if "RECHARGING\a\b" in self.packet:
            self.recharge(byte_cnt)
    
    def end(self):
        """ends connection with client"""
        self.running = False
        self.connection.close()
        
    def recharge(self, byte_cnt):
        """takes care of recharging"""
        self.connection.settimeout(TIMEOUT_RECHARGING)
        self.recieve_clear(12)
        if "FULL POWER\a\b" in self.packet:
            self.recieve_clear(byte_cnt)
            self.connection.settimeout(TIMEOUT)
        else:
            self.send(SERVER_LOGIC_ERROR)
            self.end()

    def around_right(self):
        """turn right"""
        self.send(SERVER_TURN_RIGHT)
        self.recieve_clear(12)
        if len(ascii(self.packet)) < 12:
            self.recieve(12)
        if (check_coor(self.packet) == False):
            self.send(SERVER_SYNTAX_ERROR)
            self.end()
    
    def around_left(self):
        """turns left"""
        self.send(SERVER_TURN_LEFT)
        self.recieve_clear(12)
        if len(ascii(self.packet)) < 12:
            self.recieve(12)
        if (check_coor(self.packet) == False):
            self.send(SERVER_SYNTAX_ERROR)
            self.end()
    
    def move(self):
        """move robot"""
        self.send(SERVER_MOVE)
        self.recieve_clear(12)
        if len(ascii(self.packet)) < 12:
            self.recieve(12)
        if (check_coor(self.packet) == False):
            self.send(SERVER_SYNTAX_ERROR)
            self.end()
    
    
    def moving(self):
        """move with robots"""
        last_cor_X = 666
        last_cor_Y = 666
        cor_X = 666
        cor_Y = 666
        is_start = True
        self.around_right()
        last_cor_X, last_cor_Y = extract_coordinates(self.packet)
        while True:
            if is_start == False:
                last_cor_X, last_cor_Y = cor_X, cor_Y
            else:
                is_start = False
            self.move()
            cor_X, cor_Y = extract_coordinates(self.packet)
            if cor_X == 0 and cor_Y == 0:
                break
            dir_X = cor_X - last_cor_X
            dir_Y = cor_Y - last_cor_Y
            # block found
            if cor_X == last_cor_X and cor_Y == last_cor_Y:
                self.around_right()
                self.move()
                last_cor_X, last_cor_Y = extract_coordinates(self.packet)
                self.around_left()
                self.move()
                cor_X, cor_Y = extract_coordinates(self.packet)
                if cor_X == 0 and cor_Y == 0:
                    break
                dir_X = cor_X - last_cor_X
                dir_Y = cor_Y - last_cor_Y
            # get right direction towards [0,0]
            if cor_X > 0:
                if dir_X == 1:
                    self.around_left()
                    self.around_left()
                elif dir_X == -1:
                    continue
                elif dir_Y == 1:
                    self.around_left()
                elif dir_Y == -1:
                    self.around_right()
            elif cor_X < 0:
                if dir_X == 1:
                    continue
                elif dir_X == -1:
                    self.around_left()
                    self.around_left()
                elif dir_Y == 1:
                    self.around_right()
                elif dir_Y == -1:    
                    self.around_left()
            # x == 0
            else:
                if cor_Y > 0:
                    if dir_X == 1:
                        self.around_right()
                    elif dir_X == -1:
                        self.around_left()
                    elif dir_Y == 1:
                        self.around_left()
                        self.around_left()
                    elif dir_Y == -1:
                        continue
                elif cor_Y < 0:
                    if dir_X == 1:
                        self.around_left()
                    elif dir_X == -1:
                        self.around_right()
                    elif dir_Y == 1:
                        continue
                    elif dir_Y == -1:
                        self.around_left()
                        self.around_left()
        
        # check secret msg        
        self.send(SERVER_PICK_UP)
        self.recieve_clear(100)
        if "\a\b" not in self.packet or len(self.packet) > 100:
            # segmentation of packets
            if len(self.packet) <= 100:
                self.recieve(100-len(self.packet))
                if "\a\b" not in self.packet:
                    self.send(SERVER_SYNTAX_ERROR)
                    self.end()
            else:
                self.send(SERVER_SYNTAX_ERROR)
                self.end()
        self.send(SERVER_LOGOUT)    
        
    def check_client_hash(self):
        """compare client hash with server hash"""
        get_dehash = dehash(self.client_hash, client_keys[self.key_id])
        
        if get_dehash == self.client_name_ascii:
            self.send(SERVER_OK)
        else:
            self.send(SERVER_LOGIN_FAILED)
            self.end()

    def get_client_hash(self):
        """recieve hash from client"""
        self.recieve_clear(10)
        if len(ascii(self.packet)) < 7:
            self.recieve(10)
        
        self.client_hash = extract_end_seq(self.packet)
        
        # client hash isn't correct
        if (self.client_hash.isnumeric()) == False or len(self.client_hash) > 5:
            self.send(SERVER_SYNTAX_ERROR)
            self.end()
        
        self.client_hash = (int)(self.client_hash)
        
        if self.client_hash < 0:
            self.send(SERVER_LOGIN_FAILED)
            self.end()

    def get_hash(self):
        """recieve key_id from client, count hash and send hash to client"""
        self.recieve_clear(1)
        if (self.packet).isnumeric() == False:
            byte = self.connection.recv(12)
            self.packet += byte.decode("ascii")
            if "RECHARGING\a\b" in self.packet:
                self.recharge(1)
            else:
                self.send(SERVER_SYNTAX_ERROR)
                self.end()
        
        # client key
        self.key_id = int(self.packet)
        if self.key_id < 0 or self.key_id > 4:
            self.send(SERVER_KEY_OUT_OF_RANGE_ERROR)
            self.end()
        
        # get hash from client name
        self.client_name_ascii = name_hash(self.client_name)
        self.server_hash = hash(self.client_name_ascii, server_keys[self.key_id])
        
        # SERVER CONFIRM with hash
        self.send(f"{self.server_hash}{END_SEQ}")
        
    def check_name(self):
        """recieve name of client and send key request"""
        self.client_name = extract_end_seq(self.packet)
        # longer client name then expected
        if len(self.client_name) > 18:
            self.send(SERVER_SYNTAX_ERROR)
            self.end()
        self.send(SERVER_KEY_REQUEST)
    
    # thread.init -> call run()
    def run(self):
        """thread run"""
        self.connection.settimeout(TIMEOUT)
        i = 0
        try:
            # recieve packet/msg from client
            while self.running:
                self.recieve(1)
                
                if "\a\b" in self.packet and i == 0:
                    self.check_name()
                    i += 1
                    
                if "\a\b" in self.packet and i == 1:
                    self.get_hash()
                    i += 1
                    
                if "\a\b" in self.packet and i == 2:
                    self.get_client_hash()
                    i += 1
                
                if "\a\b" in self.packet and i == 3:
                    self.check_client_hash()
                    i += 1
                
                if "\a\b" in self.packet and i == 4:
                    self.moving()
                    i += 1
                
                if "\a\b" not in self.packet and len(self.packet) > 18:
                    self.send(SERVER_SYNTAX_ERROR)
                    self.end()
        
        # if client doesn't communicate -> end connection
        except socketserver.socket.timeout:
            self.end()

        # close connection after communication
        finally:
            self.connection.close()

if __name__ == "__main__":
    # create a TCP/IP socket
    # AF_INET - refers to the address-family ipv4
    # SOCK_STREAM - connection-oriented TCP protocol.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # https://stackoverflow.com/questions/72319941/what-do-socket-sol-socket-and-socket-so-reuseaddr-in-python
    # used for setting protocol level, socket type, 
    # !enable address reuse (this case)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # bind the socket to a public host, and a well-known port
    # specifies that the socket is reachable by any address the machine happens to have
    server_socket.bind((HOST, PORT))

    print("\n", f"-"*15, f"Server runs!", f"-"*15, "\n")
    
    while True:
        # tells the socket library to queue up 1 connect request before refusing outside connections
        server_socket.listen(1)
        # accept connections from outside
        conn, ip = server_socket.accept()
        # new thread -> server commun with client here
        new_client = Server_TCP(conn)
        # start the thread’s activity
        # arranges for the object’s run() method to be invoked in a separate thread of control
        new_client.start()