
from Print import Print
import serial
import time
from smspdudecoder.codecs import UCS2


class SMS:
    
    def __init__(self, COM, port, phone):
        self.phone = phone
        self.ser = serial.Serial(COM, port, timeout=1, bytesize=8, parity='N', stopbits=1)
    
    
    def _send_command(self, com, error=0):
        
        error = error
        
        try:
            self.ser.write(f'{com}\r'.encode())
            return self.ser.readall()
        
        except Exception as e:
            Print.error("[+] Error in get _send_command")
            Print.error(e)
               
    
    def getSMScode(self):
        
        try:
            Print.log("[+] Get SMS code")
            
            res = self._send_command("AT+CMGF=1")
            if res is False: return False

            Print.log("[+] Get all message")
            all_message = self._send_command('AT+CMGL="ALL"')
            
            Print.log("[+] Decode all message")
            all_message_decode = all_message.decode("utf-8")
            
            Print.log(all_message_decode)
            
            Print.log("[+] Find all message")
            if all_message_decode.find("REC UNREAD") == -1:
                Print.warning("[+] No new messages")
                return 0
            
            indices = []
            index = -1
            code_num = []
            
            Print.log("[+] Cound all message")
            while True:
                index = all_message_decode.find("+CMGL", index + 1)
                if index == -1: break
                indices.append(index)
            
            all_message = len(indices) - 1
            Print.log(f'[+] Message length: {all_message}')
            
            for i in range(0, all_message):
                
                Print.log("[+] AT+CMGF=1")
                self._send_command("AT+CMGF=1")
                
                Print.log("[+] AT+CSCS=\"GSM\"")
                self._send_command("AT+CSCS=\"GSM\"")
                
                Print.log("[+] AT+CSMP=17,167,0,0")
                self._send_command("AT+CSMP=17,167,0,0")
                
                Print.log(f"[+] AT+CMGR={all_message}")
                res = self._send_command(f"AT+CMGR={all_message}")
                
                all_message -= 1
                
                Print.log("[+] Decode result")
                res = res.decode("utf-8")
                
                Print.log("[+] Split result")
                res = res.split(",")
                
                if len(res) == 1 or len(res) == 0: return False
                
                number = res[1].replace('"', "")
                
                Print.log("[+] Compare numbers")
                if number != self.phone: continue
                
                Print.log("[+] Get message")
                time_mess = res[4].split("+")
                
                Print.log("[+] Converting message")
                message = UCS2.decode(time_mess[1].split("\r\n")[1])
                
                Print.log("[+] Search code in message")
                if "код" in message.lower():
                    
                    for i in message:
                        if len(code_num) == 5: break
                        if i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']: code_num.append(i)
                    
                    break
            
            Print.log("[+] Delete all message")
            res = self._send_command('AT+CMGDA="DEL ALL"')
            
            if 'ok' in res.decode("utf-8").lower():
                Print.ok("[+] Meesage was deleted")
            else:
                Print.warning("[+] Something went wrong when deleting all messages")
            
            self.ser.close()
            
            return 0 if len(code_num) == 0 else ''.join(code_num)
        
        except Exception as e:
            Print.error("[+] Error in getSMScode")
            Print.error(e)
            return False
        

if __name__ == "__main__":
    
    try:

        res = SMS('COM', 9600, '+7XXXXXXXXXXXX').getSMScode()
        
        if res is not False:
            
            if res == 0: Print.warning("[+] Code not found")
            else: Print.ok(f'[+] Code {res}')
        
        else: Print.warning("[+] An error has occurred")
    
    except Exception as e:
        Print.error("[+] Error in main")
        Print.error(e)

