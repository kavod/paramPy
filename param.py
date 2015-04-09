#!/usr/bin/env python
#encoding:utf-8

import os,sys
import json
import re
import getpass
import copy
	
class PointCusto(object):
	def __init__(self,id,type,multi=False,label=None,placeholder="",required=False,choices=[],condition=[],default=None):
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
		self.setValue(self.default)
		
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
		
	def __deepcopy__(self,memo):
		newone = type(self)(id=self.id,type=self.type,multi=self.multi,label=self.label,placeholder=self.placeholder,required=self.required,default=self.default)
		newone.choices = dict(self.choices)
		newone.condition = list(self.condition)
		newone.value = copy.deepcopy(self.value)
		return newone
		
	def setValue(self,value):
		if value is None:
			self.value = None
		elif self.multi:
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
		warning = ''
		while True:
			reponse = globalPrompt(self.placeholder,self.choices,self.multi,password=(self.type=='password'),mandatory=False,default=self.default,warning=warning)	
			if self._validate(reponse,not self.required):
				self.value = reponse
				break
			warning='Incorrect answer'
		
			
class Param(object):
	def __init__(self,id,label="",items=[],filename=None):
		self.id = str(id)
		self.multi = False
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
		
	def __deepcopy__(self,memo):
		newone = type(self)(id=self.id,label=self.label,items=[],filename=self.filename)
		newone.items = copy.deepcopy(self.items)
		return newone
		
	def getType(self):
		return "param"
		
	def addItem(self,item):
		if len([it for it in self.items if it.id == item.id])>0:
			raise IdAlreadyUsed('402',str(item.id) + ' already used as ID')
		if not isinstance(item,PointCusto) and not isinstance(item,Param):
			raise WrongValue('401',str(it) + ' not correct for Param or PointCusto')
		self.items.append(copy.deepcopy(item))
		
	def addItems(self,items):
		if not isinstance(items,list):
			raise WrongValue('401',str(items) + ' not correct for list of Param or PointCusto')
		for it in items:
			self.addItem(it)
			
	def loadValuesFromJSON(self,json):
		for key in json.keys():
			for it in self.items:
				if str(it.id) == str(key):
					if isinstance(it,Param):
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

class ParamMulti(Param):
	def __init__(self,id,label="",items=[],filename=None):
		Param.__init__(self,id=id,label=label,items=[],filename=filename)
		self.id = id
		self.label = label
		self.filename = filename
		self.multi = True
		self.prototype = []
		for it in items:
			if not isinstance(it,PointCusto) and not isinstance(it,Param):
				raise WrongValue('401',str(it) + ' not correct for Param or PointCusto')
		self.addItems(items)
		
	def __str__(self):
		result = ''
		for i,j in enumerate(self.items):
			label = str(self.label) + ' ' + str(i+1)
			result += label + '\n'
			result += '-'*len(label) + '\n'
			for item in j:
				result += str(item) + '\n'
		return result
		
	def __deepcopy__(self,memo):
		newone = type(self)(id=self.id,label=self.label,items=[],filename=self.filename)
		newone.prototype = copy.deepcopy(self.prototype)
		return newone

	def addItem(self,item):
		if len([it for it in self.prototype if it.id == item.id])>0:
			raise IdAlreadyUsed('402',str(item.id) + ' already used as ID')
		if not isinstance(item,PointCusto) and not isinstance(item,Param):
			raise WrongValue('401',str(it) + ' not correct for Param or PointCusto')
		self.prototype.append(copy.deepcopy(item))
		
	def loadValuesFromJSON(self,json_list):
		if not isinstance(json_list,list):
			json_list = [json_list]
		for json in json_list:
			for key in json.keys():
				for it in self.items:
					if str(it.id) == str(key):
						if isinstance(it,Param):
							it.loadValuesFromJSON(json[key])

						else:
							it.setValue(json[key])
						del json[key]
						break
			if len(json)>0:
				raise WrongValue('403',str(json.keys()[0]) + ' not in ' + str(self.id))

	def cliPrompt(self):
		if len(self.prototype) < 1:
			raise WrongValue('406','ParamMulti is empty')
		while True:
			newitem = copy.deepcopy(self.prototype)
			self.items.append(newitem)
			for item in newitem:
				item.cliPrompt()
			if not promptYN('Another {0}?'.format(self.label),default='n'):
				break
			
	def toJSON(self):
		result = []
		for item in self.items:
			val = {}
			for value in item:
				val[value.id] = value.toJSON()
			result.append(val)
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
		if reponse == '' and default is not None:
			return default
		if reponse != '' or not mandatory:
			return reponse
		warning = "Mandatory answer"
		
