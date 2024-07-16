#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import re
from urllib import request, parse
import urllib
import urllib.request
class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "好趣网"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"中央台": "1",
			'卫视频道':'2',
			'省市级电视台':'3',
			'港澳台频道':'4',
			'外国电视台':'5',
			'体育频道':'sports',
			'综艺频道':'zongyi',
			'新闻频道':'xinwen',
			'影视频道':'yingshi',
			'少儿频道':'shaoer',
			'财经频道':'caijing'
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		url='http://tv.haoqu99.com/1/'
		HtmlTxt=self.custom_webReadFile(urlStr=url,codeName='gbk')
		element = self.html(HtmlTxt)
		aList = element.xpath("//a[@class='thumb-outer']")
		videos = self.custom_list(aList)
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		Province=''
		if 'Province' in extend.keys():
				Province=extend['Province']
		Url='http://tv.haoqu99.com/{0}/'.format(tid)
		if tid=='tv':
			Url='http://tv.haoqu99.com/{0}/index_{1}.html'.format(tid,pg)
		elif tid.isdigit()==False:
			Url='http://tv.haoqu99.com/zhibo/{0}/'.format(tid)
		elif tid=='3' and Province!='':
			Url='http://tv.haoqu99.com/{0}/{1}/'.format(tid,Province)
		HtmlTxt=self.custom_webReadFile(urlStr=Url,codeName='gbk')
		element = self.html(HtmlTxt)
		aList = element.xpath("//a[@class='thumb-outer']" if tid!='tv' else "//ul[@class='tvlist']/li/a")
		pagecount=self.custom_RegexGetText(Text=HtmlTxt,RegexText=r'<a href="index_([0-9]+?).html">尾页</a>',Index=1) if tid=='tv' else '1'
		videos = self.custom_list(aList,tid)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 1 if pagecount.isdigit()==False else int(pagecount)
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		result = {}
		aid = array[0].split('###')
		logo = aid[2]
		url = aid[1]
		title = aid[0]
		vodItems=[]
		vod_play_from=['鸟叔精选线路',]
		vod_play_url=[]
		HtmlTxt=self.custom_webReadFile(urlStr=url,codeName='gbk')
		element = self.html(HtmlTxt)
		nodes = element.xpath("//ul[@class='tab-list-syb']/li")
		if len(nodes)>0:
			joinStr = "#".join(self.custom_EpisodesList(nodes=nodes))
			vodItems.append(joinStr)
			vod_play_url = "$$$".join(vodItems)
		else:
			vod_play_url = "$$$".join([])
		nodes = element.xpath("//div[@class='drop-panel']/p/img")
		content=self.custom_RegexGetText(Text=HtmlTxt,RegexText=r'<div class="drop-panel"><p>(.+?)</div>')
		type_name=self.custom_RegexGetText(Text=HtmlTxt,RegexText=r'首页</a>&nbsp;>&nbsp;<a href=".+?"(.+?)</a><span class="arrow">')
		try:
			if len(nodes)>0 and aid[2]=='http://photo.16pic.com/00/23/48/16pic_2348904_b.jpg':
				logo=nodes[0].xpath('./@src')[0]
				title=nodes[0].xpath('./@alt')[0]
				array[0]="{0}###{1}###{2}".format(title,url,logo)
		except:
			pass
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":self.custom_removeHtml(type_name),
			"vod_year":"",
			"vod_area":"",
			"vod_remarks":"",
			"vod_actor":"",
			"vod_director":"鸟叔精选",
			"vod_content":self.custom_removeHtml(content)
		}
		vod['vod_play_from'] =  "$$$".join(vod_play_from)
		vod['vod_play_url'] = vod_play_url
		result = {
			'list':[
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		url='http://tv.haoqu99.com/e/sch/?keyboard={0}'.format(urllib.parse.quote(key.encode('gbk')))
		HtmlTxt=self.custom_webReadFile(urlStr=url,codeName='gbk')
		# element = self.html(HtmlTxt)
		# aList = element.xpath("//a[@class='l']")
		videos=self.custom_list_search(HtmlTxt)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		#http://tv.haoqu99.com/e/extend/tv.php?id=34433
		parse=1
		if id.isdigit():
			url='http://tv.haoqu99.com/e/extend/tv.php?id={0}'.format(id)
			HtmlTxt=self.custom_webReadFile(urlStr=url,codeName='gbk')
			temporary=self.custom_RegexGetTextLine(Text=HtmlTxt,RegexText=r'[\$|"]([a-zA-z]+://[^\s|^"]*)[\$|"]',Index=1)
			# print(temporary)
			m3u8=''
			for v in temporary:
				# print(v+'===')
				if self.custom_RegexGetText(Text=v,RegexText=r'(\.m3u8|rtmp:|\.mp4|\.ts|\.flv)')!='':#如果有其它格式源可以加
					m3u8=v
					break
			if m3u8!='':
				id=m3u8
				parse=0
			else:
				id=url
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = id
		result['jx'] = 0#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result

	config = {
		"player": {},
		"filter": {
		"3":[
		{"key":"Province","name":"地方:","value":[{"n":"默认","v":""},{"n":"广东","v":"guangdong"},{"n":"湖南","v":"hunan"},{"n":"江苏","v":"jiangsu"},{"n":"安徽","v":"anhui"},{"n":"浙江","v":"zhejiang"},{"n":"北京","v":"beijing"},{"n":"辽宁","v":"liaoning"},{"n":"江西","v":"jiangxi"},{"n":"山东","v":"shandong"},{"n":"黑龙江","v":"heilongjiang"},{"n":"上海","v":"shanghai"},{"n":"云南","v":"yunnan"},{"n":"四川","v":"sichuan"},{"n":"河南","v":"henan"},{"n":"湖北","v":"hubei"},{"n":"福建","v":"fujian"},{"n":"重庆","v":"zhongqing"},{"n":"河北","v":"hebei"},{"n":"吉林","v":"jilin"},{"n":"广西","v":"guangxi"},{"n":"山西","v":"shan-xi"},{"n":"陕西","v":"shanxi"},{"n":"宁夏","v":"ningxia"},{"n":"海南","v":"hainan"},{"n":"甘肃","v":"gansu"},{"n":"新疆","v":"xinjiang"},{"n":"内蒙古","v":"neimenggu"},{"n":"天津","v":"tianjin"},{"n":"贵州","v":"guizhou"},{"n":"青海","v":"qinghai"},{"n":"西藏","v":"xizang"}]}
		]}
		}
	header = {}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
		#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index=1):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	#分类取结果
	def custom_list(self,aList,tid='0'):
		videos = []
		head="http://tv.haoqu99.com"
		for a in aList:
			url=a.xpath("./@href")[0]
			title=a.xpath('./@title' if url.find('/tv/')>-1 else './img/@alt')[0]
			img=a.xpath('./p/img/@src' if url.find('/tv/')>-1 else './img/@src')[0]
			if tid=='sports' and self.custom_RegexGetText(Text=title, RegexText=r'(CCTV)')=='':
				continue
			if tid=='1' and (self.custom_RegexGetText(title,'(CCTV[0-9]{1,2})')=='' or self.custom_RegexGetText(title,'(CCTV4K|洲)')!=''):
				continue
			if url.find('://')<1:
				url=head+url
			if img.find('://')<1:
				img=head+img
			vod_id="{0}###{1}###{2}".format(title,url,img)
			videos.append({
				"vod_id":vod_id,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":title
			})
		if tid=='1':
			videos.sort(key=self.takeSecond)
		return videos
	def takeSecond(self,elem):
		identifying=elem['vod_remarks']
		tem=self.custom_RegexGetTextLine(identifying,'([0-9]+?)')
		if len(tem)==1:
			identifying=identifying.replace(tem[0],'0'+tem[0])
		return identifying
		#访问网页
	def custom_webReadFile(self,urlStr,header=None,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		# import ssl
		# ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName)
		return html
	#取集数
	def custom_EpisodesList(self,nodes):
		videos = []
		for vod in nodes:
			title =vod.xpath("./span/text()")[0]
			url = vod.xpath("./@data-player")[0]
			if len(url) == 0 or title.find('站外')>-1:
				continue
			videos.append(title+"$"+url)
		# print('共:'+str(len(videos)))
		return videos
	def custom_list_search(self,html):
		videos = []
		head="http://tv.haoqu99.com"
		patternTxt=r'<a class="l" href="(.+?)" target="_blank">(.+?)</a>'
		pattern = re.compile(patternTxt)
		ListRe=pattern.findall(html)
		img='http://photo.16pic.com/00/23/48/16pic_2348904_b.jpg'
		for vod in ListRe:
			url =vod[0]
			title =self.custom_removeHtml(vod[1])
			if url.find('/tv')>-1:
				continue
			if url.find('://')<1:
				url=head+url
			videos.append({
				"vod_id":"{0}###{1}###{2}".format(title,url,img),
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		return videos
	#正则取文本,返回数组	
	def custom_RegexGetTextLine(self,Text,RegexText,Index=1):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	#删除html标签
	def custom_removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	