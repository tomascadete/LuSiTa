from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



########### aws libraries #####################
import awscrt
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
############### time ###################

import datetime



############################# stuff for broker connection #############################################
# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a1mcj6srl638fo-ats.iot.eu-west-2.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "31115e61c1c7f1de2b86d19b401cf3654ae605476d124b406a8703b7c19d9bf1-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "31115e61c1c7f1de2b86d19b401cf3654ae605476d124b406a8703b7c19d9bf1-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "AmazonRootCA1.pem"
TOPIC = "Lusita/DataBase/Receive"
 ########################################################################################################

#Global variabels needed

#### Save ####
TARIFA=""
PARAMETERS=[[]]
TIME=""

#### FLAGs ####
FLAG=False
TIME_FLAG=False


def update_send_sheets():
    
    if TARIFA=="bi_semanal":
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)
            
            # Call the Sheets API
            sheet = service.spreadsheets()

            result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Bi-horária-semanal!C3:C4",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]]]}).execute()


            current_time = datetime.datetime.now()
            minutes=(current_time.minute//15)*15
            current_time=current_time.replace(minute=minutes)    
            current_time=current_time.strftime("%-d/%-m/%y %H:%M")

            print(current_time)


            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-semanal!J14:N2894").execute()

            values = result.get('values', [])

            if not values:
                print('No data found.')
                return

            for i in values:
                if i[0]==current_time:
                    price=i[4]
                    break
           
            start_time=datetime.datetime.now()

            end_time=start_time+datetime.timedelta(minutes=0.5)

            
            while datetime.datetime.now()<end_time:
                print('Begin Publish')
                publish_future = mqtt_connection.publish(
                    topic="Lusita/DataBase/Receive",
                    payload=json.dumps(price),
                    qos=mqtt.QoS.AT_LEAST_ONCE
                )
                print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                print('Publish End')
                t.sleep(10)
            
        except HttpError as err:
            print(err)

    if TARIFA=="bi_diaria":
            print("Bi_DIARIA")
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
            
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Bi-horária-diária!C3:C4",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]]]}).execute()

                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-diária!B13:D768").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[2]
                        print(price)
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)
    
    if TARIFA=="bi_semanal_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()
  
                
                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Bi-horária-semanal-autoconsumo!C3:C6",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]],[PARAMETERS[2]],[PARAMETERS[3]]]}).execute()


                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-semanal-autoconsumo!K14:P2894").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[5]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)

    
    if TARIFA=="bi_diaria_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
            
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Bi-horária-diária-autoconsumo!C3:C6",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]],[PARAMETERS[2]],[PARAMETERS[3]]]}).execute()


                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-diária-autoconsumo!B13:E108").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[3]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)

    
    if TARIFA=="tri_semanal":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
              
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Tri-horária-semanal!C3:C5",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]],[PARAMETERS[2]]]}).execute()


                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-semanal!J14:N2894").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[4]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)

    if TARIFA=="tri_diaria":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Tri-horária-diária!C3:C5",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]],[PARAMETERS[2]]]}).execute()



                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-diária!B13:D108").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[3]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)
    
    if TARIFA=="tri_semanal_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="Tri-horária-semanal-autoconsumo!C3:C7",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]],[PARAMETERS[2]],[PARAMETERS[3]],[PARAMETERS[4]]]}).execute()


                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-semanal-autoconsumo!J14:N2894").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[4]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)

    if TARIFA=="tri_diaria_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                
                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range="Tri-horária-diária-autoconsumo!C3:C7",valueInputOption="RAW", body={"values":[[PARAMETERS[0]],[PARAMETERS[1]],[PARAMETERS[2]],[PARAMETERS[3]],[PARAMETERS[4]]]}).execute()

                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-diária-autoconsumo!B13:D108").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time:
                        price=i[2]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)

    
    if TARIFA=="indexada":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="Indexada!C3",valueInputOption="RAW", body={"values":[[PARAMETERS[0]]]}).execute()


                #esta mal temos de arredondar para a hora!
                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15 
                current_time=current_time
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Indexada!B13:E732").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                for i in values:
                    if i[0]==current_time.hour:
                        price=i[3]
                        break
            
                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5)

                
                while datetime.datetime.now()<end_time:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)
                
            except HttpError as err:
                print(err)

