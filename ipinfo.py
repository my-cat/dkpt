
from urllib.request import urlopen
import json
import os
 
#Variable
url="http://ip.taobao.com/service/getIpInfo.php?ip="
#url1="http://www.ip138.com/ips.asp?ip="+s+"&action=2"
url2='http://tieba.baidu.com/'
#function
def ip_detail():
    data=urlopen(url+ip).read()
    datadict=json.loads(data.decode())
    print ("该IP的详细信息为:\n"+ "国家/地区："+ datadict["data"]["country"] + "/" + datadict["data"]["area"] +"\n省份：\t" + datadict["data"]["region"]+"\n城市:\t"+ datadict["data"]["city"]+"\n运营商：" + datadict["data"]["isp"])
#main
if __name__=="__main__":
  #  os.system("clear")
   # ip=input("input ip address>")
  #  data=urlopen(url2).read()
   # print (data)
  #  ip_detail()
    pass
