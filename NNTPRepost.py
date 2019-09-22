#!/usr/bin/env python2.4
# -*- coding: iso-8859-15 -*-

""" NNTP simple repost
"""

# 
# Copyright (C) <2005>  <S.Ninin>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# See README.txt file for how to reach the author and COPYING.txt file for the full GPL license. 

# Full version of licence can be found at:
# http://www.gnu.org/licenses/gpl.txt 

#################################################################################
#
# $RCSfile: NNTPRepost.py,v $
# $Revision: 1.2 $
# $Author: stephane $
# $Date: 2006/06/20 12:24:09 $
# $Id: NNTPRepost.py,v 1.2 2006/06/20 12:24:09 stephane Exp $
#
#################################################################################

__version__ = "1.0"
__author__ = "Stéphane Ninin"
__date__ = "$Date: 2006/06/20 12:24:09 $"

from Net import *
from NNTP import NNTPConnection

from email.Message import Message 
from PECrypt import PEcrypt

import os
import os.path
import sys

PASSWORDKEY='lkjfwskhwfksnlnfsdjnwfnk'

#--------------------------------------------------------------------------------

def getRunDir():
     try:
         sys.frozen
     except AttributeError:
         path = sys.argv[0]
     else:
         path = sys.executable

	
      print 'pwd ' + os.path.dirname(os.path.abspath(path))
     return os.path.dirname(os.path.abspath(path))

#----------------------------------------

def getAbsoluteFilename(filename):
    scriptdirectory = getRunDir()
    return os.path.join(scriptdirectory,filename)
    
#--------------------------------------------------------------------------------

class NNTPRepost(object):
    
    def __init__(self,cfg,reposter):
        self.__cfg = cfg
        self.__reposter = reposter

    def start(self):
        self.__nntpc = NNTPConnection(self.__cfg)
        self.__nntpc.connect()

    def close(self):
        self.__nntpc.close()
        
    def _getCancelMsg(self):
        self.__cancelMsg = self.__nntpc.head(self.__cancelid)
    
    def _getOriginalMsg(self):
        hcontrol = self.__cancelMsg['Control']
        omsgid = hcontrol.split()[1]
        self.__origMsg = self.__nntpc.article(omsgid)
    
    def repost(self,cancelid):
        self.__cancelid = cancelid

        self._getCancelMsg()
        self._getOriginalMsg()

        text1 = self.__origMsg.get_payload()
        text2 = self.__cancelMsg.as_string() 
         
        newmsg = Message()
        newmsg['Sender'] = self.__reposter
        
        newmsg['Newsgroups'] = self.__origMsg['Newsgroups']
        newmsg['From'] = self.__origMsg['From']
        newmsg['Subject'] = '[REPOST] ' + self.__origMsg['Subject'] 
        
        if self.__origMsg.has_key('References'):
            newmsg['References'] =  self.__origMsg['References']
        
        newmsg['Supersedes'] = self.__origMsg['Message-ID']
        
        if self.__origMsg.has_key('Followup-To'):    
            newmsg['Followup-To'] = self.__origMsg['Followup-To']
        
        if self.__origMsg.has_key('Reply-To'):    
            newmsg['Reply-To'] = self.__origMsg['Reply-To']
            
        if self.__origMsg.has_key('Organization'):    
            newmsg['Organization'] = self.__origMsg['Organization']
        
        newmsg['X-Original-Path'] = self.__origMsg['Path']

    
        from datetime import datetime
        now = datetime.now()
        
        s1 = now.strftime("%y%j%H%M%S.")
        
        s2 = self.__origMsg['Message-ID']
        s2 = s2[1:-1]

        newmsg['Message-ID'] = '<REPOST.' + s1 + s2 + ">"
        newmsg['X-Original-Message-ID'] = self.__origMsg['Message-ID']
                        
        if self.__origMsg.has_key('NNTP-Posting-Host'):    
            newmsg['X-Original-NNTP-Posting-Host'] = self.__origMsg['NNTP-Posting-Host']

        if self.__origMsg.has_key('NNTP-Posting-Date'):    
            newmsg['X-Original-NNTP-Posting-Date'] = self.__origMsg['NNTP-Posting-Date']
        
        newmsg['X-Original-Date'] = self.__origMsg['Date']

        newmsg['X-Comment'] = 'Reposted by NNTPRepost ' + self.__reposter
        newmsg.add_header('X-Comment', 'The following Usenet article was cancelled') 
        newmsg.add_header('X-Comment', 'more than likely by someone other than the original poster.')  
        newmsg.add_header('X-Comment', 'Please see the end of this posting for a copy of the cancel.')
        newmsg.add_header('X-Comment', self.__reposter)
                 
        newmsg['X-Reposted-By'] = newmsg['Sender']
        newmsg['Path'] = '!NNTPRepost'
        
        newmsg['X-No-Archive'] = 'yes'

        if self.__origMsg.has_key('MIME-Version'):    
            newmsg['MIME-Version'] = self.__origMsg['MIME-Version']

        if self.__origMsg.has_key('Content-Type'):    
            newmsg['Content-Type'] = self.__origMsg['Content-Type']

        if self.__origMsg.has_key('Content-Transfer-Encoding'):    
            newmsg['Content-Transfer-Encoding'] = self.__origMsg['Content-Transfer-Encoding']
        
        text = text1 + "\n========= WAS CANCELLED BY =======:\n" + text2
        text = text1 + "\n-- \n========= WAS CANCELLED BY =======:\n" + text2

        newmsg.set_payload(text)

        self.__nntpc.post(newmsg)
        
