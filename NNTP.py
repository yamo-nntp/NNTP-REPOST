#!/usr/bin/env python2.4
# -*- coding: iso-8859-15 -*-

"""NNTP module.
"""

# NNTP.py, NNTP client library
# Copyright (C) <2004>  <S.Ninin>

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

# See README file for how to reach the author and COPYING file for the full GPL license. 

# Full version of licence can be found at:
# http://www.gnu.org/licenses/gpl.txt 

#################################################################################
#
# $RCSfile: NNTP.py,v $
# $Revision: 1.2 $
# $Author: stephane $
# $Date: 2006/06/20 12:13:58 $
# $Id: NNTP.py,v 1.2 2006/06/20 12:13:58 stephane Exp $
#
#################################################################################

__version__ = "0.2"
__author__ = "Stéphane Ninin"
__date__ = "$Date: 2006/06/20 12:13:58 $"


__all__=["GroupInfo", "NNTPConnection", "NNTPGeneralError"]

import nntplib
from nntplib import NNTPError

# Append missing code values to nntplib LONGRESP array:
nntplib.LONGRESP.append("211")

DEBUGLIB = False

#--------------------------------------------------------------------------------

from Net import *

#--------------------------------------------------------------------------------


class NNTPGeneralError(Exception):
    """Base exception used in this module."""
    def __init__(self,args=None):
        self.args = args

#--------------------------------------------------------------------------------

class GroupInfo(object):

    """Basic Information on a group:
    first number & last number and count
    and posting, a boolean to tell if posting is enabled or disabled. 
    """
    
    def __init__(self,count=0,first=0,last=0,posting=True):
        self.__first = first
        self.__last = last
        self.__count = count
        
        self.__posting = posting

    def getFirst(self):
        """Returns first number in group."""
        return self.__first
    
    def getLast(self):
        """Returns last number in group."""
        return self.__last
    
    def getCount(self):
        """Returns count of articles in group.""" 
        return self.__count
    
    def getPosting(self):
        """Tell if posting allowed in group."""
        return self.__posting

    def __str__(self):
        return "first: " + str(self.__first) + \
               " last: " + str(self.__last) + \
               " count: " + str(self.__count) + \
               " posting: " + str(self.__posting)

#--------------------------------------------------------------------------------

class NNTPConnection(object):

    """ Class wich encapsulates NNTP commands.
    """
    
    CR = "\r"
    LF = "\n"
    CRLF = CR + LF

    def __init__(self,server):
        """Constructor. Parameter server must be of class NNTPConfig."""
        self.__server = server
        self.__lastResponse = None

# ---------------------------------------

    def getLastResponse(self):
        """Returns response given by last command."""
        return self.__lastResponse

    def setLastResponse(self,r):
        """Sets response given by last command."""
        self.__lastResponse = Response(r)
        
# ---------------------------------------

    def connect(self):
        """Connects to the server specified in constructor.""" 
        import socket
        server = self.__server
        address = server.getAddress()
        port = server.getPort()
        user = server.getUser()
        password = server.getPassword()
        try:
            self.__nntp = nntplib.NNTP(address,port=port,user=user,password=password,readermode=1)
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        except socket.gaierror,e:
            raise NNTPGeneralError, "Error: " + str(e[0]) + " -- " + e[1]
        return 

# ---------------------------------------

    def close(self):
        """Close the connection."""
        try:
            r = self.__nntp.quit()
        except NNTPError,e:
            raise NNTPGeneralError, e.response 
        self.setLastResponse(r)
        
# ---------------------------------------
    
    def help(self):
        """Returns help information as a list."""
        try:
            lst = self.__nntp.help()
        except NNTPError,e:
            raise NNTPGeneralError, e.response 
        self.setLastResponse(lst[0])
        return lst[1]
        
# ---------------------------------------

    def newgroups(self,date,time):
        """Returns dictionary of newgroups found on the server since given date
        in the form of a dictionary groupname > GroupInfo."""
        try:
            lst = self.__nntp.newgroups(date,time)
        except NNTPError,e:
            raise NNTPGeneralError, e.response 
        self.setLastResponse(lst[0])
        return self.convert_list(lst)
        
# ---------------------------------------
    
    def list(self,opt_keyword=None):
        """Return dictionary of newgroups found on the server
        in the form of a dictionary groupname > GroupInfo."""
        if (opt_keyword is None):
            try:
                lst = self.__nntp.list()
            except NNTPError,e:
                raise NNTPGeneralError, e.response 
            if DEBUGLIB:
                print 'type: ',type(lst)
            self.setLastResponse(lst[0])
            return self.convert_list(lst)

        if (opt_keyword == "OVERVIEW.FMT"):
            try:
                lst = self.__nntp.longcmd("LIST OVERVIEW.FMT")
            except NNTPError,e:
                raise NNTPGeneralError, e.response 
            self.setLastResponse(lst[0])
            return self.convert_list(lst)
        
# ---------------------------------------

    def group(self,gname):
        """Returns GroupInfo for the given group name."""
        try:
            lst = self.__nntp.group(gname)
        except NNTPError,e:
            raise NNTPGeneralError, e.response + ": " + gname 
        self.setLastResponse(lst[0])
        return GroupInfo(int(lst[1]),int(lst[2]),int(lst[3]))
            
