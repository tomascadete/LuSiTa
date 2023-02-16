from utime import sleep
import sys
import network
from umqttsimple import MQTTClient
import ubinascii
from machine import Pin, unique_id, reset ,DAC ,ADC
import time

#from time import ticks_ms

# Definir os Pinos----------------------------

# but = Pin(23, Pin.IN, Pin.PULL_UP)

led = DAC(Pin(25))
led.write(0)

PIR = Pin(23, Pin.IN, Pin.PULL_UP)

Res = ADC(Pin(34))
#--------------------------------------------
#Definir valores default de variáveis globais-------------------

global ligado
ligado = False

global max_ligado
max_ligado = False

global intensidade
intensidade = 0

global led_PIR_ON
led_PIR_ON = False

global led_Res_ON
led_Res_ON = False

global Operation_Mode
Operation_Mode = "Modo luminosidade"

global Previous_op_mode
Previous_op_mode = Operation_Mode

global lum_avg
lum_avg = Res.read()

global Trigger_lum
Trigger_lum = 1  #Colocar como topico

global connect_attempts
connect_attempts = 0

global Connected_to_broker
Connected_to_broker = False

global Connected_to_wifi
Connected_to_wifi = False
#--------------------------------------------
#Definir configurações do wifi---------------

ssid = "Vodafone-A1A035"
password = "5ETDZKgC68"

# ssid = "LAPTOPUSF7T8QQ 4579"
# password = "2^f57B35"

#ssid = "TomTomWIFI"
#password = "12345678"
#--------------------------------------------
#Definir configurações do MQTT---------------
mqtt_server = "192.168.1.69"

client_id = "ESP32"
#--------------------------------------------


def connect_to_wifi():
    global Connected_to_wifi
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())
        Connected_to_wifi = True
    except:
        Connected_to_wifi = False
        print("Couldn't connect to Wifi. Please verify the provided SSID, password and if the Wifi network is active")
        sleep(1)
        pass

def sub_cb(topic, message):
    print("Received MQTT message: topic '{0}', value '{1}'" \
        .format(topic.decode("utf-8"), message.decode("utf-8")))

    global ligado
    global intensidade
    global Operation_Mode
    global max_ligado
    global lum_avg
    global Trigger_lum
    global led_PIR_ON
    global led_Res_ON
    global Previous_op_mode

    #Este if determina o modo de operação do sistema ----------------------------
    if topic == b'operation_Mode':  #This topic should be retained in the Phone client
        if message == b'luminosidade':
            Operation_Mode = "Modo luminosidade"
            led_Res_ON = False
            led_PIR_ON = False
        elif message == b'luminosidade_e_presenca':
            Operation_Mode = "Modo luminosidade e presença"
            led_Res_ON = False
            led_PIR_ON = False
        print("Changed op mode to:", Operation_Mode)
        sleep(2)

    #-----------------------------------------------------------------------------
    #Os if's seguintes determinam os estados da luz com maior prioridade, i.e. não dependem do modo de operação
    elif topic == b'led_value': #This topic should be retained in the Phone client
        if message == b'1':
            ligado = True
            #led.write(int(intensidade))
        else:
            ligado = False
            #led.write(0)

    elif topic == b'led_intensity':  #This topic should be retained in the Phone client
        if int(message) == 0 and max_ligado == False:
            led.write(0)
        else:
            intensidade = 0.64*int(message) + 191
            if ligado == True and max_ligado == False and lum_avg < Trigger_lum:
                led.write(int(intensidade))

    elif topic == b'led_full_brightness':
        if message == b'1':
            max_ligado = True
            led.write(255)
        elif ligado == True and message == b'0':
            max_ligado = False
            if lum_avg < Trigger_lum:
                led.write(int(intensidade))
            else:
                led.write(0)
        elif ligado == False and message == b'0':
            max_ligado = False
            led.write(0)
    #-----------------------------------------------------------------------------

def connect_to_broker():
    global Connected_to_broker
    global connect_attempts
    while Connected_to_broker == False:
        try:
            global connect_attempts
            mqtt_client = MQTTClient(client_id = client_id,server = mqtt_server,port = 1883,keepalive=30,user=None, password=None, ssl=False)
            mqtt_client.set_callback(sub_cb)
            mqtt_client.connect()
            Connected_to_broker = True
            connect_attempts = 0
            print('Connected to {0} MQTT broker'.format(mqtt_server))
        except:
            global connect_attempts
            Connected_to_broker = False
            connect_attempts += 1
            print('Failed to connect to MQTT broker,for the {0}º time. Reconnecting...'.format(connect_attempts))
            sleep(5)

            if connect_attempts > 3:
                print("Couldn't connect to MQTT broker, please verify if the broker is operating. *Restarting the Esp32*.")
                sleep(5)
                reset()

            else:
                pass

    return mqtt_client

