#!/usr/bin/env python2 
# -*- coding: iso-8859-15 -*-

#PEcrypt - use a string key to encrypt/decrypt another string
#        - Simon Peverett - January 2004
#        - Raymond Hettinger, 2004/02/08
#
# taken from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/266586

#################################################################################
#
# $RCSfile: PECrypt.py,v $
# $Revision: 1.1 $
# $Author: stephane $
# $Date: 2006/06/20 12:13:58 $
# $Id: PECrypt.py,v 1.1 2006/06/20 12:13:58 stephane Exp $
#
#################################################################################

import random

class PEcrypt(object):

    def __init__(self, aKey):
        self.rng = random.Random(aKey)

    def Crypt(self, aString):
        rand = self.rng.randrange
        crypted = [chr(ord(elem)^rand(256)) for elem in aString]
        return ''.join(crypted)

if __name__ == "__main__":

    def strToHex(aString):
        hexlist = ["%02X " % ord(x) for x in aString]
        return ''.join(hexlist)

    keyStr = "This is a key"
    testStr = "The quick brown fox jumps over the lazy dog!"

    print "String:", testStr
    testStr = PEcrypt(keyStr).Crypt(testStr)
    print "Encrypted string:", testStr
    print "Hex    : ", strToHex(testStr)    
    testStr = PEcrypt(keyStr).Crypt(testStr)
    print "Decrypted string:", testStr

#################################################################################
#
# $Log: PECrypt.py,v $
# Revision 1.1  2006/06/20 12:13:58  stephane
# Added PECrypt + minor changes
#
#
#################################################################################
