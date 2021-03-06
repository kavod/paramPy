#!/usr/bin/env python
#encoding:utf-8

import sys
import json
import re
import copy
import Prompt
import ParamExceptions
import Trigger

##############
## ConfigElement
##############
class ConfigElement(object):
	def __init__(self,id,type,label=None,placeholder=None,required=False,choices=[],default=None,value=None,trigger={}):
		# ID
		self.id = str(id)
		
		# Type
		self.type = str(type)
				
		# Label
		self.label = str(label) if label is not None else self.id
		
		# Placeholder
		self.placeholder = str(placeholder) if placeholder is not None else "Enter " + self.label + " here"
		
		# Required
		self.required = bool(required)
		
		# Choices
		self.choices = []
		if (isinstance(choices,list) or isinstance(choices,dict)) and len(choices)>0:
			if self.type == 'password':
				raise ParamExceptions.WrongValue('405',str(id) + ': password not compatible with choices.')
			for item in choices:
				if not self.validateSingle(item,not self.required):
					raise ValueError(str(item) + ' not correct for ' + str(self.id))
			self.choices = choices
		else:
			self.choices = []
			
		# trigger
		self.setTrigger(trigger)
		
		# Default
		if default is None:
			self.default = None
		elif not self.required and len(self.choices)>0:
			raise ParamExceptions.WrongValue('405',str(id) + ': default value for facultative choices not compatible.')
		else:
			if not self.validateSingle(default,True):
				raise ValueError(str(default) + ' not correct for ' + str(self.id))
			self.default = default
			
		# Value
		self.setValue(value)
			
	def resetValue(self):
		self.value = self.default
		
	def setTrigger(self,trigger):
		if not isinstance(trigger,dict):
			raise TypeError("trigger parameter must be a dict instance")
		if not isinstance(trigger,Trigger.Trigger):
			trigger = Trigger.Trigger(trigger)
		for key in trigger.keys():
			if key != '*' and key is not None and not self.validateSingle(key):
				raise ValueError(str(key) + ' not correct for ' + str(self.id))
		self.trigger = trigger
		
	def __str__(self):
		return '<ConfigElement {0} (Type:{1}, required:{2}, Choices:{3})>'.format(self.id,self.type, str(self.required), str(len(self.choices)))
		
	def __deepcopy__(self,memo):
		newone = type(self)(id=self.id,type=self.type,label=self.label,placeholder=self.placeholder,required=self.required,default=self.default,value=self.value,trigger={})
		newone.choices = dict(self.choices)
		newone.setTrigger(Trigger.Trigger(self.trigger))
		return newone

	def convert(self,value):
		if value is None:
			return None
		if isinstance(value,list):
			return [self.convert(val) for val in value if val is not None]
		else:
			if self.type == "text" or self.type == "password" or self.type == "file" or self.type == 'email':
				return str(value)
			elif self.type == "boolean":
				return bool(value)
			else:
				return int(value)

	def validate(self,value,emptyAllowed=True):
		if isinstance(value,list):
			for it in value:
				if not self.validateSingle(it,emptyAllowed):
					return False
			return True
		else:
			return self.validateSingle(value,emptyAllowed)
		
	def validateSingle(self,value,emptyAllowed=True):
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
		elif self.type == "boolean":
			if not isinstance(value,bool):
				return False
		else:
			return False
		if len(self.choices)>0 and value not in self.choices:
			return False
		return True
		
	def setValue(self,value):
		if value is None:
			self.value = None
		else:
			if not self.validateSingle(value,True):
				raise ParamExceptions.WrongValue(401,str(value) + ' not correct for ' + str(self.type))
			self.value = self.convert(value)
		
	def cliPrompt(self,warning=''):
		while self.getStatus != 'disabled':
			reponse = Prompt.globalPrompt(self)
			if reponse == "" or reponse is None:
				self.setValue(self.default)
				return
			if self.validateSingle(reponse,not self.required):
				self.setValue(reponse)
				return
			warning='Incorrect answer'
			
	def getValues(self,hidePassword=True,mode='json'):
		if hidePassword and self.type == 'password':
			return '****'
		else:
			return self.value

	def toJSON(self):
		return {
				'id':			self.id,
				'type':			self.type,
				'label':		self.label,
				'placeholder':	self.placeholder,
				'required':		self.required,
				'choices':		self.choices,
				'default':		self.default,
				'trigger':		self.trigger
				}
	
	def getStatus(self):
		return self.trigger[self.value]

	def isNone(self):
		return self.value == None