def subscribe_to_topics(mqtt_client):

    topics = ['led_value','led_intensity','led_full_brightness',"operation_Mode"]

    for topic_i in topics:
        mqtt_client.subscribe(topic_i)
        sleep(0.1)

    print(f"Subscribed to: {', '.join([topic for topic in topics[:]])}")

global last_sample
last_sample = -1
global luminosity_values
luminosity_values = []
global innit_sensor
innit_sensor = 0

def Sensors():
    global Trigger_lum
    global luminosity_values
    global last_sample
    global innit_sensor
    global lum_avg

    now = time.ticks_ms()
    if now - last_sample >= 1*1000 and len(luminosity_values) < 10:      # now - last_sample = *sampling period* *10000, len(luminosity_values) < *Number of luminosity samples*
        luminosity_values.append(Res.read()*3.3/4096)
        last_sample = time.ticks_ms()
        print("len=",len(luminosity_values))
    if len(luminosity_values) >= 10:
        #print("bruh2")
        mean = 0
        for i in luminosity_values:
            mean += i/10
        luminosity_values = []
        innit_sensor = 1
        lum_avg = mean
        if lum_avg >= Trigger_lum:
            mqtt_client.publish(b"luminosidade",b"luminosidade elevada")
        else:
            mqtt_client.publish(b"luminosidade",b"luminosidade baixa")
    if innit_sensor == 0:
        return Res.read()*3.3/4096
    else:
        return lum_avg


def publisher(mqtt_client):
    but_state = False
    global led_PIR_ON
    led_PIR_ON = False
    global led_Res_ON
    led_Res_ON = False

    ON_time = 10*1000 #Colocar como topico #Tempo em que o led fica ligado, depois de ser ativado pelo PIR, em segundos

    global lum_avg
    global ligado
    global max_ligado
    global Connected_to_broker
    global intensidade
    global Operation_Mode
    start = 0
    Previous_op_mode = Operation_Mode
    while Connected_to_broker == True:
        try:
            lum_avg = Sensors() #Função que calcula o valor médio da luminosidade


            now = time.ticks_ms()
            timer = now - start

            print(timer)
            print("PIR,LUM",PIR.value(),lum_avg,Res.read())

            mqtt_client.check_msg() #Ver se há mensagens no broker

#             if but.value() != but_state:
#                 but_state = not but_state
#                 msg = 'Button ' + ('OFF' if but_state else 'ON')
#                 print(msg)
#                 mqtt_client.publish(b'button', b'0' if vut_state else b'1')

            #print("hellopub")
            #Aqui defino o que acontece quando tanto o PIR como o sensor de luminosidade afetam o LED-----------------
            if Operation_Mode == "Modo luminosidade e presença" and max_ligado == False:
                #print("hellopub2")
                if lum_avg < Trigger_lum and PIR.value() == 0:
                    if timer >= ON_time:
                        mqtt_client.publish(b'PIR', b'Movimento detectado')
                    if ligado == True and led_PIR_ON == False:
                        start = time.ticks_ms()
                        led_PIR_ON = True
                        led.write(int(intensidade))

                elif lum_avg < Trigger_lum and PIR.value() == 1 and timer >= ON_time:
                    mqtt_client.publish(b'PIR', b'Nenhum movimento detectado')
                    if led_PIR_ON == True:
                        led.write(0)
                        led_PIR_ON = False

                elif lum_avg > Trigger_lum and timer >= ON_time and led_PIR_ON == True:
                    led.write(0)
                    led_PIR_ON = False

                if ligado == False:
                    led.write(0)
                    led_PIR_ON = False


            #--------------------------------------------------------------------------------------------------------
            #Aqui defino o que acontece quando apenas sensor de luminosidade afeta o LED-----------------------------

            elif Operation_Mode == "Modo luminosidade" and max_ligado == False:
                led_PIR_ON = False
                #print("hellopub3")
                if lum_avg > Trigger_lum and led_Res_ON == True:
                    led.write(0)
                    led_Res_ON = False
                elif lum_avg < Trigger_lum and led_Res_ON == False:
                    if ligado == True:
                        led.write(int(intensidade))
                        led_Res_ON = True
                if ligado == False:
                    #print("hellopub6")
                    led.write(0)
                    led_Res_ON = False

            #----------------------------------------------------------------------------------------------------------
        except OSError as e:
            Connected_to_broker = False
            print("Connection has been interrupted. Trying to reconnect...")
            sleep(2)
            pass
        except KeyboardInterrupt:
            sys.exit("KeyboardInterrupt was raised")
        sleep(0.4)
    return


while True:
    if Connected_to_wifi == False:
        connect_to_wifi()
        sleep(1)
    elif Connected_to_broker == False and Connected_to_wifi == True:
        mqtt_client = connect_to_broker()
        subscribe_to_topics(mqtt_client)
        publisher(mqtt_client)
    elif Connected_to_broker == True and Connected_to_wifi == True:
        subscribe_to_topics(mqtt_client)
        publisher(mqtt_client)




