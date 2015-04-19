#!/usr/bin/env python
#encoding:utf-8

import sys
import getpass

##############
## PromptSimple
##############
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
		
def globalPrompt(custo,warning=''):
	'''if custo.multi:
		return promptMulti(
						custo.placeholder,
						choix=custo.choices,
						password=(custo.type=='password'),
						mandatory=custo.required,
						warning=str(warning)
						)
	else:'''
	if custo.type == 'boolean':
		return promptYN(custo.placeholder,default=custo.default)
	else:
		return promptSingle(
						custo.placeholder,
						choix=custo.choices,
						password=(custo.type=='password'),
						mandatory=custo.required,
						default=custo.default,
						warning=str(warning)
						)
		
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
	
def print_question(str_question,warning='',result=[]):
	str_question = '* ' + str_question
	print(chr(27) + "[2J")
	print str_question
	print '*'*len(str_question)
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
		
		if default is None and not mandatory:
			str_question = "{0} [keep blank for none]".format(str(question))
		else:
			str_question = question
		for i,val in enumerate(choix):
			if default is not None and str(val[0]) == str(default):
				str_question = "{0} [{1} by default]".format(str(question),str(i+1))
			if multi:
				str_selected = str_is_selected if val[0] in selected else str_not_selected
			else:
				str_selected = ''
			str_choices += ("{0:2}: {1:" + str(width) + "} {2}\n").format(str(i+1),val[1],str_selected)
		print_question(str_question,warning)
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

