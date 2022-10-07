from machine import Pin, UART
import time

##############################################
## Please change to any values
NODE =
BW =
SF =
CHANNEL =
PANID =
OWNID =
DSTID =
RSSI =
RCVID =
##############################################

class LoRa():
    def __init__(self, rPinNum, uId):
        self.rPin = Pin(rPinNum, Pin.OUT)
        
        self.rPin.value(0)
        time.sleep(1.0)
        self.rPin.value(1)
        
        self.uPin = UART(uId, 115200)
    
    def reset(self):
        self.rPin.value(0)
        time.sleep(0.1)
        self.rPin.value(1)
    
    def readline(self):
        bRes = self.uPin.readline()
        try:
            cRes = bRes.decode('utf-8')
        except:
            cRes = ''
        return cRes
    
    def write(self, msg):
        self.uPin.write(msg.encode('utf-8'))
        
    def setCmd(self, cmd):
        while True:
            self.write(cmd)
            time.sleep(0.5)
            print(cmd)
            res = self.readline()
            print(res)
            if 'OK' in res:
                return True
    
    def setProcessor(self):
        self.reset()
        time.sleep(2.0)
        self.write('config\r\n')
        time.sleep(0.5)
        self.reset()
        res = self.readline()
        while True:
            time.sleep(1.0)
            res = self.readline()
            print(res)
            if 'Mode' in res:
                time.sleep(1.0)
                ok = self.setCmd('2\r\n')
                print(ok)
                if ok:
                    return True
            
    def setMode(self):
        self.setProcessor()
        
        time.sleep(1.0)
        
        self.setCmd('a %d\r\n' % NODE)
        self.setCmd('bw %d\r\n' % BW)
        self.setCmd('sf %d\r\n' % SF)
        self.setCmd('d %d\r\n' % CHANNEL)
        self.setCmd('A %d\r\n' % 1)
        self.setCmd('l %d\r\n' % 1)
        self.setCmd('e %d\r\n' % PANID)
        self.setCmd('f %d\r\n' % OWNID)
        self.setCmd('g %d\r\n' % DSTID)
        self.setCmd('p %d\r\n' % RSSI)
        self.setCmd('o %d\r\n' % RCVID)
        self.setCmd('q 2\r\n')
        self.setCmd('w\r\n')
        
        self.reset()
        print('Lora module set to new mode')
        time.sleep(1.0)
        
    def parse(self, res):
        hex2i = lambda x: int(x, 16) if int(x, 16) <= 0x7fff else ~ (0xffff - int(x, 16)) + 1
        fmt = '4s4s4s' + str(len(res) - 14) + 's'
        arrRes = struct.unpack(fmt, res)
        rssi = hex2i(arrRes[0])
        panId = hex2i(arrRes[1])
        srcId = hex2i(arrRes[2])
        msg = arrRes[3].decode('utf-8')
        return rssi, panId, srcId, msg
        
    
    def send(self, msg):
        time.sleep(0.01)
        msg = msg + '\r\n'
        while True:
            self.write(msg)
            time.sleep(1.0)
            self.uPin.flush()
            if 'OK' in self.readline():
                print('OK')
                break
        
    def receive(self):
        res = self.uPin.readline()
        if res != None:
            if len(res) >= 14:
                return self.parse(res)
        
