import cantools
import configparser
import pandas as pd
import os
import numpy
from datetime import datetime
import time
class timeframe:
  def __init__(self, hour, minute, second, millis):
    self.hour = hour
    self.minute = minute
    self.second = second
    self.millis = millis
  def __str__(self):
    return str(self.hour)+":"+str(self.minute)+":"+str(self.second)+"."+str(self.millis)
  def __repr__(self):
    return str(self.hour)+":"+str(self.minute)+":"+str(self.second)+"."+str(self.millis)
  def epoch_unix(self): 
    ret = 0
    try: 
      ret = int(self.hour)*3600000 + int(self.minute)*60000 + int(self.second) * 1000 + int(self.millis)
    except:
      print("Existe campos vazios na hora, minuto, segundo ou ms")
      ret = 0
    return ret
  def __eq__(self, other):
    return self.epoch_unix() == other.epoch_unix() 





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
path = path.replace('"', "")


bus = config['input']['pos_bus']
num_db = config['input']['num_path_db_peak']
db = {}

for i in range(1,int(num_db)+1):
    
    path_db = config['input']['path_db'+str(i)]
    path_db = path_db.replace('"', "")
    
    if path in path_db: 
      print("O path do ficheiro não pode ser o mesmo que o path do dbc")
      exit(1) 
    
    db[i] = cantools.database.load_file(path_db)
    print("HEY")
    print(db[i].messages)


#path_db3 = "/home/micron/sav/Trabalhos/2023-2024/FormulaStudent/Eletro2024/CanTrans/Orion_CANBUS_23-09.dbc"
dictionary = {
  "pos_hour": config['input']['pos_hour'],
  "pos_minute": config['input']['pos_minute'],
  "pos_second": config['input']['pos_second'],
  "pos_ms": config['input']['pos_ms'],
  "pos_id": config['input']['pos_id'],
  "pos_bytes": config['input']['pos_bytes'],
  "pos_bus": config['input']['pos_bus'],
  "delimiter": config['input']['delimiter']
}
oldtime = 0
# remove the "


#ceck if directory exists
if os.path.exists(path):
  #foreach file that exists 
  bufferFile = []
  for file in os.listdir(path):
    #print reading file xyz
    print("Reading file: "+file)
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
    hora = 0
    minuto = 0
    segundo = 0
    ms = 0
    for line in bufferFile:
      
      
      #split the line by ,
      fat = []
      #'dictionary["delimiter"]'
      fat = line.split(';')
      
      #print (fat)
      print("line"+str(fat))
      oldhora = hora
      oldminuto = minuto
      oldsegundo = segundo
      oldms = ms
      
      oldtime: timeframe = timeframe(oldhora, oldminuto, oldsegundo, oldms)
      
      hora = fat[int(dictionary["pos_hour"])]
      minuto = fat[int(dictionary["pos_minute"])]
      segundo = fat[int(dictionary["pos_second"])]
      ms = fat[int(dictionary["pos_ms"])]
      #lmao try wont even work here
      if (hora == minuto and minuto == segundo and segundo == ms ):
        # the time is formated in the following way hh:mm:ss.ms 
        # so we need to split it by : and .
        print("Chosen SINGLE column time format!!")
        time = fat[int(dictionary["pos_hour"])]
        time = time.split(":")
        hora = time[0]
        minuto = time[1]
        stime = time[2].split(".")
        
        segundo = stime[0]
        mstime = stime[1].split(dictionary["delimiter"])
        ms = mstime[0]
        
        print(hora+"h"+minuto+"m"+segundo+"s"+ms+"ms")
        
      
        
      newtime: timeframe = timeframe(hora, minuto, segundo, ms)
      
      bus = fat[int(dictionary["pos_bus"])]
      id_s = fat[int(dictionary["pos_id"])]
      byte_s = fat[int(dictionary["pos_bytes"]):]
      try:
        id_s = int(id_s,16)
        #convert string into hexadecimal integers
        byte_s = [int(x) for x in byte_s]
        byte_s = bytes(byte_s)
        print(int(bus))
        f = db[int(bus)].decode_message(id_s, byte_s)
        #add newtime onto todays date in ms epoch unix but at 00:00:00.000


        now = datetime.now()
        # Get the start of the day (midnight)
        start_of_day = datetime(now.year, now.month, now.day).timestamp()
        last_time_epoch = newtime.epoch_unix() + start_of_day*1000

        # convert last_time_epoch to datetime and print the year, month, day, hour, minute, second
      
        print(last_time_epoch)
        f['tp'] = last_time_epoch
        output.append(f)
      except IndexError as e:
        print("DBC em falta para o bus"+ int(bus))
      except ValueError as e:
        print("O id não é um hexadecimal")
        
        continue
    
      except:
        print("Erro Perdu (O perdu nao meteu o id no dbc(provavelmente))")
      #
    print("=========DONE==========")
    print("Output: "+str(output))
    turn_json_csv(output)
  
  
  
  
else:
  print("O diretório não existe, por favor cria um diretório com o nome: "+path)
  


