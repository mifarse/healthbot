import requests, time, logging
from bs4 import BeautifulSoup

logging.basicConfig(format = u'[%(asctime)s] %(levelname)-8s %(message)s', level = logging.DEBUG)

new_data = {}
old_data = {}

def signed(i):
    if (i>0):
        return "+"+str(i)
    else:
        return i

def get_doctors():
    doctors = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 OPR/40.0.2308.90'}
    data = {'COMMAND': 1}
    r = requests.post("http://p75.spb.ru/cgi-bin/tcgi1.exe", headers=headers, data=data)
    soup = BeautifulSoup(r.text.encode('latin1').decode('cp1251'), 'html.parser')

    for k in soup.find_all('button')[4:]:
        try:
            raw = k.span.string.split()
            if (raw[0] != "ТЕРАПЕВТ"):
                doctors[raw[0]] = raw[-1]
        except:
            logging.error("Ошибка! Не удалось обработать врача.")

    #Смотрим конкретных докторов терапевтов.
    data['COMMAND'] = 10
    data['DIALOGSPECCOMMAND'] = 2
    data['CODESPEC'] = 3
    r = requests.post("http://p75.spb.ru/cgi-bin/tcgi1.exe", headers=headers, data=data)
    soup = BeautifulSoup(r.text.encode('latin1').decode('cp1251'), 'html.parser')
    for k in soup.find_all('button')[4:-1]: # Три лишних кнопки, без кнопки "любой доктор"
        try:
            raw = k.span.string.split()
            doctors["Терапевт: "+raw[0]] = raw[-1]
        except:
            logging.error("Ошибка! Не удалось обработать терапевта.")
    
    #print(doctors)
    logging.debug(doctors)
    return doctors

old_data = get_doctors()
print("Listener has been started.")
while(1):
    new_data = get_doctors()
    send_body = {'text': '', 'chat_id':'@p75talony'}
    for key in new_data:
        try:
            if   (old_data[key] == "НЕТ" and new_data[key] != "НЕТ"):
                logging.debug("Появились талоны к врачу ",key)
                send_body['text'] = 'Появились талоны к врачу!\n {} {} шт.'.format(key, new_data[key])
                requests.get("https://api.telegram.org/bot287489756:AAHUDL_e_MRtkgKyK5IMyJFtYPTPzzbJ3tI/sendMessage",
                             params=send_body)
            elif (old_data[key] != "НЕТ" and new_data[key] == "НЕТ"):
                logging.debug("Исчезли талоны к врачу ",key)
                send_body['text'] = '{} - талоны закончились :('.format(key)
                requests.get("https://api.telegram.org/bot287489756:AAHUDL_e_MRtkgKyK5IMyJFtYPTPzzbJ3tI/sendMessage",
                             params=send_body)
            elif (old_data[key] != new_data[key]):
                logging.debug("Изменились талоны к врачу ",key)
                send_body['text'] = '{}, \nосталось {} ({})'.format(key, new_data[key], signed(int(new_data[key])-int(old_data[key])) )
                requests.get("https://api.telegram.org/bot287489756:AAHUDL_e_MRtkgKyK5IMyJFtYPTPzzbJ3tI/sendMessage",
                             params=send_body)
        except:
            logging.error("key error!")
        try:
            old_data[key] = new_data[key]
        except:
            old_data = get_doctors()
    time.sleep(5)
