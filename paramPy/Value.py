#!/usr/bin/env python
#encoding:utf-8

import sys
import json
import copy
import Prompt
import ParamExceptions
import param

##############
## Value
##############	
class Value(object):
	def __init__(self,custo,value=None):
		if not isinstance(custo,param.PointCusto):
			raise ParamExceptions.WrongValue('401','First parameter must be a param.PointCusto')
		self.custo = custo
		
		if value is None:
			self.value = self.custo.default
		else:
			if self.custo.validate(value):
				self.value = value
			else:
				raise ParamExceptions.WrongValue(401,str(value) + ' not correct for ' + str(self.custo.type))
				
	def __str__(self):
		if self.custo.type == 'password' and not self.custo.multi:
			value = '****'
		elif self.custo.type == 'password' and self.custo.multi:
			value = ['****' for item in self.value]
		else:
			value = self.value
		if self.multi:
			value = '[' + ','.join([str(i) for i in value]) + ']'
		else:
			value = str(value)
		return '{1}'.format(value)		
		
	def __deepcopy__(self,memo):
		newone = type(self)(custo=self.custo)
		newone.value = copy.deepcopy(self.value)
		return newone

	def setValue(self,value):
		if value is None:
			self.value = None
		elif self.custo.multi:
			if not isinstance(value,list):
				raise ParamExceptions.WrongValue('401',str(value) + ' not correct for ' + str(self.custo.type) + ' (multi)')
			for item in value:
				if not self.custo.validate(item,True):
					raise ParamExceptions.WrongValue('401',str(item) + ' not correct for ' + str(self.type) + ' (multi)')
				item = self.convert(item)
			self.value = value
		else:
			if not self.validate(value,True):
				raise ParamExceptions.WrongValue(401,str(value) + ' not correct for ' + str(self.type))
			self.value = self.convert(value)
		
	def convert(self,value):
		if self.custo.type == "text" or self.custo.type == "password" or self.custo.type == "file" or self.custo.type == 'email':
			return str(value)
		else:
			return int(value)
		
	def toJSON(self):
		return self.value
			
	def cliPrompt(self):
		warning = ''
		while True:
			reponse = Prompt.globalPrompt(self.custo)	
			if self.custo.validate(reponse,not self.custo.required):
				self.value = reponse
				break
			warning='Incorrect answer'

##############
## MultiValue
##############	
class MultiValue(Value):
	def __init__(self,custo,value=[]):
		if not isinstance(custo,param.PointCusto):
			raise ParamExceptions.WrongValue('401','First parameter must be a param.PointCusto with multi=True')
		if not custo.multi:
			raise ParamExceptions.WrongValue('401','First parameter must be a param.PointCusto with multi=True')
		self.custo = custo
		
		if self.validate(value,False):
			raise ParamExceptions.WrongValue('401','Second parameter must be a list of ' + str(self.custo.type))
			
		self.value = value
				
	def __str__(self):
		if self.custo.type == 'password':
			value = ['****' for item in self.value]
		else:
			value = '[' + ','.join([str(i) for i in value]) + ']'
		return '{1}'.format(value)
		
	def __deepcopy__(self,memo):
		newone = type(self)(custo=self.custo)
		newone.value = copy.deepcopy(self.value)
		return newone

	def setValue(self,value):
		self.value = []
		if value is None:
			return
		elif self.custo.validate(value):
			for item in value:
				self.value.append(self.custo.convert(item))
		else:
			ParamExceptions.WrongValue('401',str(value) + ' not correct for MultiValue ' + str(self.type))
		
	def toJSON(self):
		return self.value
			
	def cliPrompt(self):
		warning = ''
		while True:
			reponse = Prompt.globalPrompt(self.custo)	
			if self.custo.validate(reponse,not self.custo.required):
				self.value = reponse
				break
			warning='Incorrect answer'
			
##############
## ValueSet
##############		
class ValueSet(object):
	def __init__(self,values=[]):
		if not isinstance(values,list):
			raise ParamExceptions.WrongValue('401','First parameter must be a list of Value or ValueSet')
		for it in values:
			if not isinstance(it,Value) and not isinstance(it,ValueSet):
				raise ParamExceptions.WrongValue('401',str(it) + ' not correct for Value or ValueSet')
		self.values = values
	
	def __str__(self):
		result = ''
		for item in self.values:
			result += str(item) + '\n'
		return result
	
	def __deepcopy__(self,memo):
		newone = type(self)()
		newone.values = copy.deepcopy(self.values)
		return newone
			
	def loadValuesFromJSON(self,json):
		for key in json.keys():
			for it in self.values:
				if isinstance(it,Value):
					if str(it.custo.id) == str(key):
						it.setValue(json[key])
				else:
					it.loadValuesFromJSON(json[key])
				del json[key]
				break
		if len(json)>0:
			raise ParamExceptions.WrongValue('403',str(json.keys()[0]) + ' not in ' + str(self.param.id))
			
	def loadValuesFromJSONfile(self,filename):
		json_data=open(filename).read()
		self.loadValuesFromJSON(json.loads(json_data))
		
	def cliPrompt(self):
		result = []
		for item in self.param.items:
			self.values = self.param.cliPrompt()

	def toJSON(self):
		result = {}
		for item in self.values:
			result[item.custo.id] = item.custo.toJSON()
		return result

