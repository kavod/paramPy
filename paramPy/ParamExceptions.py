#!/usr/bin/env python
#encoding:utf-8

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
