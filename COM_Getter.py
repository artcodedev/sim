


from  Print import Print
import sys
import glob
import serial
import json



class COM_Getter:
    
    
    def __init__(self) -> None:
        pass
    
    
    def _send_command(self, com):
        
        try:
            self.ser.write(f'{com}\r'.encode())
            return self.ser.readall()
        
        except Exception as e:
            Print.error("[+] Error in get _send_command")
            Print.error(e)
            return False
    
    
    def save_json(self, js):
        try:
            
            Print.log("[+] Save file ports.json")
            with open("ports.json", "w+", encoding="utf-8") as f: f.write(json.dumps(js))
            
            return True
        
        except Exception as e:
            Print.error('[+] Error in method save_json')
            Print.error(e)
            return False
    
    
    def _getOpenPort(self):
        
        try:
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            
            if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                ports = glob.glob('/dev/tty[A-Za-z]*')
            
            if sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            
            result = []
            
            for port in ports:
                try:
                    
                    if port != 'COM1':
                        
                        s = serial.Serial(port)
                        s.close()
                        result.append(port)
                        
                except (OSError, serial.SerialException): pass
            
            return result
                
        except Exception as e:
            Print.error("[+] Error in search method")
            Print.error(e)
            return False
            
            
    def __search_com(self):
        
        try:
            
            Print.log("[+] Get open ports")
            coms = self._getOpenPort()
            
            if coms is not False:
                
                Print.log(f"PORT lenght: {len(coms)}")
                if len(coms) != 0:
                    
                    js = []
                    
                    for i in coms:
                        
                        try:
                            
                            Print.log(f"[+] Connect to port {i}")
                            self.ser = serial.Serial(i, 9600, timeout=1, bytesize=8, parity='N', stopbits=1)
                        
                            Print.log('[+] AT+CNUM')
                            res = self._send_command("AT+CNUM")
                            
                            Print.log('[+] Decode result AT+CNUM')
                            number = res.decode("utf-8").split(',')[1]
                            
                            Print.log("[+] Append to mass")
                            js.append({"port": f'{i}', "number": f'{number.replace('"', "")}'})
                        
                        except Exception as e:
                            Print.error(f"Error in COM {i}")
                            Print.error(e)
                    
                    Print.log("[+] Return result")

                    return True if self.save_json(js) else False
            
            Print.log("[+] Return result")
            return False        
                        
        except Exception as e:
            Print.error("[+] Error in search method")
            Print.error(e)
            return False
    
        
    def getAllPort(self):
        
        if self.__search_com():
            Print.ok("[+] File with all ports was created")
            return True
        else:
            Print.error('[+] File not was created')
            return False


if __name__ == "__main__":
    
    COM_Getter().getAllPort()
    