def timed_send():
    global TIME_FLAG
    if TARIFA=="bi_semanal":
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)
          
            # Call the Sheets API
            sheet = service.spreadsheets()
        

            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-semanal!J14:N2894").execute()

            values = result.get('values', [])

            if not values:
                print('No data found.')
                return


            if not TIME_FLAG:
                current_time = datetime.datetime.now()
                minutes=(current_time.minute//15)*15
                current_time=current_time.replace(minute=minutes)    
                current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                print(current_time)

                for i in values:
                    if i[0]==current_time:
                        price=i[4]
                        break


                start_time=datetime.datetime.now()

                end_time=start_time+datetime.timedelta(minutes=0.5) 

            
                while datetime.datetime.now()<end_time and not FLAG:
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')
                    t.sleep(10)

            else:
                for i in values:
                    if i[0]==TIME:
                        price=i[4]
                        break

                TIME_FLAG=False
                
                print('Begin Publish')
                publish_future = mqtt_connection.publish(
                        topic="Lusita/DataBase/Receive",
                        payload=json.dumps(price),
                        qos=mqtt.QoS.AT_LEAST_ONCE
                    )
                print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                print('Publish End')

            
        except HttpError as err:
            print(err)
    
    if TARIFA=="bi_diaria":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
            
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-diária!B13:D768").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return



                if not TIME_FLAG:
                    
                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")
    
                    print(current_time)
                    
                    for i in values:
                        if i[0]==current_time:
                            price=i[2]
                            break
            
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)
                    
                else:
                    for i in values:
                        if i[0]==TIME:
                            price=i[2]
                            break
                    
                    TIME_FLAG=False
                
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')


            except HttpError as err:
                print(err)

    if TARIFA=="bi_semanal_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()
  


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-semanal-autoconsumo!K14:P2894").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return


                if not TIME_FLAG:
                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)

                    for i in values:
                        if i[0]==current_time:
                            price=i[5]
                            break
            
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)
                    
                else:
                    for i in values:
                        if i[0]==TIME:
                            price=i[5]
                            break
                    
                    TIME_FLAG=False
                
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')

                
            except HttpError as err:
                print(err)

    if TARIFA=="bi_diaria_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
            
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Bi-horária-diária-autoconsumo!B13:E108").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return



                if not TIME_FLAG:

                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)

                    for i in values:
                        if i[0]==current_time:
                            price=i[3]
                            break
                
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)

                    else:
                        for i in values:
                            if i[0]==TIME:
                                price=i[3]
                                break

                        TIME_FLAG=False
                
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                                topic="Lusita/DataBase/Receive",
                                payload=json.dumps(price),
                                qos=mqtt.QoS.AT_LEAST_ONCE
                            )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')



                
            except HttpError as err:
                print(err)

    if TARIFA=="tri_semanal":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
              
                # Call the Sheets API
                sheet = service.spreadsheets()
  

                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-semanal!J14:N2894").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                if not TIME_FLAG:
                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)
                    for i in values:
                        if i[0]==current_time:
                            price=i[4]
                            break
                
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)
                    
                else:
                    for i in values:
                            if i[0]==TIME:
                                price=i[4]
                                break

                    TIME_FLAG=False
                
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                                topic="Lusita/DataBase/Receive",
                                payload=json.dumps(price),
                                qos=mqtt.QoS.AT_LEAST_ONCE
                            )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')

                
            except HttpError as err:
                print(err)

    if TARIFA=="tri_diaria":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-diária!B13:D108").execute()

                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return

                if not TIME_FLAG:
                    
                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)
                    for i in values:
                        if i[0]==current_time:
                            price=i[3]
                            break
                
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)
                    
                    else:
                        for i in values:
                            if i[0]==TIME:
                                price=i[3]
                                break
                        
                        TIME_FLAG=False
                
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                                    topic="Lusita/DataBase/Receive",
                                    payload=json.dumps(price),
                                    qos=mqtt.QoS.AT_LEAST_ONCE
                                )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')

                
            except HttpError as err:
                print(err)

    if TARIFA=="tri_semanal_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-semanal-autoconsumo!J14:N2894").execute()

                values = result.get('values', [])

                if not TIME_FLAG:

                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)
                    if not values:
                        print('No data found.')
                        return

                    for i in values:
                        if i[0]==current_time:
                            price=i[4]
                            break
                
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)

                else:
                    for i in values:
                            if i[0]==TIME:
                                price=i[4]
                                break
                    
                    TIME_FLAG=False
                
                        
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                                    topic="Lusita/DataBase/Receive",
                                    payload=json.dumps(price),
                                    qos=mqtt.QoS.AT_LEAST_ONCE
                                )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')

                
            except HttpError as err:
                print(err)

    if TARIFA=="tri_diaria_autoconsumo":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()

                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Tri-horária-diária-autoconsumo!B13:D108").execute()

                values = result.get('values', [])

                if not TIME_FLAG:
                    
                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)

                    if not values:
                        print('No data found.')
                        return

                    for i in values:
                        if i[0]==current_time:
                            price=i[2]
                            break
                
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)
                    
                else:
                    for i in values:
                            if i[0]==TIME:
                                price=i[2]
                                break

                    TIME_FLAG=False
                
                        
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                                    topic="Lusita/DataBase/Receive",
                                    payload=json.dumps(price),
                                    qos=mqtt.QoS.AT_LEAST_ONCE
                                )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')


                
            except HttpError as err:
                print(err)

    if TARIFA=="indexada":
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            try:
                service = build('sheets', 'v4', credentials=creds)
                
                # Call the Sheets API
                sheet = service.spreadsheets()


                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Indexada!B13:E732").execute()

                values = result.get('values', [])


                if not TIME_FLAG:
                    
                    current_time = datetime.datetime.now()
                    minutes=(current_time.minute//15)*15
                    current_time=current_time.replace(minute=minutes)    
                    current_time=current_time.strftime("%-d/%-m/%y %H:%M")

                    print(current_time)
                    if not values:
                        print('No data found.')
                        return

                    for i in values:
                        if i[0]==current_time:
                            price=i[3]
                            break
                
                    start_time=datetime.datetime.now()

                    end_time=start_time+datetime.timedelta(minutes=0.5)

                    
                    while datetime.datetime.now()<end_time:
                        print('Begin Publish')
                        publish_future = mqtt_connection.publish(
                            topic="Lusita/DataBase/Receive",
                            payload=json.dumps(price),
                            qos=mqtt.QoS.AT_LEAST_ONCE
                        )
                        print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                        print('Publish End')
                        t.sleep(10)

                else:
                    for i in values:
                            if i[0]==TIME:
                                price=i[3]
                                break
                        
                    TIME_FLAG=False
                
                        
                    print('Begin Publish')
                    publish_future = mqtt_connection.publish(
                                    topic="Lusita/DataBase/Receive",
                                    payload=json.dumps(price),
                                    qos=mqtt.QoS.AT_LEAST_ONCE
                                )
                    print("Published: '" + json.dumps(price) + "' to the topic: " + "'test/testing'")
                    print('Publish End')

                
            except HttpError as err:
                print(err)

def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    payload = payload.decode('utf-8')
    parameters=payload.split()
    global TARIFA
    global PARAMETERS
    global FLAG
    global TIME_FLAG
    global TIME
    
    if parameters[0]=="bi_semanal":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return

  
    if parameters[0]=="bi_diaria":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return

    if parameters[0]=="bi_semanal_autoconsumo":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return

    if parameters[0]=="bi_diaria_autoconsumo":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return

    if parameters[0]=="tri_semanal":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return
      
    if parameters[0]=="tri_diaria":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return
    
    if parameters[0]=="tri_semanal_autoconsumo":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return
    
    if parameters[0]=="tri_diaria_autoconsumo":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return

    if parameters[0]=="indexada":
        TARIFA=parameters[0]
        parameters.pop(0)
        PARAMETERS=parameters
        print("TESTE:",PARAMETERS)
        FLAG=True
        return

    if parameters[0]=="time":
        TIME_FLAG=True
        TIME=parameters[1]+" "+parameters[2]
        print(TIME)
        timed_send()
        return
        
        

def BrokerConnect():
    # Spin up resources 
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    global mqtt_connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=ENDPOINT,
                cert_filepath=PATH_TO_CERTIFICATE,
                pri_key_filepath=PATH_TO_PRIVATE_KEY,
                client_bootstrap=client_bootstrap,
                ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
                client_id=CLIENT_ID,
                clean_session=False,
                keep_alive_secs=6
                )

    print("Connecting to {} with client ID '{}'...".format(
            ENDPOINT, CLIENT_ID))
    try:
    # Make the connect() call
        connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
        connect_future.result()  
    #pode não ser o mesmo erro caso o broker vá a baixo.. isto é o que me dá quando não tenho net
    # contudo a vm esta na cloud por isso não se é o mesmo  
    except awscrt.exceptions.AwsCrtError:
        return False


    print("Connected!")
    mqtt_connection.subscribe(topic="Lusita/DataBase/Publish", qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received)
    return True 

