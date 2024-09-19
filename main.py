import cantools
import configparser
import pandas as pd
import os
import numpy
import datetime


def switch_plicas_aspas(stringsf: str):
  return stringsf.replace("'", '"')
def colapse_columns_into_array(json: dict):
  result = {}
  for entry in json:
    for key, value in entry.items():
        # If the key is not already in result, initialize it with an empty list
        if key not in result:
            result[key] = []
        # Append the value to the corresponding list in result
        result[key].append(value)
  return result
def turn_json_csv(json: dict):
  #make each key a column and separate it by ; 
  df = pd.DataFrame(json)

  # Save DataFrame to CSV
  df.to_csv('output.csv', index=False)

#go into config.ini input.path
config = configparser.ConfigParser()
#check if config.ini exists
if not os.path.exists('config.ini'):
  print("O ficheiro config.ini não existe, por favor cria um ficheiro config.ini com as seguintes configurações:")
  print("[input]")
  print("path = /path/to/your/files")

config.read('config.ini')

path = config['input']['path']
path_db = config['input']['path_db']
path_db = path_db.replace('"', "")
db = cantools.database.load_file(path_db)
#print(db.messages)

dictionary = {
  "pos_hour": config['input']['pos_hour'],
  "pos_minute": config['input']['pos_minute'],
  "pos_second": config['input']['pos_second'],
  "pos_ms": config['input']['pos_ms'],
  "pos_id": config['input']['pos_id'],
  "pos_bytes": config['input']['pos_bytes']
}
oldtime = 0
# remove the "
path = path.replace('"', "")

#ceck if directory exists
if os.path.exists(path):
  #foreach file that exists 
  bufferFile = []
  for file in os.listdir(path):
    #read the file
    with open(path+file, 'r') as f:
      lines = f.readlines()
      #remove /n from lines
      lines = [x.strip() for x in lines]

      if lines is not None:

        bufferFile.append(lines)
      else:
        print("O ficheiro: "+file+" está vazio, tenta de novo pato")
      
      #close file
      f.close()
  #FLATTEN bufferFile
  bufferFile = numpy.array(bufferFile).flatten()
  output = []
  
  for line in bufferFile:
    
    
    #split the line by ,
    fat = []
    fat = line.split(",")
    #print (fat)
    print(fat)
    hora = fat[int(dictionary["pos_hour"])]
    minuto = fat[int(dictionary["pos_minute"])]
    segundo = fat[int(dictionary["pos_second"])]
    ms = fat[int(dictionary["pos_ms"])]
    try:
      timestamp= int(hora)*3600000 + int(minuto)*60000 + int(segundo) * 1000 + int(ms)
    except:
      print("Existe campos vazios na hora, minuto, segundo ou ms")
      timestamp = oldtime + 1
    id_s = fat[int(dictionary["pos_id"])]
    
    byte_s = fat[int(dictionary["pos_bytes"]):]
    try:
      id_s = int(id_s, 16)
      
      #convert string into hexadecimal integers
      byte_s = [int(x, 16) for x in byte_s]
      byte_s = bytes(byte_s)
      
      print("id"+str(id_s))
      print(byte_s)
      f = db.decode_message(id_s, byte_s)
      
      
    except:
      print("Erro ao decodificar a mensagem")
    #f["timestamp"] = timestamp
    k:dict = f
    k['tp'] = timestamp
    oldtime = timestamp
    output.append(k)
    

    #
  print("=========DONE==========")
  
  turn_json_csv(output)
  
  #write time.log.json
  #unixtime = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()
  
  
  #unixtime=int(unixtime)
  #write_ = switch_plicas_aspas(str(output))
  
  #with open(str(unixtime)+'.log.json', 'w') as f:
  #  f.write(write_)
  #  f.close()
  
    # T
  #for line in bufferFile:
  #print (line)
else:
  print("O diretório não existe, por favor cria um diretório com o nome: "+path)
  


