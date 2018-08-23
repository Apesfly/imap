import imaplib

class Account_Log(object):
    def __init__(self,account,keyword,poptype):
        self.__account = account
        self.__keyword = keyword
        self.poptype = poptype
        self.get_server()
    def get_server(self):
        try:
            self.server = imaplib.IMAP4_SSL(self.poptype)
            self.server.login(self.__account,self.__keyword)
            self.result = self.server.select()[0]
            print("%s Connected To The %s."%(self.result[:2],self.poptype) )
        except Exception as e:
            print("Connected to the %s error:\n%s."%(self.poptype,e) )