#If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID = '1m9LccczO1oGm-q5yPl_lR5pSnfLECJY0MqSVBfmJxtw'
SAMPLE_RANGE_NAME = 'Autoconsumo!A1'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("Desde de inicio")


    while True:
        global FLAG     

        if TARIFA=="bi_semanal":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send()    

        if TARIFA=="bi_diaria":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send() 

        if TARIFA=="bi_semanal_autoconsumo":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send() 
        
        if TARIFA=="bi_diaria_autoconsumo":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send() 

        if TARIFA=="tri_semanal":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send() 
        
        if TARIFA=="tri_diaria":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send()
        
        if TARIFA=="tri_semanal_autoconsumo":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send()
        
        if TARIFA=="tri_diaria_autoconsumo":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send()
        
        if TARIFA=="indexada":
            if FLAG:
                update_send_sheets()
                FLAG=False

            current_time = datetime.datetime.now()
            minutes=current_time.minute
            if minutes%2==0:#esta a spamar
                #ter em atenção que se retornar-mos do update _send_sheets apos entrar as 18:14 e sair as 18:23 não entra aqui e ate as 18:30 vai ficar com a informação das 18H
                timed_send()


        t.sleep(1)


if __name__ == '__main__':
    
    CONNECTED=False

    while not CONNECTED:
       CONNECTED=BrokerConnect()
    main()