def ConfigElementFromJSON(json):
	label = json['label'] if 'label' in json.keys() else None
	placeholder = json['placeholder'] if 'placeholder' in json.keys() else None
	required = json['required'] if 'required' in json.keys() else None
	choices = json['choices'] if 'choices' in json.keys() else []
	default = json['default'] if 'default' in json.keys() else None
	trigger = json['trigger'] if 'trigger' in json.keys() else {}
	return ConfigElement(id=json['id'],type=json['type'],label=label,placeholder=placeholder,required=required,choices=choices,default=default,trigger=trigger)

##############
## Param
##############
class Param(object):
	def __init__(self,id,multi=False,label="",items=[],filename=None,trigger=[]):
		self.id = str(id)
		self.multi = multi
		self.label = str(label) if str(label) is not None else self.id
		self.items = []
		self.addItems(items)
		self.filename = filename if filename is not None else None
		self.trigger = trigger
		
	def __str__(self):
		return '<Param {0} ({1} items, Multi:{2})>'.format(self.id,str(len(self.items)),str(self.multi))
		
	def __repr__(self):
		return str(self)
		
	def __len__(self):
		return len(self.items)
		
	def __deepcopy__(self,memo):
		newone = type(self)(id=self.id,label=self.label,items=[],filename=self.filename,trigger=[])
		newone.items = copy.deepcopy(self.items)
		newone.trigger = copy.deepcopy(self.trigger)
		return newone
		
	def __getitem__(self,key):
		if isinstance(key,int):
			return self.items[key]
		if isinstance(key,str):
			for item in self.items:
				if item.id == key:
					return item
			raise IndexError("list assignment index out of range")
		raise TypeError("Param indices must be integers or str, not " + type(key))
		
	def __setitem__(self,key,item):
		if not isinstance(key,int):
			raise TypeError("Param indices must be integers, not " + type(key))
		key_int = int(key)
		if not isinstance(item,ConfigElement) or isinstance(item,Param):
			raise TypeError("Param items only accept ConfigElement or Param, not " + type(key))
		if key_int < 0 or key_int > len(self.items) -1:
			raise IndexError("list assignment index out of range")
		self.items[key_int] = item
		
	def __delitem__(self, key):
		if not isinstance(key,int):
			raise TypeError("Param indices must be integers, not " + type(key))
		key_int = int(key)
		if key_int < 0 or key_int > len(self.items) -1:
			raise IndexError("list assignment index out of range")
		del self.items[key_int]

	def getStatus(self,key=None):
		if key is None:
			for trig in self.trigger: 
				if all(x in trig.keys() for x in ['src_id','src_status','dst_id','dst_status']) and trig['src_id'] != 'self' and trig['dst_id'] == 'self':
					if self[trig['src_id']].getStatus() == trig['src_status']:
						return trig['dst_status']
			return ''
		if self[key].getStatus() != "":
			return self[key].getStatus()
		else:
			for trig in self.trigger:
				if all(x in trig.keys() for x in ['src_id','src_status','dst_id','dst_status']):
					src = self if trig['src_id'] == 'self' else self[trig['src_id']]
					if src.getStatus() == trig['src_status'] and key == trig['dst_id']:
						return trig['dst_status']
		return ''
		
	def addItem(self,item):
		if len([it for it in self.items if it.id == item.id])>0:
			raise ParamExceptions.IdAlreadyUsed('402',str(item.id) + ' already used as ID')
		if not self.validate(item):
			raise ParamExceptions.WrongValue('401',str(item) + ' not correct for Param or ConfigElement')
		self.items.append(copy.deepcopy(item))
		
	def addItems(self,items):
		if not isinstance(items,list):
			self.addItem(items)
		else:
			for it in items:
				self.addItem(it)
		
	def cliPrompt(self):
		if len(self) < 1:
			raise ParamExceptions.WrongValue('406','Param {0} is empty'.format(str(len(self.items))))
		for item in self.items:
			if self.getStatus(item.id) != 'disabled':
				item.cliPrompt()
				
	def cliChange(self):
		choices = {}
		width = len(max([i.label for i in self.items], key=len))
		for key,item in enumerate(self.items):
			if isinstance(item,ConfigElement):
				value = item.value
			elif isinstance(item,ParamMulti):
				value = '{0} managed'.format(str(len(item)))
			else:
				value = ''
			line = ("{0:" + str(width)+"} - {1}").format(item.label,value)
			choices.update({key:line})
		reponse = Prompt.promptChoice(str(self.label),choices,warning='',selected=[],default = None,mandatory=True,multi=False)
		if isinstance(self.items[reponse],ConfigElement):
			self.items[reponse].cliPrompt()
		else:
			self.items[reponse].cliChange()
	
	def validate(self,item):
		if not isinstance(item,ConfigElement) and not isinstance(item,Param):
			return False
		return True
		
	def getValues(self,hidePassword=True,mode='json'):
		result = {}
		for item in self.items:
			result.update(copy.deepcopy({item.id:item.getValues(hidePassword)}))
		return result

	def loadValuesFromJSON(self,values):
		if not isinstance(values,dict):
			raise ParamExceptions.WrongValue('401',str(values) + ' not correct for ' + str(self.id))
		if str(self.id) not in [str(key) for key in values.keys()]:
			raise ParamExceptions.WrongValue('407',str(self.id) + ' not in input')
		json = values[self.id]
		if not isinstance(json,dict):
			raise ParamExceptions.WrongValue('401',str(json) + ' not correct for ' + str(self.id))
		for key in json.keys():
			for it in self.items:
				if str(it.id) == str(key):
					if isinstance(it,Param):
						it.loadValuesFromJSON({str(key):json[key]})
					else:
						it.setValue(json[key])
					del json[key]
					break
		if len(json)>0:
			raise ParamExceptions.WrongValue('403',str(json.keys()[0]) + ' not correct for ' + str(self.id))
			
	def resetValue(self):
		for item in self.items:
			item.resetValue()

	def isNone(self):
		return all(item.isNone() or self.getStatus(item.id) == 'disabled' for item in self.items)

	def toJSON(self):
		return {
				'id': 		self.id,
				'type':		'Param',
				'label':	self.label,
				'items':	[item.toJSON() for item in self.items],
				'trigger':	self.trigger
				}

	def loadFromFile(self,filename=None):
		if filename is None and self.filename is None:
			raise AttributeError("No filename provided")
		if filename is not None:
			self.filename = filename
		with open(self.filename) as data_file:   
			content = json.load(data_file) 
			self.loadValuesFromJSON({self.id:content})

	def saveToFile(self,filename=None):
		if filename is None and self.filename is None:
			raise AttributeError("No filename provided")
		if filename is not None:
			self.filename = filename
		with open(self.filename, "w") as outfile:
			json.dump(self.getValues(hidePassword=False), outfile, ensure_ascii=False)


