# -*- coding: UTF-8 -*-
from time import sleep

import urllib2
from bs4 import BeautifulSoup, NavigableString, Tag
import re

#-------------------------util functions-------------------------
def getClassName(soupTag):
	'''returns a list of class names'''
	return soupTag.get('class','')

def isClassLast(soupTag):
	if 'views-row-last' in getClassName(soupTag):	return 1
	return 0

#make it work for unicode
# def naive_tokenize(a):
# 	try:
# 		a = a.replace('\xe0\xa5\xa4', ' \xe0\xa5\xa4 ')
# 		a = re.sub('\t+', ' ', a)
# 		a = re.sub(' +', ' ', a)
# 		a,count = re.subn('(\xe0\xa5\xa4 \xe0\xa5\xa4)+', ' \xe0\xa5\xa4 ',a)
# 		while(count):
# 			a = a.replace('\xe0\xa5\xa4', ' \xe0\xa5\xa4 ')
# 			a = re.sub('\t+', ' ', a)
# 			a = re.sub(' +', ' ', a)
# 			a,count = re.subn('(\xe0\xa5\xa4 \xe0\xa5\xa4)+', ' \xe0\xa5\xa4 ',a)
# 		return a
# 	except:
# 		print type(a),a
# 		a = a.replace('\xe0\xa5\xa4', ' \xe0\xa5\xa4 ')
#------------------------/util functions-------------------------

def get_bookname_id(soup):
	#the dropdown id
	select = soup.find('select', { "id" : "edit-field-kanda-tid"})
	#the selected option in the dropdown : names the book id and name
	option = select.find_all('option', selected=True)[0]
	return (option.text, option['value'])

def get_sarga_id(soup):
	#the dropdown id
	select = soup.find('select', { "id" : "edit-field-sarga-value"})
	#the selected option in the dropdown : names the book id and name
	option = select.find_all('option', selected=True)[0]
	#text and value are the same
	return option['value']

def parse_contentbox(text,flag=0):
	pass

def sans_para_reader(sans_text):
	"""returns the shloka text and the shloka number.
	needs a text string, not a soup-tag object"""
	final_text=''
	rege = re.findall(ur'(.*)(\d+\.\d+\.\d+)(.*)(\d+\.\d+\.\d+)(.*)', sans_text)
	try:
		for r in rege[0]:
			if not (re.findall(ur'\d+\.\d+\.\d+', r)):
				final_text += r				
	except:
		rege = re.findall(ur'(.*)(\d+\.\d+\.\d+)(.*)', sans_text)
		try:
			for r in rege[0]:
				if not (re.findall(ur'\d+\.\d+\.\d+', r)):
					final_text += r
		except:
			final_text += re.findall(ur'(.*)', sans_text)[0]
	return final_text

def eng_and_sans_para_reader(english1_text):
	temp = []
	#read text between the <br>'s
	for a in english1_text.childGenerator():
		if isinstance(a,NavigableString):
			temp.append(a)
	english1_text = temp[0]
	sans2_text = temp[1]
	english2_text = temp[2]
	del temp

	return english1_text, sans2_text, english2_text

def extract_first_box_sans_text(mixed_text):
	"""returns the shloka text and the shloka number.
	needs a mixed text string, not a soup-tag object"""
	try:
		sans_text = re.findall(ur'\[(.*)\](.*)', mixed_text)
		return sans_para_reader(sans_text[0][1])
	except:
		sans_text = re.findall(ur'\[(.*?)\.(.*)', mixed_text)
	return sans_para_reader(sans_text[0][1])

sargas_in_each_book = [77,119,75,67,68,128,111]

# for book_id in xrange(5):
#only book's exceptions handled
for book_id in [0]: #last two books unavailable
	book_id = book_id+1
	if book_id==1:
		continue
	for sarga_id in xrange(sargas_in_each_book[book_id-1]):
		sarga_id +=1

		if(sarga_id%20==0): #scraping manners
			sleep(5)


		url = 'https://www.valmiki.iitk.ac.in/sloka?field_kanda_tid='+str(book_id)+'&language=dv&field_sarga_value='+str(sarga_id)
		website = urllib2.urlopen(url)

		soup = BeautifulSoup(website, "lxml")

		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()    # rip it out

		print get_bookname_id(soup)[0]
		print get_sarga_id(soup)
		
		content_div = soup.find_all('div', { "class" : "views-row" })

		es_list=[] #list of english - sanskrit pairs; one for each sarga

		#1like=1prayer and 1box=1shloka
		box_count=1
		for box in content_div:
			content = box.find_all('div', { "class" : "field-content" })
			if book_id == 1: #this has a different structure
				if book_count==2 and sarga_id==26:
					print "Asdasd"
				else:
					print box_count, sarga_id
					sans_text = extract_first_box_sans_text(content[0].text)
					english_text = content[2].text
					es_list.append([english_text,sans_text])
			
			elif isClassLast(box): #this has two sanskrit - english pairs
				try:
					sans1_text = sans_para_reader(content[0].text)
					english1_text, sans2_text, english2_text = eng_and_sans_para_reader(content[2])
					es_list.append([english1_text,sans1_text])
					es_list.append([english2_text,sans2_text])
				except:
					if content[0].text=='':
						pass
			else:
				try:
					content = box.find_all('div', { "class" : "field-content" })
					sans_text = sans_para_reader(content[0].text)
					english_text = content[2].text
					es_list.append([english_text,sans_text])
				except:
					print content[0].text					
					raw_input()
			print box_count, "================================"
			box_count += 1 

		f = open('Data/Book_'+str(book_id)+'/'+'sarga_'+str(sarga_id), 'w')
		f.write(str(es_list))
		f.write('\n')
		f.close()