#!/usr/bin/env python
#encoding:utf-8

import os,sys
import json
import re
import getpass
	
class PointCusto(object):
	def __init__(self,id,type,multi=False,label=None,placeholder="",required=False,choices=[],condition=[],value=None,default=None):
		# ID
		self.id = str(id)
		
		# Type
		self.type = str(type)
		
		# Multi
		self.multi = bool(multi)
		
		# Label
		self.label = str(label) if str(label) is not None else self.id
		
		# Placeholder
		self.placeholder = str(placeholder) if str(placeholder) != "" else "Enter " + self.label + " here"
		
		# Required
		self.required = bool(required)
		
		# Choices
		if (isinstance(choices,list) or isinstance(choices,dict)) and len(choices)>0:
			if self.type == 'password':
				raise WrongValue('405',str(id) + ': password not compatible with choices.')
			for item in choices:
				if not self._validate(item,not self.required):
					raise WrongValue('401',str(item) + ' not correct for ' + str(self.type))
			self.choices = choices
		else:
			self.choices = []
		
		# Condition
		self.condition = condition
		
		# Default
		if default is None:
			self.default = None
		else:
			if self.multi:
				raise WrongValue('405',str(id) + ': default value not compatible with multivalue.')
			if isinstance(default,list):
				for item in default:
					if not self._validate(item,not self.required):
						raise WrongValue('401',str(item) + ' not correct for ' + str(self.type))
			else:
				if not self._validate(default,not self.required):
					raise WrongValue('401',str(default) + ' not correct for ' + str(self.type))
			self.default = default
		
		# Value
		if value is not None:
			self.setValue(value)
		else:
			self.value = self.default
		
	def __str__(self):
		if self.type == 'password' and not self.multi:
			value = '****'
		elif self.type == 'password' and self.multi:
			value = ['****' for item in self.value]
		else:
			value = self.value
		if self.multi:
			value = '[' + ','.join([str(i) for i in value]) + ']'
		else:
			value = str(value)
		return '{0:25} {1}'.format(self.label+':',value)
		
	def setValue(self,value):
		if self.multi:
			if not isinstance(value,list):
				raise WrongValue('401',str(value) + ' not correct for ' + str(self.type) + ' (multi)')
			for item in value:
				if not self._validate(item,True):
					raise WrongValue('401',str(item) + ' not correct for ' + str(self.type) + ' (multi)')
				item = self._convert(item)
			self.value = value
		else:
			if not self._validate(value,True):
				raise WrongValue(401,str(value) + ' not correct for ' + str(self.type))
			self.value = self._convert(value)
			
	def getType(self):
		return self.type
		
	def toJSON(self):
		return self.value
		'''return {
			"id":			self.id,
			"type":			self.type,
			"multi":		self.multi,
			"label":		self.label,
			"placeholder":	self.placeholder,
			"required":		self.required,
			"choices":		self.choices,
			"condition":	self.condition,
			"value":		self.value
			}'''

	def _validate(self,value,emptyAllowed=True):
		if self.type == "text" or self.type == "password" or self.type == "file":
			if not isinstance(value,str) and not isinstance(value,unicode):
				return False
			if not emptyAllowed and len(value) == 0:
				return False
		elif self.type == "number":
			if not isinstance(value,int) and not str(value).isdigit():
				return False
			if not emptyAllowed and value == 0:
				return False
		elif self.type == "email":
			if not isinstance(value,str) and not isinstance(value,unicode):
				return False
			if emptyAllowed and len(value) == 0:
				return True
			elif not re.match(r"[^@]+@[^@]+\.[^@]+", value):
				return False
		else:
			return False
		return True
		
	def _convert(self,value):
		if self.type == "text" or self.type == "password" or self.type == "file" or self.type == 'email':
			return str(value)
		else:
			return int(value)
			
	def cliPrompt(self):
		self.value = globalPrompt(self.placeholder,self.choices,self.multi,password=(self.type=='password'),mandatory=False,default=self.default)
		'''if self.multi:
			if self.choices is None: # Multichoice
				self.value = promptList(self.placeholder,password=(self.type=='password'))
			else: # Multientries
				choicesList = [[key,val] for key,val in enumerate(self.choices)]
				result = promptList(self.placeholder,choix=choicesList)
				self.value = []
				for item in result:
					self.value.append(self.choices[item])
		else:
			if self.choices is None: # Single entry
				self.value = promptSimple(self.placeholder,self.default,password=(self.type=='password'))
			else: # Single choice
				choicesList = [[key,val] for key,val in enumerate(self.choices)]
				default = [i for i in enumerate(self.choices) if i[1] == self.default][0] if self.default is not None else 0
				self.value = self.choices[promptChoice(self.placeholder,choix=choicesList,default=default)]'''
			
			
