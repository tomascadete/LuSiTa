import utime as time
from machine import I2C, Pin, RTC, reset
from utime import sleep
import sys
import network
from umqttsimple import MQTTClient
import ntptime



#O Código das classes Device e HT16K33Segment foi baseado em https://github.com/smittytone/HT16K33-Python e https://github.com/hybotics/Hybotics_Micropython_HT16K33.
# Algumas funções são iguais, outras foram alteradas para as simplificar ou tornar mais clara a sua função. 

class Device:
    """
    Esta classe define métodos low-level. Interagem diretamente com o display através do protocolo I2C.  
    """


    # Definição de comandos/addresses que serão chamadas posteriormente

    DISPLAY_ON = 0x81
    DISPLAY_OFF = 0x80 # -> 10000001
    SYSTEM_ON = 0x21 # -> 00100001
    SYSTEM_OFF = 0x20  # -> 00100000
    DISPLAY_ADDRESS = 0x00
    CMD_BRIGHTNESS = 0xE0 # -> 11100000
    CMD_BLINK = 0x81 # -> 10000001 

    # Valores default 
    
    brilho = 15
    
    blink_freq = 0
    
    def __init__(self, i2c, i2c_address):
        """
        Esta função inicializa a classe que interage a um nivel mais baixo com o display. 
        """

        self.i2c = i2c
        self.address = i2c_address
        self.start_up()

    def set_blink_freq(self,blink_freq):
        """
        Define a Frequência do piscar do display

        A Frequência do piscar deve ser 0, 0.5, 1 ou 2 Hz. 
        Default: blink_freq = 0 (Não pisca)
        """
        assert blink_freq in (0, 0.5, 1, 2), "Erro - Frequência inválida, apenas [0, 0.5, 1, 2] são permitidos"
        
        Bin_freq_dict =  {0:0x0, 0.5:0x3,1:0x2,2:0x1}

        # << -> Desloca 1 bit para a esquerda, | -> Operação OR bit a bit nos numeros

        data_byte = self.CMD_BLINK | Bin_freq_dict[blink_freq] << 1
        
        self._write_cmd(data_byte)


    def set_brilho(self, brilho=15):
        """
        Define o brilho do display

        O brilho deve ser um valor entre 0 (0000) e 15 (1111)
        """
        assert brilho >= 0 and brilho <= 15, "Erro - Brilho inválido, deve ser um valor entre 0 e 15"

        self._write_cmd(self.CMD_BRIGHTNESS | brilho)


    def clear(self):
        """
        Limpa os valores no display
        """

        for i in range(0, len(self.buffer)): self.buffer[i] = 0x00
        return self
    
    def start_up(self):
        """
        Função que inicializa o display com o valores atual de Brilho 
        """
        self._write_cmd(self.SYSTEM_ON)
        self._write_cmd(self.DISPLAY_ON)
         

    def Desligar(self):
        """
        Desliga o display e o sistema
        """
        self._write_cmd(self.DISPLAY_OFF)
        self._write_cmd(self.SYSTEM_OFF)

    def update(self):
        """
        Esta função escreve no display o valor do buffer
        """
        buffer = bytearray(len(self.buffer) + 1)
        buffer[1:] = self.buffer
        buffer[0] = 0x00
        self.i2c.writeto(self.address, bytes(buffer))

    def _write_cmd(self, byte):
        """
        Função geral que envia um comando para o sistema do display
        """
        self.i2c.writeto(self.address, bytes([byte]))