#--------------------------------------------------------------------------------

class MultiRepost(object):

    def __init__(self,filename):

        self.__filename = getAbsoluteFilename(filename)
        
        import ConfigParser
        self.__cfg = ConfigParser.ConfigParser()

        self.__cfg.read(self.__filename)

        saddress = self.__cfg.get('Server','Address') 
                
        if self.__cfg.has_option('Server','Port'):
            sport = self.__cfg.getint('Server','Port')
        else:
            sport = 119
            
        if self.__cfg.has_option('Server','User'):
            user = self.__cfg.get('Server','User')
        else:
            user = None

        if self.__cfg.has_option('Server','Password'):
            encodedpassword = self.__cfg.get('Server','Password')
        else:
            encodedpassword = None

        if encodedpassword is None:
            password =  None
        else:
            import base64
            cryptedpassword = base64.standard_b64decode(encodedpassword)
            pe = PEcrypt(PASSWORDKEY)
            password = pe.Crypt(cryptedpassword)
            
        self.__reposter = self.__cfg.get('Server','Reposter')

        self.__nntpcfg = NNTPConfig(saddress,user,password,sport)


    def start(self):
        self.__repost = NNTPRepost(self.__nntpcfg,self.__reposter)
        self.__repost.start()
        
    def close(self):
        self.__repost.close()

    def repost(self,cancelids):
        self.__cancelids = cancelids
        for cancelid in self.__cancelids:
             try:
                  self.__repost.repost(cancelid)
             except:
                  print 'Problem with repost: ' + cancelid
                  
#--------------------------------------------------------------------------------

def advancedRepost(filename):
    
    print "Enter Cancel Message-ID's, one by line, finish with END"

    cancelids = []
    while True:
        cancelid = raw_input()
        if cancelid == 'END':
            break
        else:
            cancelids.append(cancelid)

    if len(cancelids) > 0:
        mr = MultiRepost(filename)
        connected = False
        try:
             mr.start()
             connected = True
             try:
                  mr.repost(cancelids)
             except:
                  print 'Problems during repost.'
        finally:
             if connected:
                  mr.close()

#--------------------------------------------------------------------------------

def initConfigFile(filename):
    filename = getAbsoluteFilename(filename)
    reposter = raw_input('Reposter (name and email address) ?\n')
    server = raw_input('Server address ?\n')
    user = raw_input('User name ?\n')
    import getpass
    password = getpass.getpass('Password ?')

    reposter = reposter.strip()
    server =  server.strip()
    user = user.strip()
    password = password.strip()

    pe = PEcrypt(PASSWORDKEY)
    cryptedpassword = pe.Crypt(password)
    
    import base64
    encodedpassword =  base64.standard_b64encode(cryptedpassword)
        
    f = file(filename,'w')

    f.write('[Server]\n')

    f.write('Address: ' + server + '\n')
    f.write('Port: 119\n')

    if user != '':
        f.write('User: ' + user + '\n')

    if reposter != '':
        f.write('Reposter: ' + reposter + '\n')
        
    f.write('Password: ' + encodedpassword + '\n')
        
    f.close()

#-------------------------------------------------------------------------------- 

def testConfigFile(filename):
    filename = getAbsoluteFilename(filename)

    import ConfigParser

    cfg = ConfigParser.ConfigParser()
    cfg.read(filename)

    print cfg.get('Server','Address')
    print cfg.get('Server','User')
    print cfg.get('Server','Reposter')
    print cfg.getint('Server','Port')

    encodedpassword = cfg.get('Server','Password')

    import base64
    cryptedpassword = base64.standard_b64decode(encodedpassword)

    pe = PEcrypt(PASSWORDKEY)
    password = pe.Crypt(cryptedpassword)
    print password

#--------------------------------------------------------------------------------

def simpleRepost():
    cmsgid = raw_input('Cancel Message-ID ?\n')
    
    server = raw_input('Server address ?\n')
    user = raw_input('User name ?\n')
    password = raw_input('Password ?\n')

    cfg = NNTPConfig(server,user,password)
    
    reposter = NNTPRepost(cfg,'Stéphane Ninin <stefnin@alussinan.org>')
    reposter.start()
    reposter.repost(cmsgid)
    reposter.close()

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    
    filename = 'config.ini'
    
    if len(sys.argv) == 1:
        advancedRepost(filename)
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'init':
            initConfigFile(filename)
        elif sys.argv[1] == 'test':
            testConfigFile(filename)
        else:
            sys.exit('Syntax error. Syntax is NNTPRepost or NNTPRepost init or NNTPRepost test.')
    else:
        sys.exit('Too many parameters. Syntax is NNTPRepost or NNTPRepost init or NNTPRepost test.')
    
    
#################################################################################
#
# $Log: NNTPRepost.py,v $
# Revision 1.2  2006/06/20 12:24:09  stephane
# Added support for multi reposts.
#
# Revision 1.1  2005/07/28 13:09:41  stephane
# Original source code
#
#
#################################################################################