class Param(object):
	def __init__(self,id,label="",items=[],filename=None):
		self.id = str(id)
		self.label = str(label) if str(label) is not None else self.id
		for it in items:
			if not isinstance(it,PointCusto) and not isinstance(it,Param):
				raise WrongValue('401',str(it) + ' not correct for Param or PointCusto')
		self.items = []
		self.addItems(items)
		self.filename = filename if filename is not None else None
		
	def __str__(self):
		result = str(self.label) + '\n'
		result += '-'*len(self.label) + '\n'
		for item in self.items:
			result += str(item) + '\n'
		return result
		
	def getType(self):
		return "param"
		
	def addItem(self,item):
		if len([it for it in self.items if it.id == item.id])>0:
			raise IdAlreadyUsed('402',str(item.id) + ' already used as ID')
		if not isinstance(item,PointCusto) and not isinstance(item,Param):
			raise WrongValue('401',str(it) + ' not correct for Param or PointCusto')
		self.items.append(item)
		
	def addItems(self,items):
		if not isinstance(items,list):
			raise WrongValue('401',str(items) + ' not correct for list of Param or PointCusto')
		for it in items:
			self.addItem(it)
			
	def loadValuesFromJSON(self,json):
		for key in json.keys():
			for it in self.items:
				if str(it.id) == str(key):
					if it.getType() == 'param':
						it.loadValuesFromJSON(json[key])
					else:
						it.setValue(json[key])
					del json[key]
					break
		if len(json)>0:
			raise WrongValue('403',str(json.keys()[0]) + ' not in ' + str(self.id))
			
	def loadValuesFromJSONfile(self,filename):
		json_data=open(filename).read()
		loadValuesFromJSON(json.loads(json_data))
		
	def cliPrompt(self):
		for item in self.items:
			item.cliPrompt()
		
	def toJSON(self):
		result = {}
		for item in self.items:
			result[item.id] = item.toJSON()
		return result
		
def promptSimple(question,default = '',password=False):
	"""
		The ``promptSimple`` function
		=============================
		
		Use it for a text required input from stdin
		
		:param question: Text displayed before text input
		:type question: string

		:return: user typed text
		:rtype: string

		:Example:

		>>> from Prompt import *
		>>> promptSimple('What is the answer to life, the universe, and everything?')
		What is the answer to life, the universe, and everything?
		0 = Exit
		42
		'42'
		
	"""	
def promptText(question,default = None,selected=[],warning='',password=False,mandatory=False):
	while True:
		str_default = ''
		if default is not None:
			str_default = '[{0}]'.format(str(default))
		print_question('{0} {1}'.format(str(question),str_default),warning,selected)
		reponse = str(prompt(password))
		if reponse != '' or not mandatory:
			return reponse
		warning = "Mandatory answer"
		
def globalPrompt(question,choix=[],multi=False,password=False,mandatory=False,default=None):
	if default is not None and multi:
		raise WrongValue('405',str(id) + ': default value not compatible with multivalue.')
	if multi:
		return promptMulti(question,choix=choix,password=password,mandatory=mandatory)
	else:
		return promptSingle(question,choix=choix,password=password,mandatory=mandatory,default=default)
		
def promptSingle(question,choix=[],password=False,mandatory=False,default=None):
	if len(choix)>0:
		if isinstance(choix,list):
			mydict = {}
			for i,j in enumerate(choix):
				mydict.update({i:j})
		else:
			mydict = choix
		reponse = promptChoice(question,selected=[],choix=mydict,mandatory=mandatory,default=default)
	else:
		reponse = promptText(question,selected=[],password=password,mandatory=mandatory,default=default)
	return reponse
			
		
def promptMulti(question,choix=[],password=False,mandatory=False):
	reponse = None
	result = []
	warning = ''
	while reponse != '':
		if len(result)>0:
			selected = "Already entered: " + str(result) + "\n"
		else:
			selected = ""
		if len(choix)>0:
			if isinstance(choix,list):
				mydict = {}
				for i,j in enumerate(choix):
					mydict.update({i:j})
			else:
				mydict = choix
			str_question = question + ' (Press "Enter" to achieve entry)' if len(result) > 0 or not mandatory else question
			reponse = promptChoice(str_question,warning=warning,selected=result,choix=mydict,mandatory=(mandatory and len(result)<1),default=None,multi=True)
			if reponse is None:
				reponse = ''
			else:
				if reponse in result:
					result.remove(reponse)
				else:
					result.append(reponse)
		else:
			str_question = question + ' (Press "Enter" to achieve entry)' if len(result) > 0 else question
			reponse = promptText(str_question,warning=warning,selected=result,password=password,mandatory=(mandatory and len(result)<1))
			if str(reponse) in result:
				warning = '!!! ' + str(reponse) + ' already entered'
				reponse = None
			elif reponse != '':
				warning = ''
				result.append(reponse)
	return result
	
def print_question(question,warning='',result=[]):
	question = '* ' + question
	print(chr(27) + "[2J")
	print question
	print '*'*len(question)
	if len(result)>0:
		print "Previously entered:{0}".format(str(result))
	if warning != '':
		print warning
	