class HT16K33Segment(Device):

    """
    Esta classe define métodos medium-level. Utilizam os métodos criados na classe Device para alterar o estado do display. 
    O funcionamento geral relaciona-se com as alterações que são feitas a um buffer (um array de bits), buffer que é depois enviado para o display atravéz de I2C.
    Em geral o buffer guarda os valores que serão mostrados no display de acordo com o código ASCII.
    """

    # *********** CONSTANTS **********

    HT16K33_SEGMENT_COLON_ROW = 0x04

    # Posições dos segmentos dentro do buffer. 
    POS = (0, 2, 6, 8)

    # Este dicionário contém "todos" os caractéres distintos possíveis de escrever com um display de 7 segmentos, guardados no formato hexadecimal.   
    CHARSET = {"0":'0x3F',"1":'0x06',"2":'0x5B',"3":'0x4F',"4":'0x66',"5":'0x6D',"6":'0x7D',"7":'0x07',"8":'0x7F',"9":'0x6F',\
    "a":'0x77',"b":'0x7C',"c":'0x39',"d":'0x5E',"e":'0x79',"f":'0x71',"g":'0x3C',"h":'0x76',"i":'0x30',"j":'0x1E',"l":'0x38',\
    "n":'0x54',"o":'5C',"p":'0x73',"s":'0x6D',"u":'0x3E',"y":'0x6E',\
    "-":'0x40'," ":'0x00',}
    # *********** CONSTRUCTOR **********

    def __init__(self, i2c, i2c_address=0x70):
        """
        Esta função inicializa a classe que interage a um nivel intermédio com o display. 
        """
        self.buffer = bytearray(16)    
        super(HT16K33Segment, self).__init__(i2c, i2c_address)


    def set_colon(self, is_set=True):
        """
        Esta função muda o estado dos 2 pontos (":") do display.
        """
        self.buffer[self.HT16K33_SEGMENT_COLON_ROW] = 0x02 if is_set is True else 0x00
        return self

    def set_glyph(self, glyph, digit=0, has_dot=False):
        """
        Esta função dá a oportunidade de definir um padrão qualquer num segmento do display. Não necessitando desse padrão existir no dicionário CHARSET. 

        A lógica da sequência de 8 bits que formam o "glyph" relaciona-se com o seguinte diagrama:
                0
                _
            5 |   | 1
              |   |
                - <----- 6
            4 |   | 2
              | _ |
                3
        Cada segmento (led) corresponde a uma posição no array glyph, posição que é dada pelo diagrama, lida da direita para a esquerda no glyph (x6543210). 
        Se o bit correspondente á sua posição for 1, o led liga, se for 0, desliga. 
        Por exemplo: Quero ativar o segmento de cima (que é a casa 0 do glyph) e o segmento do canto inferior esquerdo (ue é a casa 4 do glyph), do *segundo* digito do display. 
        O meu array glyph deve então ser 00010001. Que em hexadecimal é 0x11. Devo então chamar a função da forma: set_glyph("0x11",2,False) (True se quiser o ponto)
        
        Esta lógica matém se verdade para todos os caracteres disponiveis no dicionário. Por exemplo: 3->'0x4F'-> 01001111 que é exatamente o estado em que o segmento 4 e 5 estão desligados. 
        """
        assert 0 <= digit < 4, "ERRO - Digito inválido, deve ser 0,1,2 ou 3"
        assert 0 <= glyph < 0xFF, "ERRO -  glyph {} inválido, deve estar no intervalo (0x00-0xFF)".format(glyph)
        self.buffer[self.POS[digit]] = glyph
        if has_dot is True: self.buffer[self.POS[digit]] |= 0x80
        return self

    def set_number(self, number, digit=0, has_dot=False):
        """
        Esta função serve para colocar um número no buffer, set_character também serve para números.
        """
        assert 0 <= digit < 4, "ERROR - Invalid digit (0-3) set in set_number()"
        assert 0 <= number < 10, "ERROR - Invalid value (0-9) set in set_number()"
        return self.set_character(str(number), digit, has_dot)

    def set_character(self, char, digit=0, has_dot=False):
        """
        Esta função coloca o caracter (char) pretendido no buffer. Não atualiza automáticamente o display, para isso é nessário fazer update(). 
        """

        assert 0 <= digit < 4, "ERRO - Digito incorreto, deve ser 0,1,2 ou 3"
        char = char.lower()
        print("char:",char,"ord(char): ",ord(char),"char type: ",type(char))

        print("self.CHARSET[char]:",self.CHARSET[char])
        try: 
        
            char_val = int(self.CHARSET[char],16)
        except:
            print("Erro - Caracter {} é inválido".format(char))
            raise KeyboardInterrupt
       
        print("char_val:",char_val)


        self.buffer[self.POS[digit]] = char_val
        if has_dot is True: self.buffer[self.POS[digit]] |= 0x80
        return self
    
    def push(self, value_in="0xFF",has_dot=False):
        """
        Desloca os caracteres presentes no buffer uma casa para a esquerda, e coloca um novo caracter no buffer no 
        lugar aberto. Não atualiza automáticamente o display. 
        """
        if type(value_in) != str:
            value_in = str(value_in)
        print("buffer before: ",self.buffer)
        for index in range(1,4):
            self.buffer[self.POS[index - 1]] = self.buffer[self.POS[index]]
        
        self.set_character(value_in, 3, has_dot)
        print("buffer after: ",self.buffer)
        return self


