#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import re
from urllib import request, parse
import urllib
import urllib.request
from xml.etree.ElementTree import fromstring, ElementTree as et

class Spider(Spider):  # 元类 默认的元类 type
	def getName():
		return "高清资源"#除去少儿不宜的内容
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual ={
			'动作片':'5',
			'喜剧片':'6',
			'爱情片':'7',
			'科幻片':'8',
			'恐怖片':'9',
			'剧情片':'10',
			'战争片':'11',
			'国产剧':'12',
			'台湾剧':'13',
			'韩国剧':'14',
			'欧美剧':'15',
			'香港剧':'16',
			'泰国剧':'17',
			'日本剧':'18',
			'记录片':'20',
			'动画片':'41',
			'海外剧':'54',
			'大陆综艺':'62',
			'港台综艺':'63',
			'日韩综艺':'64',
			'欧美综艺':'65',
			'国产动漫':'66',
			'日韩动漫':'67',
			'欧美动漫':'68',
			'港台动漫':'69',
			
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
		xmlTxt=self.custom_webReadFile(urlStr='https://api.1080zyku.com/inc/api.php?ac=list&h=24')
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		listXml=root.iter('list')
		videos = self.custom_list(html=listXml)
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		pagecount=1
		limit=20
		total=9999
		Url='https://api.1080zyku.com/inc/api.php?ac=list&t={0}&pg={1}'.format(tid,pg)
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		listXml=root.iter('list')
		for vod in listXml:
			pagecount=vod.attrib['pagecount']
			limit=vod.attrib['pagesize']
			total=vod.attrib['recordcount']
		videos = self.custom_list(html=root.iter('list'))
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pagecount
		result['limit'] = limit
		result['total'] = total
		return result
	def detailContent(self,array):
		result = {}
		aid = array[0].split('###')
		id=aid[1]
		logo = aid[2]
		title = aid[0]
		vod_play_from=['1080zyk',]
		vod_year=''
		vod_actor=''
		vod_content=''
		vod_director=''
		type_name=''
		vod_area=''
		vod_lang=''
		vodItems=[]
		vod_play_url=[]
		try:
			url='https://api.1080zyku.com/inc/apijson.php?ac=detail&ids='+id
			xmlTxt=self.custom_webReadFile(urlStr=url)
			jRoot = json.loads(xmlTxt)
			if jRoot['code']!=1:
				return result
			jsonList=jRoot['list']
			for vod in jsonList:
				vodItems=self.custom_EpisodesList(vod['vod_play_url'])
				joinStr = "#".join(vodItems)
				vod_play_url.append(joinStr)
				vod_year=vod['vod_year']
				vod_actor=str(vod['vod_actor'])
				vod_content=vod['vod_content']
				vod_director=str(vod['vod_director'])
				type_name=str(vod['type_name'])
				vod_area=str(vod['vod_area'])
		except :
			pass
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":type_name,
			"vod_year":vod_year,
			"vod_area":vod_area,
			"vod_remarks":vod_lang,
			"vod_actor":vod_actor,
			"vod_director":vod_director,
			"vod_content":vod_content
		}
		vod['vod_play_from'] =  "$$$".join(vod_play_from)
		vod['vod_play_url'] = "$$$".join(vod_play_url)
		result = {
			'list':[
				vod
			]
		}
		if self.custom_RegexGetText(Text=type_name,RegexText=r'(伦理|倫理|福利)',Index=1)!='':
			result={'list':[]}
		return result

	def searchContent(self,key,quick):
		Url='https://api.1080zyku.com/inc/api.php?ac=list&wd={0}&pg={1}'.format(urllib.parse.quote(key),'1')
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		listXml=root.iter('list')
		videos = self.custom_list(html=listXml)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		result["parse"] = 0#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = id
		result['jx'] = 0#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result


	config = {
		"player": {},
		"filter": {}
		}
	header = {}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
		#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	#分类取结果
	def custom_list(self,html):
		ListRe=html
		videos = []
		temporary=[]
		for vod in ListRe:
			for value in vod:
				for x in value:
					if x.tag=='name':
						title=x.text
					if x.tag=='id':
						id=x.text
					if x.tag=='type':
						tid=x.text
					if x.tag=='last':
						last=x.text
				temporary.append({
					"name":title,
					"id":id,
					"last":last
					})
		if len(temporary)>0:
			idTxt=''
			for vod in temporary:
				idTxt=idTxt+vod['id']+','
			if len(idTxt)>1:
				idTxt=idTxt[0:-1]
				url='https://api.1080zyku.com/inc/apijson.php?ac=detail&ids='+idTxt
				xmlTxt=self.custom_webReadFile(urlStr=url)
				jRoot = json.loads(xmlTxt)
				if jRoot['code']!=1:
					return videos
				jsonList=jRoot['list']
				for vod in jsonList:
					title=vod['vod_name']
					vod_id=vod['vod_id']
					img=vod['vod_pic']
					remarks=vod['vod_remarks']
					type_name=vod['type_name']
					vod_year=vod['vod_year']
					if self.custom_RegexGetText(Text=type_name,RegexText=r'(伦理|倫理|福利)',Index=1)!='':
						continue
					vod_id='{0}###{1}###{2}'.format(title,vod_id,img)
					# vod_id='{0}###{1}###{2}###{3}###{4}###{5}###{6}###{7}###{8}###{9}###{10}'.format(title,vod_id,img,vod_actor,vod_director,'/'.join(type_name),'/'.join(vod_time),'/'.join(vod_area),vod_lang,vod_content,vod_play_url)					
					# print(vod_id)
					videos.append({
						"vod_id":vod_id,
						"vod_name":title,
						"vod_pic":img,
						"vod_year":vod_year,
						"vod_remarks":remarks
					})
		return videos
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
	
	#取剧集区
	def custom_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit	
	#正则取文本,返回数组	
	def custom_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	#取集数
	def custom_EpisodesList(self,html):
		ListRe=html.split('#')
		videos = []
		for vod in ListRe:
			t= vod.split('$')
			url =t[1]
			title =t[0]
			if len(url) == 0:
				continue
			videos.append(title+"$"+url)
		return videos
	#取分类
	def custom_classification(self):
		xmlTxt=self.custom_webReadFile(urlStr='https://api.1080zyku.com/inc/api.php?ac=list')
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		classXml=root.iter('class')
		temporaryClass={}
		for vod in classXml:
			for value in vod:
				if self.custom_RegexGetText(Text=value.text,RegexText=r'(福利|倫理片|伦理片)',Index=1)!='':
					continue
				temporaryClass[value.text]=value.attrib['id']
				print("'{0}':'{1}',".format(value.text,value.attrib['id']))
		return temporaryClass

# T=Spider()
# l=T.homeVideoContent()
# # l=T.searchContent(key='柯南',quick='')
# # l=T.categoryContent(tid='12',pg='1',filter=False,extend={})
# for x in l['list']:
# 	print(x['vod_name'])
# mubiao= l['list'][1]['vod_id']
# print(mubiao)
# playTabulation=T.detailContent(array=[mubiao,])
# print(playTabulation)