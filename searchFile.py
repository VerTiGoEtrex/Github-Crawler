#!/usr/bin/env python

import sys
import re
import sqlite3

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
    
ssh_RE = re.compile(r"sshpass\s+-p\s+\S+\s+ssh.*")
rdesktop_RE = re.compile(r"rdesktop.*-p\s+\S+.*")
def extractHardcodedPasswords(text):
    print re.findall(ssh_RE, text)
    sshPasswords = re.findall(ssh_RE, text)
    rdesktopPasswords = re.findall(rdesktop_RE, text)
    
    return sshPasswords + rdesktopPasswords

    
def findSecrets(text, user, repo, dbConn, dbCur):
    try:

        # Check for various kinds of secrets (by which I mean one kind of secret)
        # and save to SQLite3

        accessID, key = extractAWSKey(text)

        if accessID and key:
            dbCur.execute('INSERT INTO AWSKeys VALUES("' + accessID + '", "' + key + '", "' + user + '", "' + repo + '");')
            dbConn.commit()
            sys.stderr.write("Found an AWS key!\n")
            
        passwords = extractHardcodedPasswords(text)
        for p in passwords:
            sys.stderr.write(p + "\n")
        
    except:
        pass

def main():
    url = raw_input("url: ")
    dbConn = sqlite3.connect("secrets.db")
    dbCur = dbConn.cursor()

    findSecrets(url, "fppro", "Testing", dbConn, dbCur)

if __name__=='__main__':
    main()