# ---------------------------------------
        
    def stat(self,id=""):
        """Returns stat (article number and Message-ID) for the given id.
        id may be integer or of class ArticleIdentification."""
        try:
            if isinstance(id,ArticleIdentification):
                lst = self.__nntp.stat(id.getNumber())
            else:
                lst = self.__nntp.stat(id)
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        if DEBUGLIB:
            print lst
        self.setLastResponse(lst[0])
        return ArticleIdentification(lst[1],lst[2])
            
# ---------------------------------------
        
    def last(self):
        """Encapsulate last command. Return value is an ArticleIdentification object."""
        try:
            lst = self.__nntp.last()
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        return ArticleIdentification(lst[1],lst[2])

# ---------------------------------------
        
    def next(self):
        """Encapsulate next command. Return value is an ArticleIdentification object."""
        try:
            lst = self.__nntp.next()
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        return ArticleIdentification(lst[1],lst[2])

# ---------------------------------------
        
    def head(self,id=""):
        """Head command. Return value is a Message from email package."""
        try:
            if isinstance(id,ArticleIdentification):
                lst = self.__nntp.head(id.getNumber())
            else:
                lst = self.__nntp.head(str(id))
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        txt = self.as_text(lst[3])
        from email.Parser import Parser
        p = Parser()
        return p.parsestr(txt,True)
    
# ---------------------------------------
        
    def body(self,id=""):
        """Body command. Return value is a Message from email package."""
        try:
            if isinstance(id,ArticleIdentification):
                lst = self.__nntp.body(id.getNumber())
            else:
                lst = self.__nntp.body(str(id))
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        txt = self.as_text(lst[3])
        from email.Parser import Parser
        p = Parser()
        return p.parsestr(txt,False)

# ---------------------------------------
    
    def article(self,id=""):
        """Article command. Return value is a Message from email package."""
        try:
            if isinstance(id,ArticleIdentification):
                lst = self.__nntp.article(id.getNumber())
            else:
                if DEBUGLIB:
                    print id
                lst = self.__nntp.article(str(id))
                if DEBUGLIB:
                    print lst
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        txt = self.as_text(lst[3])
        from email.Parser import Parser
        p = Parser()
        return p.parsestr(txt,False)

# ---------------------------------------
        
    def slave(self):
        """Slave command. Not tested yet."""
        try:
            r = self.__nntp.slave()
        except NNTPError,e:
            raise NNTPGeneralError, e.response 
        self.setLastResponse(r)

# ---------------------------------------
    
    def post(self,message):
        """Post command. message can be
        -a string
        -a list of string
        -a Message from email package
        """

        import StringIO
        from email.Message import Message
        
        if type(message) == type(""):
            # tested
            msg = StringIO.StringIO(message)

        elif (type(message) == type([])) or (type(message) == type(())):
            # not yet tested
            msg = StringIO.StringIO(LF.join(message) + CRLF)

        elif isinstance(message,Message):
            # not yet tested
            from email.Generator import Generator
            msg = StringIO.StringIO()
            g = Generator(msg,mangle_from_=False)
            g.flatten(message)
            msg.seek(0)
        
        # NYI: test format of message instance
        
        try:
            r = self.__nntp.post(msg)
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        msg.close()
        
        self.setLastResponse(r)

# ---------------------------------------
    
    def date(self):
        """Date command. Returns a datetime from datetime module."""
        try:
            lst = self.__nntp.date()
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        dt = lst[0].split()
        dt = dt[1]

        from datetime import datetime
        return datetime(int(dt[0:4]),int(dt[4:6]),int(dt[6:8]),int(dt[8:10]),int(dt[10:12]),int(dt[12:14]))
    
# ---------------------------------------

    def xhdr(self,hdr,st=""):
        """chdr command. Not tested yet."""
        try:
            lst = self.__nntp.xhdr(hdr,st)
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        return lst[1]
    
# ---------------------------------------

    def listgroup(self,gname=""):
        """listgroup command. Not tested yet."""
        try:
            lst = self.__nntp.longcmd("LISTGROUP " + gname)
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])
        return lst[1]
        
# ---------------------------------------

    def newnews(self,group,date,time):
        """newnews command. Not tested yet."""
        try:
            lst = self.__nntp.newnews(group,date,time)
        except NNTPError,e:
            raise NNTPGeneralError, e.response
        self.setLastResponse(lst[0])

# ---------------------------------------

    def convert_list(self,lst):
        lstm = {}
        for l in lst[1]:
            if l[3] == 'y':
                posting = True
            else:
                posting = False
            last = int(l[1])
            first = int(l[2])
            count = (last - first) + 1
            gname = l[0]
            lstm[gname] = GroupInfo(count,first,last,posting) 
        return lstm

# ---------------------------------------

    def as_text(lst):
        return NNTPConnection.LF.join(lst)
    as_text = staticmethod(as_text)

# ---------------------------------------

    def checkRequiredHeaders(message):
        required_fields = ["From","Date","Newsgroups","Subject","Message-ID","Path"]
        for f in required_fields:
            if not message.has_key(f):
                return False
        return True
    checkRequiredHeaders = staticmethod(checkRequiredHeaders) 

#--------------------------------------------------------------------------------

#################################################################################
#
# $Log: NNTP.py,v $
# Revision 1.2  2006/06/20 12:13:58  stephane
# Added PECrypt + minor changes
#
# Revision 1.1  2005/07/15 14:01:52  stephane
# Original source code
#
#
#################################################################################

