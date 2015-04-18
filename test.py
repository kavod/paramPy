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

trigger = [
		{'src_id':'id','src_status':'NoLogin','dst_id':'user','dst_status':'disabled'},
		{'src_id':'id','src_status':'NoLogin','dst_id':'password','dst_status':'disabled'}
		]

param_tracker = paramPy.ParamMulti(
		id='tracker',
		label="Torrent provider",
		items=[tracker_id,tracker_user,tracker_password],
		trigger=trigger
		)

param = paramPy.Param(
		id='conf',
		items=[param_tracker]
		)

param.cliPrompt()
print param.getValues()
param.loadValuesFromJSON({'conf':{'tracker':[{'id':'t411','user':'niorf'}]}})
print param.getValues()
print len(param_tracker)
