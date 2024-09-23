import cantools
import configparser
import pandas as pd
import os
import numpy
import datetime

class timeframe:
  def __init__(self, hour, minute, second, millis):
    self.hour = hour
    self.minute = minute
    self.second = second
    self.millis = millis
def fix_time (timeframe_new: timeframe, timeframe_old: timeframe):
  try: 
    #python wont catch this exception for some fucking reason so i had to do this ugly ass code
    
    timeframe_new.hour = int(timeframe_new.hour)
    timeframe_new.minute = int(timeframe_new.minute)
    timeframe_new.second = int(timeframe_new.second)
    timeframe_new.millis = int(timeframe_new.millis)
  except:
    timeframe_new.hour = 0
    timeframe_new.minute = 0 
    timeframe_new.second = 0
    timeframe_new.millis = 0
    #if (type(timeframe_new.hour) == str):
    #  timeframe_new.hour=timeframe_old.hour+"?"
      
    #if(type(timeframe_new.minute) == str):
    #  timeframe_new.minute =timeframe_old.minute+"?"
    
    #if(type(timeframe_new.second) == str):
    #  timeframe_new.secondhhpw=timeframe_old.second+"?"
    
    #if(type(timeframe_new.millis) == str):
    #  timeframe_new.millis=timeframe_old.millis+"?"
  return timeframe_new

def time_squash_perdu (hour, minute, second, millis):
  return str(hour)+":"+str(minute)+":"+str(second)+"."+str(millis)



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
path_db = config['input']['path_db']
path_db = path_db.replace('"', "")
bus = config['input']['pos_bus']
db = cantools.database.load_file(path_db)

if path in path_db: 
  print("O path do ficheiro não pode ser o mesmo que o path do dbc")
  exit(1) 

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
      newtime = fix_time(newtime, oldtime)
      bus = fat[int(dictionary["pos_bus"])]
      id_s = fat[int(dictionary["pos_id"])]
      byte_s = fat[int(dictionary["pos_bytes"]):]
      try:
        id_s = int(id_s)
        #convert string into hexadecimal integers
        byte_s = [int(x) for x in byte_s]
        byte_s = bytes(byte_s)
        
        f = db.decode_message(id_s, byte_s)
      
        #time = time_squash_perdu(hora, minuto, segundo, ms)
        #print ("timestamp da linha"+time)
        #f["timestamp"] = time 
        output.append(f)
        
      except ValueError as e:
        print("O id não é um hexadecimal"+e.args)
        
        continue
    
      except:
        print("Erro Perdu (O perdu nao meteu o id no dbc(provavelmente))")
      #
    print("=========DONE==========")
    
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
  


