# -*- coding: utf-8 -*- 
# @Author:围观的白菜哥哥 
import requests
import datetime
import threading
import sys
import random
import time
import execjs
url_bookCab="http://cabinet.ujn.edu.cn/bookCab"
url_getCabIds="http://cabinet.ujn.edu.cn/getCabIds"
url_getCabInfo="http://cabinet.ujn.edu.cn/getCabInfo"
url_renew="http://cabinet.ujn.edu.cn/renew"  
url_login="http://cabinet.ujn.edu.cn/"


#开始的序号和结束的序号
start_num=4400
end_num=4700
#多线程间隔，太快会被认为dos
time_interval=0.3

dict = {
'test':{'name':"test","id":"123456","pwd":"123456","cookie":""},
'test1':{'name':"tset1","id":"2016","pwd":"","cookie":""},
}

#加载当前目录下的des.js 
def get_js(): 
	with open("./des.js", 'r', encoding='UTF-8')  as f:
		# line = f.readline()  
		# htmlstr = ''  
		# while line:  
		# 	htmlstr = htmlstr + line  
		# 	line = f.readline()
		htmlstr=f.read()  
	return htmlstr

#存储着des.js对象，每次都读800行太费劲，只让他读一次
jsstr=get_js()

#加载js文件，获取名字叫做rsa的密文,实际上是DES
#看到注释觉得可能以前学校用的是rsa，后来改为des，rsa的参数这个名字就没改
def get_rsa(user,pwd,lt):
	 
	ctx = execjs.compile(jsstr)  
	rsa=ctx.call('strEnc',user+pwd+lt,'1','2','3')
	return rsa

def get_header_(name):
	header={
    'Host': 'cabinet.ujn.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://cabinet.ujn.edu.cn/',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '40',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': 'JSESSIONID='+dict[name]['cookie']+'',
}
	return header

def get_header(cookie=""):
	header={
	'Host': 'sso.ujn.edu.cn',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': 'http://cabinet.ujn.edu.cn/',
	'DNT':"1",
	'Connection': 'keep-alive',
	'Referer': 'http://sso.ujn.edu.cn/tpass/login?service=http://cabinet.ujn.edu.cn/',
	"Content-Type":"application/x-www-form-urlencoded",
	'Cookie':'JSESSIONID='+cookie,
}
	return header
#绕过前端加密，返回cookie值
def get_cookie(user,pwd,i):

	#首先获取第一个cookie
	res=requests.get(url_login,headers=get_header())
	cookie_first=res.cookies.get_dict()['JSESSIONID']
	#获取lt的值
	res=res.text
	flag=res.index('value="LT')
	lt=res[flag+7:flag+53]
	#获取execution的值
	flag=res.index('execution" value="')
	execution=res[flag+18:flag+22]
	#得到rsa的值
	rsa=get_rsa(user,pwd,lt)
	#提交rsa,ul,pl,execution,_eventId,ul学号长度，pl密码长度
	#302跳转，用allow_redirects=False处理下一个跳转的页面
	res_post302=requests.post("http://sso.ujn.edu.cn/tpass/login?service=http://cabinet.ujn.edu.cn/",data={"rsa":rsa,"ul":len(user),"pl":len(pwd),"lt":lt,"execution":execution,"_eventId":"submit"},headers=get_header(cookie_first),allow_redirects=False)
	#获取location,访问是一个get形的302跳转,这个get302的header里面有个set_cookie字段可以获得cookie
	res_get302=requests.get(res_post302.headers["Location"],allow_redirects=False)
	#print(requests.get(res_post302.headers["Location"]).text)
	#print(res_get302.headers['location'])
	res_final=requests.get(res_get302.headers['location'])
	cookie=res_get302.headers['location'][38:70]
	dict[i]['cookie']=cookie
	return cookie

#把cookie存dict里面，这登陆起来太慢了，获得cookie之后让他一直不停的发。
def store_cookie():
	for i in dict:
		t = threading.Thread(target=get_cookie, args=(dict[i]['id'],dict[i]['pwd'],i))
		t.start()
		time.sleep(time_interval)
		# cookie=get_cookie(dict[i]['id'],dict[i]['pwd'])
		# print(cookie)
		# dict[i]['cookie']=cookie

#直接预约座位
def bookcab(cabid,name):
#有个人想要七楼
	if(name=="moujiawen1"):
		num=7000+random.randint(0,500)
		res_bookCab=requests.post(url_bookCab,data={"cabId":7000+random.randint(0,500)},headers=get_header_(name))
		res=res_bookCab.text.encode('utf-8').decode('utf-8')
		print(name+":"+str(num)+res)
	else:
		res_bookCab=requests.post(url_bookCab,data={"cabId":cabid},headers=get_header_(name))
		res=res_bookCab.text.encode('utf-8').decode('utf-8')
		print(name+":"+str(cabid)+res)

#顺序抢
def start():
	for  cab in range(start_num,end_num,len(dict)):
		for user in dict:
			cab=cab+1
			t = threading.Thread(target=bookcab, args=(cab,user))
			t.start()
			time.sleep(time_interval)

#随机抢,名字与模块冲突
def random_():
	for  cab in range(0,100):
		for user in dict:
			t = threading.Thread(target=bookcab, args=(random.randint(4,7)*1000+random.randint(0,500),user))
			t.start()
			t.join()
#输出dict
def out():
	flag=0
	for i in dict:
	
			if dict[i]['cookie']=="":
				print(dict[i]['name']+"登陆失败")
				flag=flag+1
	if flag==0:
		print("\n全部登陆成功\n")

			

def main():
	
	while True:
		print('****************************************************************************************************')
		print("1:一键登陆")
		print("2:顺序抢柜子")
		print("3:随机抢")
		print("4:查看登陆状态")
		func = input("input:\n")
		func=(str(func))
		if(func=='1'):
			store_cookie()
		if(func=='2'):
			start()
		if(func=='3'):
			random_()
		if(func=='4'):
			out()
	
if __name__ == '__main__':
	main()