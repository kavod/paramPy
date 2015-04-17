#!/usr/bin/env python
#encoding:utf-8

import sys
import paramPy

p1 = paramPy.PointCusto(id="id",type='text',label='Torrents provider',placeholder="Indicate your torrents provider",required=True,choices={'t411':'T411','kickass':'KickAss'},default='t411',trigger={'t411':'UserRequired'})
p2 = paramPy.PointCusto(id="user",type='text',label='Torrents provider username',placeholder="Indicate your torrents provider user",required=False,choices=[],default=None)
p3 = paramPy.PointCusto(id="password",type='password',label='Torrents provider password',placeholder="Indicate your torrents provider password",required=False,choices=[],default=None)
param_tracker = paramPy.ParamMulti('tracker',items=[p1,p2,p3])
param = paramPy.Param('conf',items=[param_tracker])
param.cliPrompt()
print param[0].values[0][0].getStatus()
sys.exit()
param.loadValuesFromJSON({'conf':{'tracker':[{'id':'t411','user':'niorf'}]}})
print param.getValues()
print len(param_tracker)