def globalPrompt(question,choix=[],multi=False,password=False,mandatory=False,default=None,warning=''):
	if default is not None and multi:
		raise WrongValue('405',str(id) + ': default value not compatible with multivalue.')
	if multi:
		return promptMulti(question,choix=choix,password=password,mandatory=mandatory,warning=str(warning))
	else:
		return promptSingle(question,choix=choix,password=password,mandatory=mandatory,default=default,warning=str(warning))
		
def promptSingle(question,choix=[],password=False,mandatory=False,default=None,warning=''):
	if len(choix)>0:
		if isinstance(choix,list):
			mydict = {}
			for i,j in enumerate(choix):
				mydict.update({i:j})
		else:
			mydict = choix
		
		reponse = promptChoice(question,selected=[],warning=str(warning),choix=mydict,mandatory=mandatory,default=default)
	else:
		reponse = promptText(question,selected=[],warning=str(warning),password=password,mandatory=mandatory,default=default)
	return reponse

def promptYN(question,default=None):
	str_y = 'y'
	str_n = 'n'
	if default is None:
		mandatory = True
	else:
		mandatory = False
		if str(default).lower() not in ['y','n']:
			default = 'n'
		if str(default).lower() == 'y':
			str_y = str_y.upper()
		else:
			str_n = str_n.upper()
	reponse = promptSingle('{0} [{1}/{2}]'.format(str(question),str_y,str_n),choix=[],password=False,mandatory=mandatory,default=str(default))
	return reponse.lower() == 'y'

		
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
		elif int(reponse) < 1 or int(reponse) > len(choix):
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
	p1 = PointCusto('id','text',multi=False,label='Torrents provider',placeholder="Indicate your torrents provider",required=True,choices={'t411':'T411','kickass':'KickAss'},condition=[],default='kickass')
	p2 = PointCusto('user','text',multi=False,label='Torrents provider username',placeholder="Indicate your torrents provider user",required=False,choices=[],condition=[],default=None)
	p3 = PointCusto('password','password',multi=False,label='Torrents provider password',placeholder="Indicate your torrents provider password",required=False,choices=[],condition=[],default=None)
	param_tracker = ParamMulti(id='tracker',label='Torrent providers',items=[p1,p2,p3],filename=None)
	
	p4 = PointCusto('server','text',multi=False,label='Transmission server',placeholder="Indicate the transmission address",required=True,choices=[],condition=[],default=None)
	p5 = PointCusto('port','number',multi=False,label='Transmission port',placeholder="Indicate the transmission port",required=True,choices=[],condition=[],default=51413)
	p6 = PointCusto('user','text',multi=False,label='Transmission username',placeholder="Indicate the transmission username",required=False,choices=[],condition=[],default=None)
	p7 = PointCusto('password','password',multi=False,label='Transmission password',placeholder="Indicate the transmission password",required=False,choices=[],condition=[],default=None)
	p8 = PointCusto('slots','number',multi=False,label='Transmission maximum slots',placeholder="Indicate the maximum number of simultaneous slots",required=True,choices=[],condition=[],default=6)
	p9 = PointCusto('transfer','text',multi=False,label='Local transfer directory',placeholder="Indicate the target local directory (keep blank for disable)",required=False,choices=[],condition=[],default=None)
	param_transmission = Param(id='transmission',label='Transmission',items=[p4,p5,p6,p7,p8,p9],filename=None)

	param = Param(id='conf',label="Configuration",items=[param_tracker,param_transmission],filename=None)
	
	param.cliPrompt()
	
	print param.toJSON()
