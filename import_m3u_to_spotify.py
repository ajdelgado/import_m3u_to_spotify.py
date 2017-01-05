#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import_m3u_to_spotify.py
# Description: Creates a playlist in Spotify based on a M3U playlist.
# https://developer.spotify.com/web-api/authorization-guide/#client_credentials_flow
# https://developer.spotify.com/web-api/get-list-users-playlists/
CONFIG=dict()
CONFIG['baseurl']='https://api.spotify.com'
CONFIG['clientidfile']=''
CONFIG['clientid']=''
CONFIG['clientsecret']=''
CONFIG['debug']=0
CONFIG['playlistfile']=''
CONFIG['config-file']=''
CONFIG['syslog']=True
CONFIG['spotifyuser']=''
def GetArguments():
  global CONFIG
  import sys
  for arg in sys.argv:
    if arg == "-v" or arg == "-d" or arg == "--verbose" or arg == "--debug":
      if isinstance( CONFIG['debug'], str):
        CONFIG['debug']=int(CONFIG['debug'])+1
      else:
        CONFIG['debug']=CONFIG['debug']+1
      CONFIG['debug']=CONFIG['debug'] + 1
      Message("Increased debug level to %s" % CONFIG['debug'])
    elif arg == "-h" or arg == "--help":
      Usage()
    elif arg.find("=")>-1:
      aarg=arg.split("=",1)
      if aarg[0]=="--config-file":
        CONFIG['config-file']=aarg[1]
        Message("Will read config file '%s' (after processing command line arguments)" % aarg[1])
    if CONFIG['config-file']!="":
      ReadConfigFile(CONFIG['config-file'])
def Message(TEXT,FORCE=False,LEVEL=0,SYSLOG=False):
  global CONFIG
  import syslog
  try:
    TEXT=TEXT.decode("utf8")
  except:
    try:
      TEXT=TEXT.encode("ascii", 'replace')
    except:
      TEXT=TEXT
  #To a log file
  #if not os.path.exists(os.path.dirname(CONFIG['logfile'])):
    #os.mkdir(os.path.dirname(CONFIG['logfile']))
  #logf=open(CONFIG['logfile'],"a")
  #try:
    #logf.write(TEXT)
  #except:
    #TEXT=TEXT.encode("utf8")
    #logf.write(TEXT)
  #logf.close()
  #To syslog
  if CONFIG['syslog']:
    syslog.syslog(TEXT)
  #To screen
  if int(CONFIG['debug']) > LEVEL or FORCE:
    print TEXT
def ReadConfigFile(configfile):
  global CONFIG
  import os
  if not os.path.exists(configfile):
    Message("The configuration file '%s' doesn't exist" % configfile)
    return False
  f_config=open(configfile,"r")
  for line in f_config:
    a_line=line.split("=",1)
    if len(a_line)>1:
      for k in CONFIG.iterkeys():
        if a_line[0]==k:
          CONFIG[k]=a_line[1].replace(chr(13),"").replace(chr(10),"").strip('"')
          if a_line[0].find("pass")==-1:
            Message("Setting option '%s' as '%s' from config file" % (a_line[0],CONFIG[k]))
  f_config.close()
def SpotifyAuthorize():
  import requests
  import urllib
  import base64
  global CONFIG
  authurl='https://accounts.spotify.com/api/token'
  grant_type='client_credentials'
  #It have to be added to the client valid redirect URIs
  authorization=base64.encodestring(CONFIG['client_id'] + CONFIG['client_secret'])
  response=requests.get(url=authurl,headers={"Authorization":authorization})
  if response.status_code != 200:
    Message('Error %s authorizing. Response: %s' % ( response.status_code,response.text),FORCE=True)
    return False
  return True
def ReadClientAuth():
  global CONFIG
  import os
  if not os.path.exists(CONFIG['clientidfile']):
    Message("The file containing the client ID '%s' doesn't exist" % CONFIG['clientidfile'])
    return False
  f=open(CONFIG['clientidfile'],"r")
  CONFIG['clientid']=f.read().strip('\n')
  f.close
  if CONFIG['clientid'] == '':
    Message("Nothing read from the client ID file '%s'." % CONFIG['clientidfile'])
    return False
  else:
    Message("Client id is '%s'" % CONFIG['clientid'])
  return True
def ReadPlayList():
  global CONFIG
  import os
  if not os.path.exists(CONFIG['playlistfile']):
    Message("The file containing the M3U playlist '%s' doesn't exist" % CONFIG['playlistfile'])
    return False
  f=open(CONFIG['playlistfile'],'r')
  CONFIG['playlist']=list()
  for line in f:
    CONFIG['playlist'].append(line)
  f.close()
  return True
Message('Getting configuration.')
GetArguments()
if CONFIG['clientidfile'] != '':
  Message('Reading client identification from file "%s"' % CONFIG['clientidfile'])
  if not ReadClientAuth():
    Message('Failed.')
  else:
    Message('Ok.')
Message('Authenticating with Spotify.')
if SpotifyAuthorize():
  Message('Ok.')
  Message('Reading M3U playlist.')
  if ReadPlayList():
    Message('Ok.')
  else:
    Message('Failed.')
else:
  Message('Failed.')