def ParamFromJSON(json):
	id = json['id']
	label = json['label'] if 'label' in json.keys() else None
	items = []
	if 'items' in json.keys():
		for item in json['items']:
			if item['type'] == 'Param':
				items.append(ParamFromJSON(item))
			elif item['type'] == 'ParamMulti':
				items.append(ParamMultiFromJSON(item))
			else:
				items.append(ConfigElementFromJSON(item))
	trigger = json['trigger'] if 'trigger' in json.keys() else {}
	return Param(id,label=label,items=items,trigger=trigger)

##############
## ParamMulti
##############	
class ParamMulti(Param):
	def __init__(self,id,multi=True,label="",items=[],filename=None,trigger=[]):
		Param.__init__(self,id,multi=True,label=label,items=[],filename=filename)
		self.values = []
		self.addItems(items)
		self.trigger = trigger
		
	def __str__(self):
		return '<ParamMulti {0} ({1} items, Multi:{2}, ValueSets:{3})>'.format(self.id,str(len(self.items)),str(self.multi),str(len(self.values)))
		
	def __deepcopy__(self,memo):
		newone = type(self)(id=self.id,label=self.label,items=[],filename=self.filename)
		newone.items = copy.deepcopy(self.items)
		newone.values = copy.deepcopy(self.values)
		newone.trigger = copy.deepcopy(self.trigger)
		return newone

	def addItem(self,item):
		if len(self.values)>0:
			print "Warning! The values of {0} has been reset since adding a new ConfigElement".format(self.id)
			self.resetValue()
		Param.addItem(self,item)
		
	def loadValuesFromJSON(self,values):
		if not isinstance(values,dict):
			raise ParamExceptions.WrongValue('401',str(values) + ' not correct for ' + str(self.id))
		if self.id not in values.keys():
			raise ParamExceptions.WrongValue('407',str(self.id) + ' not in input')
		json = values[self.id]
		if isinstance(json,dict):
			json = [json]
		if not isinstance(json,list):
			raise ParamExceptions.WrongValue('401',str(json) + ' not correct for ' + str(self.id))
		self.values = []
		for item in json:
			newitem = Param(id=self.id,multi=False,label=self.label,items=copy.deepcopy(self.items),filename=None,trigger=self.trigger)
			for key in item.keys():
				for it in newitem.items:
					if str(it.id) == str(key):
						if isinstance(it,Param):
							it.loadValuesFromJSON({str(it.id):item[key]})
						else:
							it.setValue(item[key])
						del item[key]
						break
			if len(item)>0:
				raise ParamExceptions.WrongValue('403',str(item[0]) + ' not correct for ' + str(self.id))
			self.values.append(newitem)

	def cliPrompt(self):
		if len(self) < 1:
			raise ParamExceptions.WrongValue('406','ParamMulti {0} is empty'.format(self.id))
		while True:
			newitem = Param(id=self.id,multi=False,label=self.label,items=copy.deepcopy(self.items),filename=None,trigger=self.trigger)
			newitem.cliPrompt()
			if not newitem.isNone():
				self.values.append(newitem)
				if not Prompt.promptYN('Another {0}?'.format(self.label),default='n'):
					break
			else:
				break
				
	def getValues(self,hidePassword=True,mode='json'):
		result = []
		for value in self.values:
			result.append(copy.deepcopy(value.getValues(hidePassword)))
		return result

	def resetValue(self):
		self.values = []

	def toJSON(self):
		return {
				'id': 		self.id,
				'type':		'ParamMulti',
				'label':	self.label,
				'items':	[item.toJSON() for item in self.items],
				'trigger':	self.trigger
				}