class Communication:
    """
    Esta classe inicializa as comunicações por wifi e mqtt. 
    """

    def __init__(self,SSID,wifi_pass,mqtt_server,client_id):
        """
        Construtor da classe
        SSID -> ID da wifi network usada | wifi_pass -> password da rede wifi
        mqtt_server -> ID do broker mqtt, usando um servidor de wifi local, é o IP privado do computador onde está o broker. 
        client_id -> ID do esp32 no mqtt broker, pode ser um nome qualquer caso seja usada uma rede privada.  
        """
        SSID = 

        
        self.connect_to_wifi(SSID,wifi_pass)
        self.mqtt_client = self.connect_to_broker(mqtt_server,client_id)
        self.subscribe_to_topics(self.mqtt_client)

    
    def connect_to_wifi(self,SSID,wifi_pass):
        """
        Esta função conecta o esp32 á rede wifi definida.
        """
        
        self.Connected_to_wifi = False 
        
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            if not wlan.isconnected():
                print('connecting to network...')
                wlan.connect(ssid, password)
                while not wlan.isconnected():
                    pass
            print('network config:', wlan.ifconfig())
            self.Connected_to_wifi = True
        except:
            self.Connected_to_wifi = False
            print("Couldn't connect to Wifi. Please verify the provided SSID, password and if the Wifi network is active")
            sleep(1)
            pass

    def connect_to_broker(self,mqtt_server,client_id):
        """
        Esta função conecta o esp32 ao mqtt broker.
        """

        self.Connected_to_broker = False
        self.connect_attempts = 0
        while self.Connected_to_broker == False:
            try:
                self.mqtt_client = MQTTClient(client_id = client_id,server = mqtt_server,port = 1883,keepalive=30,user=None, password=None, ssl=False)
                self.mqtt_client.set_callback(self.message_controller)
                self.mqtt_client.connect()
                self.Connected_to_broker = True
                self.connect_attempts = 0
                print('Connected to {0} MQTT broker'.format(mqtt_server))
            except:
                
                self.Connected_to_broker = False
                self.connect_attempts += 1
                print('Failed to connect to MQTT broker,for the {0}º time. Reconnecting...'.format(self.connect_attempts))
                sleep(5)

                if self.connect_attempts > 3:
                    print("Couldn't connect to MQTT broker, please verify if the broker is operating. *Restarting the Esp32*.")
                    sleep(5)
                    reset()

                else:
                    pass

        return self.mqtt_client

    def subscribe_to_topics(self,mqtt_client):

        topics = ['Operation_mode','blink_freq','brilho']

        for topic_i in topics:
            self.mqtt_client.subscribe(topic_i)
            sleep(0.1)

        print(f"Subscribed to: {', '.join([topic for topic in topics[:]])}")

    def message_controller(self,topic,message):
            
            print("Received MQTT message: topic '{0}', value '{1}'" \
    .format(topic.decode("utf-8"), message.decode("utf-8")))

        if topic == b'Operation_mode':
            if message == b"hora_local":
                ntptime.settime()
                UTC_OFFSET = 1 * 60 * 60 
                actual_time = time.localtime(time.time() + UTC_OFFSET)
                print(actual_time)




DELAY = 0.01
PAUSE = 3

# START
if __name__ == '__main__':
    i2c = I2C(scl=Pin(5), sda=Pin(4))
    display = HT16K33Segment(i2c)
    display.set_brilho(2)

    
    coms = Communication()



    # Write 'SYNC' to the LED using custom glyphs
    sync_text = b"\x6D\x6E\x37\x39"
    for i in range(len(sync_text)):
        display.set_glyph(sync_text[i], i)
    display.update()
    time.sleep(PAUSE)

    # Write 'SYNC' to the LED -- this time with decimal points

    # Write 'BEEF' to the display using the charset characters
    display.set_character("B", 0).set_character("E", 1)
    display.set_character("E", 2).set_character("F", 3)
    display.update()
    time.sleep(PAUSE)

    # Show a countdown using the charset numbers
    # (also uses 'set_colon()')
    count = 0100
    colon_state = True
#     while True:
#          Convert 'count' into Binary-Coded Decimal (BCD)
#         bcd = int(str(count), 16)

#          Display 'count' as decimal digits
#         display.set_number((bcd & 0xF000) >> 12, 0)
#         display.set_number((bcd & 0x0F00) >> 8, 1)
#         display.set_number((bcd & 0xF0) >> 4, 2)
#         display.set_number((bcd & 0x0F), 3)

#         if count % 10 == 0: colon_state = not colon_state
#         display.set_colon(colon_state).update()

#         count -= 1
#         if count < 0: break

#          Pause for breath
#         time.sleep(DELAY)

    # Flash the LED
    display.clear()
    display.update()

    for carc in "0123456789abcdefghijlnopsuy -":
        display.push(carc,False)
        display.update()
        time.sleep(1)
    display.clear()
    display.update()
 #    display.set_blink_freq(0)
#     display.set_character("A", 0).set_character("B", 1)
#     display.set_character("C", 2).set_character("D", 3)
#     display.update()
#     time.sleep(3)
#     display.clear()
#     display.update()
#     display.set_character("E", 0).set_character("F", 1)
#     display.update()
#     time.sleep(3)
#     display.clear()
#     display.update()
#     display.set_glyph(glyph = 00000001, digit=0, has_dot=False)
#     display.set_glyph(glyph = 00000010, digit=0, has_dot=False)
#     display.update()
#     display.clear()
#     display.update()
#     display.set_number(1, 0)
#     display.set_number(3, 1)
#     display.set_number(9, 2)
#     display.set_character("A", 3)
#     display.update()
#     time.sleep(2)
#     display.push(1,False)
#     display.update()
#     time.sleep(2)
#     display.push("1",False)
#     display.update()
#     time.sleep(2)
#     display.push(" ",False)
#     display.update()