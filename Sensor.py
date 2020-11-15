import signal
import sys
import requests
import urllib.parse
import json
import time
import psutil
from bmp180 import bmp180

bmp = bmp180(0x77)

# Crear canal

metodo = 'POST'
uri = "https://api.thingspeak.com/channels.json"
cabeceras = {'Host': 'api.thingspeak.com', 'Content-Type': 'application/x-www-form-urlencoded'}
contenido = {'api_key': 'FS4JEW6KCH12Y2JF', 'name': 'Sensor', 'field1': "Temperatura (ºC)", 'field2': "Presión (hPa)", 'field3': "Altura (m)"}
contenido_encoded = urllib.parse.urlencode(contenido)
cabeceras['Content-Length'] = str(len(contenido_encoded))
respuesta = requests.request(metodo, uri, data=contenido_encoded, headers=cabeceras, allow_redirects=False)


codigo = respuesta.status_code
descripcion = respuesta.reason
print(str(codigo) + " " + descripcion)
contenido = respuesta.content
print(contenido)

contenido_python = json.loads(contenido)
channel_id = contenido_python["id"]
for each in contenido_python['api_keys']:
    if each['write_flag'] == True:
        write_api_key = each['api_key']
    else:
        read_api_key = each['api_key']

print("Canal creado")

# Gestión de la parada

def handler(sig_num, frame):
    # Gestión del evento
    print('\nSignal handler called with signal ' + str(sig_num))
    print('Check signal number on ' 'https://en.wikipedia.org/wiki/Signal_%28IPC%29#Default_action')

    print('\nExiting gracefully')

    # Si se desea eliminar el contenido del canal una vez detenido la ejecucion
    
    #metodo = "DELETE"
    #uri = "https://api.thingspeak.com/channels/" + str(channel_id) + "/feeds.json"
    #cabeceras = {"Host": "api.thingspeak.com", "Content-Type": "application/x-www-form-urlencoded"}
    #cuerpo = {"api_key": "FS4JEW6KCH12Y2JF"}
    #cuerpo_coded = urllib.parse.urlencode(cuerpo)

    #respuesta = requests.delete(uri, headers=cabeceras, data=cuerpo_coded)

    #codigo = respuesta.status_code
    #print("Status: " + str(codigo))

    #descripcion = respuesta.reason
    #print("Descripción: " + descripcion)

    #cuerpo_json = respuesta.content
    #print(cuerpo_json)

    sys.exit(0)

if __name__ == '__main__':
    # Cuando se reciba SIGINT, se ejecutará el método "handler"
    signal.signal(signal.SIGINT, handler)

    print('Running. Press CTRL-C to exit.')
    
    while True:
        
        temperature = bmp.get_temp()
        pressure = bmp.get_pressure()
        altitude = bmp.get_altitude()*1000

        metodo = "POST"
        uri = "https://api.thingspeak.com/update"
        cabeceras = {"Host": "api.thingspeak.com", "Content-Type": "application/x-www-form-urlencoded"}
        cuerpo = {"api_key": write_api_key, "field1": temperature, "field2": pressure, "field3": altitude}
        cuerpo_coded = urllib.parse.urlencode(cuerpo)

        respuesta = requests.post(uri, headers=cabeceras, data=cuerpo_coded)

        codigo = respuesta.status_code
        print("Status: " + str(codigo))

        descripcion = respuesta.reason
        print("Descripción: " + descripcion)

        cabeceras = respuesta.headers
        for each in cabeceras:  # each contiene el nombre de la cabecera
            valor = respuesta.headers[each]
            print("\t" + each + ": " + valor)

        cuerpo = respuesta.content

        print(cuerpo)
        print("Dato subido")
        time.sleep(300)




