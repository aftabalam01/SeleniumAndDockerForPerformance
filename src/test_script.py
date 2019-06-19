from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver import ChromeInstance
from perfutils import BrowserPerformance
from logger import Logger
from config import CONFIG
import os
import time
import unittest


Logger=Logger()
logger = Logger.getLogger(name='Mytableauloadtest',level=CONFIG.get('logging').get('level') )

class LoadUrls(unittest.TestCase):

    def test_load_urls(self,event, context):
        # TODO implement

        def get_current_page(driver):
            return driver.title

        instance = ChromeInstance()
        browser = BrowserPerformance(webdriver=instance.driver, env=os.environ.get('ENV',CONFIG.get('default_env')),application="Mytableau.com", inputlogger=logger)
        if 'homepage' in event.keys():
            instance.driver.get(event['homepage'])
            instance.wait_for(instance.page_has_loaded)
            page_data = get_current_page(instance.driver)
            browser.set_page_context(action='LoginPage', testname=__name__, pageContext='LoginPage')
            browser.capture_navigation_timing()
            if "Log In" in get_current_page(instance.driver):
                username = instance.driver.find_element(By.ID,"os_username")
                password = instance.driver.find_element(By.ID,"os_password")
                username.send_keys(os.getenv('LOGIN_ID'))
                password.send_keys(os.getenv('LOGIN_PASSWD'))
                login = instance.driver.find_element(By.ID,"loginButton")
                login.click()
                instance.wait_for(instance.page_has_loaded)
                page_data = get_current_page(instance.driver)
                print("logged {}".format(page_data))
                browser.set_page_context(action='loginButton', testname=__name__, pageContext='LoginPage')
                browser.capture_navigation_timing()
            url_count = len(event['uris'])
            i_count = 0
            for pages in event['uris']:
                page = instance.driver.get(event['homepage']+pages)
                page_data = get_current_page(instance.driver)
                print("pages {}".format(page_data))
                browser.set_page_context(action=page_data, testname=__name__, pageContext='LoginPage')
                browser.capture_navigation_timing()
                
                if i_count%5 == 0 or i_count == url_count : # either fifth urls or last one from this list given to user will be edited
                    try:
                        edit = instance.driver.find_element(By.ID,"editPageLink") # open edit
                        edit.click()
                        # check if Edit in tittle  
                        if "Edit" in get_current_page(instance.driver):
                            # somerandom edit
                            page.send_keys('loadtestedit')
                            # find publish button
                            publish = instance.driver.find_element(By.ID,"rte-button-publish")
                            publish.click()
                    except:
                        print("edit link is not found")
                                 
                i_count += 1
                time.sleep(10)


        instance.driver.close()
        return page_data


def run_local(uris):
    """

    :param urls:
    :return:
    """
    event = {"homepage": "https://myperfwiki.com","uris":uris}
    x=LoadUrls()
    pagedata = x.test_load_urls(event,None)
    print("pagedata: {}".format(pagedata))

if __name__ == '__main__':
    user_num = int(os.getenv('USER_NUM',1))
    url_count = int(os.getenv('NUM_URLS',11))
    urls_list =[]
    with open('./urls/data_file.txt', 'r') as data_file:
        lines = data_file.read().splitlines()
        lines_gen = lines[user_num:user_num+url_count]

        print(user_num,url_count)
    run_local(lines_gen)
