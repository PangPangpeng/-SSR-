# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 11:13:35 2018

@author: zhukw
"""

#自动获取github上面的ssr账号和密码
#曾尝试直接获取github上面图片的地址，让百度识别，结果失败
#折中的办法就是先下载到本地，然后再编码进行识别

import urllib,urllib2
import json
import base64
import re
#此处填写自己百度ocr的APPid
#百度ocr：http://ai.baidu.com/tech/ocr/general
client_id="jOVWVXfp4NUdRLvNFuv32ihB"
client_secret="EiGIs95WGU5aEdkfx4fwKOz0GODoGGdp"

#此函数用来获取github上面写着地址的图片
def get_message_picture_url():
    host="https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
    page=urllib2.urlopen(host)
    html=page.read()
    #python的re模块并不支持变长的后发断言，用这条表达式会出现错误
    #reg= '(?<=<(img|IMG)[^>]*?src=").*?(?=")'
    reg='(?<=img src=").*?(?=")'
    imgre = re.compile(reg)
    imglist=re.findall(imgre,html)
    return imglist[len(imglist)-1]
#此函数获得百度OCR的access_token
def get_access_token(client_id,client_secret):
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='
    host=host+client_id+'&client_secret='
    host=host+client_secret
    
    request = urllib2.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib2.urlopen(request)
    content = response.read()
    if (content):
        results=json.loads(content)
        return results.get("access_token")
#此函数用来向百度发送文字识别请求，并且获得识别结果
def send_Pic2word_request(b64file,access_token):
    host="https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token="
    host+=access_token
    data={'image':b64file}
    body=urllib.urlencode(data)  
    request=urllib2.Request(host,body)
    request.add_header('Content-Type','application/x-www-form-urlencoded')
    response=urllib2.urlopen(request)
    content = response.read()
    if (content):
        results=json.loads(content)
        return results.get("words_result")
#检查识别之后的method，使其正确
def check_method(method):
    if method.find("no")>=0:
        return "none"
    elif method.find("128")>=0:
        if method.find("CTR")>=0:
            return "aes-128-ctr"
        return "aes-128-cfb"
    elif method.find("192")>=0:
         if method.find("CTR")>=0:
            return "aes-192-ctr"
         return "aes-192-cfb"
    elif method.find("256")>=0:
        if method.find("CTR")>=0:
            return "aes-256-ctr"
        return "aes-256-cfb"
    elif method.find("rc4")>=0:
        if method.find("md5")>=0:
            if method.find("6")>=0:
                return "rc4-md5-6"
            return "rc4-md5"
        return "rc4"
    elif method.find("salsa")>=0:
        return "salsa20"
    elif method.find("chacha")>=0:
        if method.find("ietf")>=0:
            return "chacha20-ietf"
        return "chacha20"
    else:
        return "none"

#检查识别之后的protocol使其正确
def check_protocol(protocol):
    if protocol.find("ori")>=0:
        return "origin"
    elif protocol.find("verify")>=0:
        return "verify_deflate"
    elif protocol.find("auth")==0:
        if protocol.endswith("4"):
            return "auth_sha1_v4"
        elif protocol.endswith("md5"):
            return "auth_aes128_md5"
        elif protocol.endswith("sha1"):
            return "auth_aes128_sha1"
        elif protocol.endswith("a"):
            return "auth_chain_a"
        else:
            return "auth_chain_b"

#检查识别之后的"混淆"使其正确     
def check_obfs(obfs):
    if obfs.startswith("p"):
        return "plain"
    elif obfs.startswith("http"):
        if obfs.endswith("simple"):
            return "http_simple"
        else:
            return "http_post"
    elif obfs.startswith("random"):
        return "random_head"
    elif obfs.startswith("tls1.2"):
        if obfs.find("fast")>=0:
            return "tls1.2_ticket_fastauth"
        else:
            return "tls1.2_ticket_auth"

#检查识别之后的密码。一般就是两个很简单
def check_passwd(passwd):
    if passwd.startswith("dong"):
        return "dongtaiwang.com"
    else:
        return "ntdtv.com"
        
#此函数将识别结果中的内容调整为list(dict)的形式，使自动填写更为方便
#因为有的汉字识别错误，所以需要进行人工修正
def words_parse_head(words):
    loop_times=len(words)/2
    server_list=[]
    for i in range(0,loop_times):
        str1=words[2*i].get('words')
        str2=words[2*i+1].get('words')
        str1=str1.replace(" ","")
        str2=str2.replace(" ","")
        #使用正则表达式匹配字符串，有点奇怪，有好的意见可以发个issue给我 XXXD
        reg1=u'(?<=:)[^\:]+(?=端|密|$)'
        reg1_ipv6=u'(?<=:)[^\:]+(?=密|$)'
        reg2=u'(?<=:)[^\:]+(?=协|混|$)'
        if str1.find("ipv6")>0:
            compilled_reg = re.compile(reg1_ipv6)
            server_ip=str1[str1.find(":")+1:str1.find(u"端口")]
            temp_list=re.findall(compilled_reg,str1)
            server_port=temp_list[0]
            server_passwd=check_passwd(temp_list[1])
        else:
            compilled_reg = re.compile(reg1)
            temp_list=re.findall(compilled_reg,str1)
            server_ip=temp_list[0]
            server_port=temp_list[1]
            server_passwd=check_passwd(temp_list[2])
        
        compilled_reg = re.compile(reg2)
        temp_list=re.findall(compilled_reg,str2)
        server_method=check_method(temp_list[0])
        server_proto=check_protocol(temp_list[1])
        server_obfuse=check_obfs(temp_list[2])
        dict_temp={"server":server_ip,"server_port":server_port,"password":server_passwd,"method":server_method,"protocol":server_proto,"obfs":server_obfuse}
        server_list.append(dict_temp)
    return server_list

#将获得的服务列表写成配置文件，同时纠正一些文字识别的错误
def write_config(list_servers):
    f=open("gui-config.json",'rb')
    dicts=json.load(f)
    f.close()
    dicts.pop("configs")
    dicts["configs"]=list_servers
    f=open("gui-config.json",'w')
    f.write(json.dumps(dicts))
    f.close()
    
if __name__ == "__main__":
    get_message_picture=urllib2.urlopen(get_message_picture_url())
    print "get picture done!"
    pic=get_message_picture.read()
    pic_encoded=base64.b64encode(pic)
    Access_Token=get_access_token(client_id,client_secret)
    print "start recognize!"
    get_word=send_Pic2word_request(pic_encoded,Access_Token)
    print "recogenize done!"
    list_servers=words_parse_head(get_word)
    print "start config!"
    write_config(list_servers)
    print "config done!"