#!/usr/bin/env python
#encoding:utf-8

class Trigger(dict):
	def __init__(self,*args):
		dict.__init__(self,*args)
		for value in self.values():
			if not isinstance(value,str):
				raise TypeError("Trigger parameter must be a dict with str values only not " + str(value))
	
	def __getitem__(self,key):
		if key not in self.keys():
			if '*' in self.keys():
				return dict.__getitem__(self,'*')
			else:
				return ''
		else:
			return dict.__getitem__(self,key)
