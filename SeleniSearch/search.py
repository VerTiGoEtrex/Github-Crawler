from selenium import webdriver
import random
import time
import re

SEARCHURL = 'https://github.com/search'
SEARCHSTRING = 'AWSSecretKey'

ACCESSKEYREGEX = r'AKI[A-Z0-9]{17}(?![A-Z0-9])'
SECRETKEYREGEX = r'[A-Za-z0-9+/]{40}'

SLEEPTIMEBOUND = (6, 18)

def rateLimit():
    sleepTime = random.randint(*SLEEPTIMEBOUND)
    print "[-] Sleeping for {} seconds".format(sleepTime)
    time.sleep(sleepTime)

def main():
    print "[+] Starting GitHub crawler!"
    driver = webdriver.Chrome(executable_path="./chromedriver")

    # Load search home page and find search box
    driver.get(SEARCHURL)
    rateLimit()
    assert 'Code Search' in driver.title
    elem = driver.find_element_by_name('q')
    elem.send_keys(SEARCHSTRING)
    elem.submit()

    # Set search results to only search code (default is repositories)
    rateLimit()
    assert 'Search' in driver.title
    elem = driver.find_element_by_xpath('//*[@id="container"]/div[2]/div/div[1]/nav/a[2]')
    assert 'Code' in elem.text
    elem.click()

    # Set search results to use 'most recently indexed' option
    rateLimit()
    assert 'Search' in driver.title
    elem = driver.find_element_by_xpath('//*[@id="container"]/div[2]/div/div[2]/div[1]/div/span')
    elem.click()
    elem = driver.find_element_by_xpath('//*[@id="container"]/div[2]/div/div[2]/div[1]/div/div/div/div[2]/a[2]')
    assert 'Recently indexed' in elem.find_element_by_xpath('.//span[contains(@class, "select-menu-item-text")]').get_attribute('innerHTML')
    elem.click()

    # Parse through the search results
    keySet = set()
    while True:
        print '[-] Loading next results page'
        rateLimit()
        assert 'Search' in driver.title
        results = driver.find_element_by_xpath('//*[@id="code_search_results"]')
        codeDivs = results.find_elements_by_xpath('.//div[contains(@class, "code-list-item")]')
        for codeDiv in codeDivs:
            repoTitle = codeDiv.find_element_by_xpath('.//p/a').text
            secretKey = None
            accessKey = None
            codeLines = codeDiv.find_elements_by_xpath('.//td[contains(@class, "blob-code")]')
            for codeLine in codeLines:
                lineContents = codeLine.get_attribute('innerHTML')
                accessKeyMatch = re.search(ACCESSKEYREGEX, lineContents)
                if accessKeyMatch is not None:
                    accessKey = accessKeyMatch.group(0)
                secretKeyMatch = re.search(SECRETKEYREGEX, lineContents)
                if secretKeyMatch is not None:
                    secretKey = secretKeyMatch.group(0)
            if accessKey is not None and secretKey is not None:
                print '[*] Found creds in {}: Access Key={}, Secret Key={}'.format(repoTitle, accessKey, secretKey)
                keySet.add((accessKey, secretKey))
            elif accessKey is not None:
                print '[*] Found only one cred in {}: Access Key={}'.format(repoTitle, accessKey)
            elif secretKey is not None:
                print '[*] Found only one cred in {}: Secret Key={}'.format(repoTitle, secretKey)
        try:
            nextButton = results.find_element_by_xpath('.//a[@class="next_page"]')
            nextButton.click()
        except:
            print '[-] Couldn\'t find next button'
            break
    print '[+] Done scanning GitHub results!'
    for x in keySet:
        print x
    driver.close()


if __name__=='__main__':
    main()
