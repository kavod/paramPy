#!/usr/bin/env python
#encoding:utf-8

import sys
import paramPy

tracker_id = paramPy.ConfigElement(
		id="id",
		type='text',
		label='Torrents provider',
		placeholder="Indicate your torrents provider",
		required=False,
		choices={'t411':'T411','kickass':'KickAss'},
		default=None,
		trigger={'kickass':'NoLogin',None:'NoLogin'}
		)
export = tracker_id.toJSON()
tracker_id1 = paramPy.ConfigElementFromJSON(export)

tracker_user = paramPy.ConfigElement(
		id="user",
		type='text',
		label='Torrents provider username',
		placeholder="Indicate your torrents provider user",
		required=False,
		choices=[],
		default=None
		)

tracker_password = paramPy.ConfigElement(
		id="password",
		type='password',
		label='Torrents provider password',
		placeholder="Indicate your torrents provider password",
		required=False,
		choices=[],
		default=None
		)

email_enable = paramPy.ConfigElement(
		id="email_enabled",
		type="boolean",
		label="Email activation",
		placeholder="Activate email notification?",
		required="True",
		choices=[],
		default=False
		)

version = paramPy.ConfigElement(
		id="version",
		type="text",
		trigger={'*':'disabled'}
		)
version.setValue("2.0")

trigger = [
		{'src_id':'id','src_status':'NoLogin','dst_id':'login','dst_status':'disabled'}
		]

tracker_login = paramPy.Param(
		id='login',
		label='Torrent provider login',
		items=[tracker_user,tracker_password],
		trigger={}
		)

param_tracker = paramPy.ParamMulti(
		id='tracker',
		label="Torrent provider",
		items=[tracker_id1,tracker_login],
		trigger=trigger
		)

param = paramPy.Param(
		id='conf',
		label='Configuration',
		items=[version,param_tracker,email_enable]
		)
values = param.getValues()
export = param.toJSON()
param1 = paramPy.ParamFromJSON(export)
param1.loadValuesFromJSON({'conf':values})

param1.loadFromFile('test.json')
print param1.getValues()
print "ok"
param1.cliChange()
param1.saveToFile("test.json")
"""param1.cliPrompt()
print param1.getValues()
param1.saveToFile("test.json")"""
