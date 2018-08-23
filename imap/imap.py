from Login import Account_Log
import email
from email.header import decode_header
from email.utils import parseaddr
import re
import os
import base64
import quopri
class get_mail(object):  
    def __init__(self,account,keyword,poptype):
        self.server = Account_Log(account,keyword,poptype).server 
        self.msg = self.server.search(None,'All')[1][0].split()
        self.mails_number = len(self.msg)
        print('Total has %s mails.'%self.mails_number)
        self.start_at = self.mails_number
    def __ReadMail(self,index):
        onemail = self.server.fetch(str(index).encode(),'(RFC822)')[1][0][1]
        onemail = Decode_Mail(email.message_from_bytes(onemail))
        vital_imfo = onemail.get_content()    #[正文,Html信息,附件名称]
        basic_imfo = onemail.get_basic_imfo() #[主题,来信人,来信邮件,收信人,收信邮箱,发信日期]
        return basic_imfo,vital_imfo
    def get_mail(self,index):
        self.start_at = self.mails_number - index
        return __ReadMail(index)
    def get_nextmail(self,start = -1):
        if start != -1:
            self.start_at = self.mails_number - start + 1
        for num in range(self.start_at,0,-1):
            yield self.__ReadMail(num)
class Decode_Mail(object):
    def __init__(self,msg):
        self.msg = msg
        self.From = ''
        self.TO = ''
        #basic_imformation:[主题,来信人,来信邮件,收信人,收信邮箱,发信日期]
        self.Subject = ''
        self.From_Name = ''
        self.From_email = ''
        self.TO_Name = ''
        self.TO_email = ''
        self.Date = ''
        #vital_imformation:[正文,Html信息,附件名称]
        self.text = ''
        self.html = ''
        self.attacment_name = ''
        self.charset = 'utf-8'
    def get_basic_imfo(self): 
        self.Subject = self.msg.get('Subject')
        self.Subject = self.__decode_str__(self.Subject)
        self.TO = self.msg.get('To')
        self.TO_Name,self.TO_email = parseaddr(self.TO)
        self.TO_Name = self.__decode_str__(self.TO_Name)
        try:
            self.From = self.msg.get('From')
            self.From_Name,self.From_email = parseaddr(self.From)
        except Exception as e:
            msg_to_string = self.msg.as_string()  
            self.From = re.findall(re.compile(".*?From:.*?=\?(.*?)\?=\n"),msg_to_string)[0].split('?')[2]
            self.From = base64.b64decode(self.From).decode(self.charset)
            self.From_Name,self.From_email = parseaddr(self.From)
        self.From_Name = self.__decode_str__(self.From_Name)
        self.Date = self.msg.get('Date')
        self.From = self.__strip_same_imfo__(self.From_Name,self.From_email)
        self.TO = self.__strip_same_imfo__(self.TO_Name,self.TO_email)
        return [self.Subject,self.From,self.TO,self.Date]
    def __strip_same_imfo__(self,name,mail):
        name = name.strip(' ')
        mail = mail.strip(' ')
        if(name == mail):
            return name
        elif(name =='' or mail == ''):
            return name + mail
        else:
            return name + ',' + mail
    def get_content(self):
        self.__get_content__(self.msg)
        return [self.text,self.html,self.attacment_name]
    def __get_content__(self,part):
        if(part.is_multipart()):
            for m in part.get_payload():
                self.__get_content__(m)
        else:
            content_type = part.get_content_type()
            try:
                cheak_content_type = part._headers[0][0]#检查是否有用,或符合标准
                if(cheak_content_type == 'Content-Type'):
                    if(content_type == 'text/plain'):
                        charset = self.__find_charset__(part)
                        self.text = part.get_payload(decode = True)
                        self.text = self.text.decode(charset,'ignore')
                    elif(content_type == 'text/html'):
                        charset = self.__find_charset__(part)
                        self.html = part.get_payload(decode = True)
                        self.html = self.html.decode(charset)
                    else:
                        cheak_content_disposition = part._headers[1][0] #检查是否为附件,或符合标准
                        if(cheak_content_disposition == 'Content-Disposition'):
                            self.attacment = part.get_payload(decode = True)
                            self.attacment_name = self.__find_filename__(part)
                            down_attact(self.attacment,self.attacment_name)
            except Exception as e:
                print(e)
    def __find_charset__(self,part):
        patt1 = re.compile('(charset=|charset = )(.*?)$')
        patt2 = re.compile('(charset=|charset = )(.*?);')
        content_type = part.get('Content-Type', '').lower()
        charset = re.findall(patt2,content_type)
        if charset == []:
            charset = re.findall(patt1,content_type)
        return charset[0][1].strip('\"')
    def __find_filename__(self,part):
        patt1 = re.compile('.*?filename=(.*?)$')
        patt2 = re.compile('(=\?.*?\?.*?\?.*?\?=)')
        content_type = part.get('Content-Disposition', '')
        try:
            attacmentname = re.findall(patt1,content_type)[0].strip('\"')
            attacmentname = self.__decode_str__(attacmentname)
        except:#'attachment; \r\n\tfilename="=?GBK?Q?=C8=CB=C0=E0=BC=F2=CA=B7=A3=BA?=\r\n =?GBK?Q?=B4=D3=B6=AF=CE=EF=B5=BD=C9=CF=B5=DB?=\r\n =?GBK?Q?_=28=BF=AA=B7=C5=C0=FA=CA=B7=CF=B5=C1=D0=29_-?=\r\n =?GBK?Q?_Yuval_Noah_Harari=2Emobi?="'
            results = re.findall(patt2,content_type)
            attacmentname = ''
            for k in results:
                attacmentname += self.__decode_str__(k)
        return attacmentname 
    def __decode_str__(self,s):
        value,charset = decode_header(s)[0]
        try:
            if charset:
                value = value.decode(charset)
                self.charset = charset
                return value
        except Exception as e:
            value = value.decode('utf-8','ignore')
            return value
        return value
def down_attact(message,file_name):
    Invaild_Symbol = ['\\','/',':','?','\"','<','>','?']
    for i in Invaild_Symbol:
        if(i in file_name):
            file_name = file_name.replace(i,'')
    path = os.getcwd() + '/' + file_name
    with open(path,'wb') as f:
        f.write(message)
account = ''#'xxxxxx@qq.com'
keyword = ''
poptype = 'imap.163.com'
x = get_mail(account,keyword,poptype)
k = 0
for i in x.get_nextmail(1):
    k += 1
    basic = i[0]
    vital = i[1]
    text = vital[0]
    html = vital[1]
    ataccmentname = vital[2] 
    print("序号:{}\n".format(k))
    for basic_f in basic:
        print(basic_f)
    print(text)
    print(ataccmentname)
    if (k % 50 == 0):
        x.server.noop()
    #for vital_f in vital:
        #print(vital_f)
