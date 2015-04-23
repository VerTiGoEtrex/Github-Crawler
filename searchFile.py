#!/usr/bin/env python

import sys
import re
import urllib2
import sqlite3

def downloadURL(url):
    r = urllib2.urlopen(url)
    return r.read()

def isSSLKey(text):
    privateKeyRE = re.compile(r'-----BEGIN (RSA )?PRIVATE KEY-----\n([0-9A-Za-z=+/\n]{100,})-----END (RSA )?PRIVATE KEY-----')
    return re.match(privateKeyRE, text) is not None

def isBitcoin(url):
    return url.find("wallet.dat") >= 0

accessID_RE = re.compile(r'(AKIA[0-9A-Z]{16})[^0-9A-Z]')
key_RE = re.compile(r'([^0-9A-Za-z=+/]|^)([0-9A-Za-z=+/]{40})([^0-9A-Za-z=+/]|$)')

def extractAWSKey(text):
    access = re.search(accessID_RE, text)
    key = re.search(key_RE, text)

    if access and key:
        return (access.group(1), key.group(2))
    else:
        return (None, None)
    
ssh_RE = re.compile(r"sshpass\s+-p.*ssh.*")
rdesktop_RE = re.compile(r"rdesktop.*-p\s+\S+.*")
def extractHardcodedPasswords(text):
    sshPasswords = re.findall(ssh_RE, text)
    rdesktopPasswords = re.findall(rdesktop_RE, text)
    
    return sshPasswords + rdesktopPasswords


def findSecrets(url, user, repo, dbConn, dbCur):
    try:
        text = downloadURL(url)

        # Check for various kinds of secrets (by which I mean one kind of secret)
        # and save to SQLite3


        accessID, key = extractAWSKey(text)

        if accessID and key:
            dbCur.execute('INSERT INTO AWSKeys (AccessID, SecretKey, user, repo) VALUES("' + accessID + '", "' + key + '", "' + user + '", "' + repo + '");')
            dbConn.commit()
            sys.stderr.write("Found an AWS key!\n")
            
        passwords = extractHardcodedPasswords(text)
        for p in passwords:
            dbCur.execute('INSERT INTO Passwords (SecretString, user, repo) VALUES("' + p + '", "' + user + '", "' + repo + '");')
            dbConn.commit()
            sys.stderr.write("Found a password!\n")
        
    except:
        pass

def main():
    f = open(raw_input("file: "), 'r')
    text = f.read()
    f.close()
    dbConn = sqlite3.connect("secrets.db")
    dbCur = dbConn.cursor()

    findSecrets(text, "fppro", "Testing", dbConn, dbCur)


    #fileName = raw_input("file name: ")
    #with open(fileName, 'r') as f:
    #    s = f.read()
    #    if re.match(privateKeyRE, s):
    #        print "Match!"
    #    else:
    #        print "Not a match..."

if __name__=='__main__':
    main()