def promptChoice(question,choix,warning='',selected=[],default = None,mandatory=False,multi=False):
	"""
		The ``promptChoice`` function
		=============================
		
		Use it for let user select a choice in a restricted choices list
		
		:param question: Text displayed before choice list
		:type question: string
		
		:param choix: List of choices. Choices are list of number and choice label
		:type choix: list

		:param default: Index of the default choice (0 by default, ie. the first choice)
		:type choix: Integer

		:return: Index of the choice
		:rtype: Integer

		:Example:

		>>> from Prompt import *
		>>> promptChoice("What do you prefer?",[[12,'Duck'],[34,'Rabbit'],[56,'Snail']],2)
		What do you prefer? [3 by default]
		1 : Duck
		2 : Rabbit
		3 : Snail
		0 : Exit
		2
		34
		
	"""
	str_is_selected = 	'[SELECTED]'
	str_not_selected = 	'[        ]'
	choix = sorted(choix.items())
	warning = ''
	while True:	
		str_choices = ''
		width = len(max([i[1] for i in choix], key=len))
		for i,val in enumerate(choix):
			if str(val[0]) == str(default):
				question += " [{0} by default]".format(str(i+1))
			if multi:
				str_selected = str_is_selected if val[0] in selected else str_not_selected
			else:
				str_selected = ''
			str_choices += ("{0:2}: {1:" + str(width) + "} {2}\n").format(str(i+1),val[1],str_selected)
		print_question(question,warning)
		print str_choices,
		reponse = prompt()
		if reponse == '':
			if default is not None:
				return default
			if mandatory and len(selected) < 1:
				warning = "Mandatory answer"
			else:
				return None
		elif not reponse.isdigit():
			warning = "Incorrect answer"
		elif int(reponse) < 1 or int(reponse) > len(choix)+1:
			warning = "Incorrect answer"
		else:
			return choix[int(reponse)-1][0]
			
def prompt(password=False):
	invite = "> "
	try:
		if password:
			return getpass.getpass(invite)
		else:
			return raw_input(invite)
	except KeyboardInterrupt:
		print "\User interrupted"
		sys.exit()
		
class WrongValue(Exception):
	def __init__(self,value,error):
		self.value = int(value)
		self.error = error
		
	def __str__(self):
		return "Error "+str(self.value)+": "+str(self.error)
				
class IdAlreadyUsed(Exception):
	def __init__(self,value,error):
		self.value = int(value)
		self.error = error
		
	def __str__(self):
		return "Error "+str(self.value)+": "+str(self.error)
			
if __name__ == '__main__':
	'''width = 100
	print ('-'*9+'*')*5
	p1 = PointCusto('name','text',label="Name",required=True,value="Niouf Niouf")
	p2 = PointCusto('age','number',label="Age",required=True,default=24,placeholder="Please enter age of "+p1.value)
	p2.cliPrompt()
	print p2
	print p2.getType()
	param = Param('conf','Configuration',[p1,p2])
	p3 = PointCusto('email','email',label="Email",required=True,value=u"sdfd@sg.fr")
	p4 = PointCusto('password','password',label="Password",required=True,value="123456")
	param.addItems([p3,p4])
	p5 = PointCusto('fruits','text',multi=True,label="Favorite fruits",required=True,value=[u"banana","pineapple"])
	p5.cliPrompt()
	param.addItem(p5)
	p6 = PointCusto('childAge','number',multi=True,label="Children ages",required=True,value=[2,6])
	param.addItem(p6)
	print param
	param.loadValuesFromJSON({'name':'Niorf Niorf','email':'niorf@niorf.fr'})
	print param
	param.cliPrompt()
	print param'''
	
	
	p1 = PointCusto("id","text",multi=True,label="Torrent provider",placeholder="Indicate your torrent provider",required=False,choices={'t411':'T411','kickass':'Kickass'},condition=[],value=None,default=None)
	p2 = PointCusto("username","text",multi=False,label="Torrent provider username",placeholder="Indicate the username for the tracker",required=False,choices=None,condition=[],value=None,default=None)
	p3 = PointCusto("password","password",multi=False,label="Torrent provider password",placeholder="Indicate the password for the tracker",required=False,choices=None,condition=[],value=None,default=None)
	param_tracker = Param('tracker','Tracker',[p1,p2,p3])
	param = Param('conf','Configuration',[param_tracker])
	param.cliPrompt()
	print param
	print param.toJSON()
	
	'''print "Single, Not password, mandatory"
	print promptSingle(question="Enter a name",default = "Niouf Niouf",password=False,mandatory=True)
	print promptSingle(question="Enter a country",default = 0,password=False,mandatory=True,choix=['France','Other place'])
	print promptSingle(question="Enter a password",password=True,mandatory=False)
	print promptSingle(question="Your favorite football club",password=False,mandatory=False,choix=['PSG','OM'])
	print promptMulti(question="Enter children names",password=False,mandatory=False)
	print promptMulti(question="Enter at least one wish",password=False,mandatory=True)
	#print promptChoice(question="What do you own?",choix={0:'Playstation',1:'Sega'},warning='',selected=[],default = None,mandatory=True)
	print promptMulti(question="married?",password=False,mandatory=True,choix=['Yes','No', 'Yes but no longer'])
	print promptMulti(question="Do you own?",password=False,mandatory=False,choix={'psx':'a Playstation','sega':'a Sega', 'nes':'a Nintendo'})'''
	
