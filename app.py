import requests, time, threading, json, sys
#import logging
from bs4 import BeautifulSoup
from bottle import route, run, template
from datetime import datetime


#logging.basicConfig(format = u'[%(asctime)s] %(levelname)-8s %(message)s', level = logging.DEBUG)

############### SERVER ###########
@route('/')
def index():
    return 'ok'
##################################

new_data = {}
old_data = {}
bot_token = "287489756:AAF9zKnbWxhEIeELVeCQcgJlwAhW2aIeReM"
telegraph_token = "d644cfbeda45f73c80b2503287d5bea27880a343de7a7c2abc8349efa9bd"


def signed(i):
    if (i>0):
        return "+"+str(i)
    else:
        return i


def strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result


def get_doctors():
    doctors = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 OPR/40.0.2308.90'}
    data = {'COMMAND': 1}
    r = requests.post("http://89.163.32.10/cgi-bin/tcgi1.exe", timeout=6, headers=headers, data=data)
    soup = BeautifulSoup(r.text.encode('latin1').decode('cp1251'), 'html.parser')

    for k in soup.find_all('button')[4:]:
        try:
            raw = k.span.string.split()
            if (raw[0] != "ТЕРАПЕВТ"):
                doctors[raw[0]] = raw[-1]
        except:
            pass
            #logging.error("Ошибка! Не удалось обработать врача.")

    #Смотрим конкретных докторов терапевтов.
    data['COMMAND'] = 10
    data['DIALOGSPECCOMMAND'] = 2
    data['CODESPEC'] = 3
    r = requests.post("http://89.163.32.10/cgi-bin/tcgi1.exe", timeout=6, headers=headers, data=data)
    soup = BeautifulSoup(r.text.encode('latin1').decode('cp1251'), 'html.parser')
    for k in soup.find_all('button')[4:-1]: # Три лишних кнопки, без кнопки "любой доктор"
        try:
            raw = k.span.string.split()
            doctors["Терапевт: "+raw[0]] = raw[-1]
        except:
            pass
            #logging.error("Ошибка! Не удалось обработать терапевта.")

    #logging.debug(doctors)
    return doctors

def serialize_page(d):
    content = [{"tag":"i","children":["последнее обновление в "+datetime.now().strftime('%H:%M %d.%m.%Y')]}]
    content.append({"tag": "hr"})
    for key in d:
        content.append({"tag": "p", "children": [key+": "+d[key]]})
    return json.dumps(content)

if __name__ == "__main__":

    threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=sys.argv[1])).start()

    old_data = requests.get("https://api.myjson.com/bins/nem6b").json()

    #logging.debug(old_data)

    print("Listener has been started.")
    while(1):
        new_data = get_doctors()
        send_body = {'text': '', 'chat_id':'-1001093298291'}
        for key in new_data:
            try:
                if   (old_data[key] == "НЕТ" and new_data[key] != "НЕТ") or (not hasattr(old_data, key) and hasattr(new_data, key)):
                    print("Появились талоны к врачу")
                    send_body['text'] = '🆕 Появились талоны к врачу!\n{} {} шт.'.format(key, new_data[key])
                    requests.get("https://api.telegram.org/bot{}/sendMessage".format(bot_token),
                                 params=send_body)
                elif (old_data[key] != "НЕТ" and new_data[key] == "НЕТ"):
                    print("Исчезли талоны к врачу ",key)
                    send_body['text'] = '{} - талоны закончились 😔'.format(key)
                    requests.get("https://api.telegram.org/bot{}/sendMessage".format(bot_token),
                                 params=send_body)
                elif (int(old_data[key]) < int(new_data[key])):
                    print("Изменились талоны к врачу ",key)
                    send_body['text'] = '{}, \n{} ➡️ {} ({})'.format(key, strike(old_data[key]), new_data[key], signed(int(new_data[key])-int(old_data[key])) )
                    requests.get("https://api.telegram.org/bot{}/sendMessage".format(bot_token),
                                 params=send_body)
            except:
                pass#logging.error("key error!")
            try:
                old_data[key] = new_data[key]
            except:
                old_data = get_doctors()

        x = json.dumps(new_data)
        r = requests.put("https://api.myjson.com/bins/nem6b", data=x, headers={'content-type':'application/json'})
        print(r.status_code)

        telegraph_data = {'access_token': telegraph_token, \
        'title': 'Быстрая сводка', \
        'author_name': '@p75spbru', \
        'content': serialize_page(new_data) \
        }

        r = requests.get("https://api.telegra.ph/editPage/Bystraya-svodka-03-19", params=telegraph_data)
        print(r.text)

        time.sleep(60)