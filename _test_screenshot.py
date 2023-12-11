from selenium import webdriver
import chromedriver_autoinstaller
import sys


chromedriver_autoinstaller.install()

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

driver.get('https://code-maven.com/slides/python/selenium-headless-screenshot')
print(driver.title)
driver.get_screenshot_as_file(r'out\screenshot.png')
driver.close()