def ParamMultiFromJSON(json):
	id = json['id']
	label = json['label'] if 'label' in json.keys() else None
	items = []
	if 'items' in json.keys():
		for item in json['items']:
			if item['type'] == 'Param':
				items.append(ParamFromJSON(item))
			elif item['type'] == 'ParamMulti':
				items.append(ParamMultiFromJSON(item))
			else:
				items.append(ConfigElementFromJSON(item))
	trigger = json['trigger'] if 'trigger' in json.keys() else {}
	return ParamMulti(id,label=label,items=items,trigger=trigger)

'''
if __name__ == '__main__':
	p1 = ConfigElement('id','text',multi=False,label='Torrents provider',placeholder="Indicate your torrents provider",required=True,choices={'t411':'T411','kickass':'KickAss'},condition=[],default='kickass')
	p1.cliPrompt()
	p2 = ConfigElement('user','text',multi=False,label='Torrents provider username',placeholder="Indicate your torrents provider user",required=False,choices=[],condition=[],default=None)
	p3 = ConfigElement('password','password',multi=False,label='Torrents provider password',placeholder="Indicate your torrents provider password",required=False,choices=[],condition=[],default=None)'''
"""
	param_tracker = ParamMulti(id='tracker',label='Torrent providers',items=[p1,p2,p3],filename=None)
	
	p4 = ConfigElement('server','text',multi=False,label='Transmission server',placeholder="Indicate the transmission address",required=True,choices=[],condition=[],default=None)
	p5 = ConfigElement('port','number',multi=False,label='Transmission port',placeholder="Indicate the transmission port",required=True,choices=[],condition=[],default=51413)
	p6 = ConfigElement('user','text',multi=False,label='Transmission username',placeholder="Indicate the transmission username",required=False,choices=[],condition=[],default=None)
	p7 = ConfigElement('password','password',multi=False,label='Transmission password',placeholder="Indicate the transmission password",required=False,choices=[],condition=[],default=None)
	p8 = ConfigElement('slots','number',multi=False,label='Transmission maximum slots',placeholder="Indicate the maximum number of simultaneous slots",required=True,choices=[],condition=[],default=6)
	p9 = ConfigElement('transfer','text',multi=False,label='Local transfer directory',placeholder="Indicate the target local directory (keep blank for disable)",required=False,choices=[],condition=[],default=None)
	param_transmission = Param(id='transmission',label='Transmission',items=[p4,p5,p6,p7,p8,p9],filename=None)

	param = Param(id='conf',label="Configuration",items=[param_tracker,param_transmission],filename=None)
	
	param.cliPrompt()
	
	print param.toJSON()"""
	
