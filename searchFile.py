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

def extractAWSKey(text):
    keys = []

    accessID_RE = re.compile(r'AKI[0-9A-Z]{17}')
    key_RE = re.compile(r'([^0-9A-Za-z=+/]|^)([0-9A-Za-z=+/]{40})([^0-9A-Za-z=+/]|$)')

    access = re.search(accessID_RE, text)
    key = re.search(key_RE, text)

    if access and key:
        return (access.group(0), key.group(2))
    else:
        return (None, None)

    #if re.search(, text):
    #    keys += [m[1] for m in re.findall(keyRE, text)]
    #return keys

def findSecrets(url, user, repo, dbConn, dbCur):
    try:
        text = downloadURL(url)

        # Check for various kinds of secrets (by which I mean one kind of secret)
        # and save to SQLite3
        
        if "credentials2.txt" in url:
            print "[!] Got the key file with the following contents:"
            print text
            print
        
        accessID, key = extractAWSKey(text)

        if accessID and key:
            dbCur.execute('INSERT INTO AWSKeys VALUES("' + accessID + '", "' + key + '", "' + user + '", "' + repo + '");')
            dbConn.commit()
            sys.stderr.write("Found an AWS key!\n")
    except:
        pass

def main():
    url = raw_input("url: ")
    dbConn = sqlite3.connect("secrets.db")
    dbCur = dbConn.cursor()

    findSecrets(url, "fppro", "Testing", dbConn, dbCur)


    #fileName = raw_input("file name: ")
    #with open(fileName, 'r') as f:
    #    s = f.read()
    #    if re.match(privateKeyRE, s):
    #        print "Match!"
    #    else:
    #        print "Not a match..."

if __name__=='__main__':
    main()
