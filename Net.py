#!/usr/bin/env python2 
# -*- coding: iso-8859-15 -*-

"""Net module.
"""

# Net.py
# Copyright (C) <2005> <Stéphane Ninin>

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
# $RCSfile: Net.py,v $
# $Revision: 1.2 $
# $Author: stephane $
# $Date: 2006/06/20 12:13:58 $
# $Id: Net.py,v 1.2 2006/06/20 12:13:58 stephane Exp $
#
#################################################################################

__version__ = ""
__author__ = "Stéphane Ninin"
__date__ = "$Date: 2006/06/20 12:13:58 $"

__all__ = ["NetConfig", "POPConfig", "SMTPConfig", "NNTPConfig", "ArticleIdentification", "Response"]

DEBUGLIB = False

# -------------------------------------------------------------------------------

class NetConfig(object):
    
    """ Base Network Configuration which encapsulate
    host address
    user login and password
    and port.
    Derived classes set default port.
    """

    def __init__(self,address,user,password,port):
        self.__address = address
        self.__user = user
        self.__password = password
        self.__port = port

# ---------------------------------------

    def getAddress(self):
        """Returns the host address"""
        return self.__address

    def getUser(self):
        """Returns the user login"""
        return self.__user

    def getPassword(self):
        """Returns the user port"""
        return self.__password

    def getPort(self):
        """Returns the host port"""
        return self.__port

# ---------------------------------------

    def Clone(self):
        return self.__class__(self.getAddress(),
                              self.getUser(),
                              self.getPassword(),
                              self.getPort())
        
# ---------------------------------------

    def setAddress(self,address):
        """Sets the host address"""
        self.__address = address

    def setUser(self,user):
        """Sets the user login"""
        self.__user = user

    def setPassword(self,password):
        """Sets the user password"""
        self.__password = password

    def setPort(self,port):
        """Sets the host port"""
        self.__port = port

# -------------------------------------------------------------------------------

class POPConfig(NetConfig):

    def __init__(self,address,user,password,port=110):
        NetConfig.__init__(self,address,user,password,port)

# -------------------------------------------------------------------------------

class SMTPConfig(NetConfig):

    def __init__(self,address,user,password,port=25):
        NetConfig.__init__(self,address,user,password,port)

# -------------------------------------------------------------------------------

class NNTPConfig(NetConfig):

    def __init__(self,address,user,password,port=119):
        NetConfig.__init__(self,address,user,password,port)

# -------------------------------------------------------------------------------

class Response(object):
    """Response returned by servers""" 
    def __init__(self,fline):
        if DEBUGLIB:
            print fline
            
        self.__fullline = fline
        fline = fline.strip()

        i = fline.find(" ")
        if DEBUGLIB:
            print i
        if (i != -1):
            self.__code = int(fline[0:i])
            self.__line = fline[i+1:]
        

    def getCode(self):
        """Return code of the response"""
        return self.__code

    def getLine(self):
        """Return description of the response"""
        return self.__line

    def getFullLine(self):
        """Return code and description of the response"""  
        return self.__fullline

    def __str__(self):
        return self.__fullline

#--------------------------------------------------------------------------------

class ArticleIdentification(object):

    def __init__(self,nid,mid):
        self.__nid = nid
        self.__mid = mid
            
    def getNumber(self):
        return self.__nid
    
    def getMID(self):
        return self.__mid

    def __str__(self):
        return "Number: " + self.__nid + " - M-Id: " + self.__mid

#--------------------------------------------------------------------------------

#################################################################################
#
# $Log: Net.py,v $
# Revision 1.2  2006/06/20 12:13:58  stephane
# Added PECrypt + minor changes
#
# Revision 1.1  2005/07/15 13:42:11  stephane
# Original source code
#
#
#################################################################################
