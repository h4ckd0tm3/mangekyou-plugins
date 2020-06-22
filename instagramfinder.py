import os
import re
import sys
import json
import shutil
import tempfile
import requests as rq

from time import sleep
from logging import Logger
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display

from categories import Finder


class InstagramFinder(Finder):
    USER_AGENT = "Instagram 123.0.0.21.114"
    BASE_URL = "https://www.instagram.com/"
    LOGIN_URL = "https://instagram.com/accounts/login/"
    INFO_ENDPOINT = "https://i.instagram.com/api/v1/users/{}/info/"

    PROFILE_REGEX: re.Pattern

    driver: webdriver
    logger: Logger
    tempfolder: str
    username: str
    password: str

    def __init__(self):
        display = Display(visible=0, size=(1600, 1024))
        display.start()
        os.environ['MOZ_HEADLESS'] = '1'
        _browser_profile = webdriver.FirefoxProfile()
        _browser_profile.set_preference("dom.webnotifications.enabled", False)
        self.driver = webdriver.Firefox(firefox_profile=_browser_profile)
        self.driver.implicitly_wait(15)
        self.driver.delete_all_cookies()

        self.PROFILE_REGEX = re.compile(
            '(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am)\/([A-Za-z0-9-_\.]+)\/$')

    def setCredentials(self, username: str, password: str):
        self.username = username
        self.password = password

    def setLogger(self, logger: Logger):
        self.logger = logger

    def setConfigParams(self, tempfolder: str):
        self.tempfolder = tempfolder

    def doLogin(self):
        self.driver.get(self.LOGIN_URL)
        self.driver.execute_script('localStorage.clear();')

        # convert unicode in instagram title to spaces for comparison
        title_string = ''.join([i if ord(i) < 128 else ' ' for i in self.driver.title])

        if title_string.startswith("Login"):
            self.logger.debug("Instagram Login Page loaded successfully")

            user_field = self.driver.find_element_by_xpath("//input[@name='username']")
            user_field.send_keys(self.username)
            password_field = self.driver.find_element_by_xpath("//input[@name='password']")
            password_field.send_keys(self.password)

            # / html / body / span / section / main / div / article / div / div[1] / div / form / div[4] / button
            self.driver.find_element_by_xpath("//button/div[text()='Log In']").click()
            sleep(5)

            if str(self.driver.title).startswith("Instagram"):
                self.logger.debug("Instagram Login successful")
            else:
                self.logger.debug("Instagram Login failed")

    def getProfiles(self, name: str):
        try:
            self.driver.get(self.BASE_URL)
            sleep(3)

            profile_list = []

            try:
                searchbar = self.driver.find_element_by_xpath("//input[@placeholder='Search']")
            except:
                # if cant find search bar try to re-login
                self.doLogin()
                self.driver.get(self.BASE_URL)
                sleep(3)
                try:
                    searchbar = self.driver.find_element_by_xpath("//input[@placeholder='Search']")
                except:
                    self.logger.debug(
                        "Instagram Timeout Error, session has expired and attempts to reestablish have failed")
                    return profile_list

            sleep(1)

            searchbar.send_keys(name)
            sleep(1)
            search_response = self.driver.page_source.encode('utf-8')
            sleep(1)
            soup_parser = BeautifulSoup(search_response, 'html.parser')

            for element in soup_parser.find_all('a', {'class': 'yCE8d'}):
                link = "https://instagram.com" + element['href']

                if self.PROFILE_REGEX.match(link):
                    self.logger.debug(f"Getting Picture for {link}")

                    profile = dict()
                    profile["url"] = link
                    profile["picture"] = self.getPicture(link, 0)
                    profile["association"] = 1.0

                    profile_list.append(profile)

            return profile_list
        except Exception as e:
            self.logger.error("Error on line {}".format(sys.exc_info()[-1].tb_lineno) + e)
            profile_list = []

            return profile_list

    def getPicture(self, profile: str, tries: int) -> str:
        headers = {
            'User-Agent': self.USER_AGENT
        }

        picture = ""
        profile_pic_link = ""
        cookies = self._getCookies()

        profile_json = json.loads((rq.get(profile + "?__a=1")).content)
        profile_id = profile_json["graphql"]["user"]["id"]

        if tries < 3:
            profile_id_json = json.loads(
                rq.get(self.INFO_ENDPOINT.format(profile_id), headers=headers, cookies=cookies).content)

            if not profile_id_json["status"] == "fail":
                profile_pic_link = profile_id_json["user"]["hd_profile_pic_url_info"]["url"]
            else:
                sleep(60)
                tries += 1
                picture = self.getPicture(profile, tries)
        else:
            profile_pic_link = profile_json["graphql"]["user"]["profile_pic_url_hd"]

        if picture == "" and not profile_pic_link == "":
            out_file = tempfile.NamedTemporaryFile(mode="wb", dir=self.tempfolder, delete=False)
            response = rq.get(profile_pic_link, headers=headers, cookies=cookies, stream=True)
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
            del response

            picture = out_file.name

        return picture

    def kill(self):
        self.driver.close()

    def _getCookies(self):
        all_cookies = self.driver.get_cookies()
        cookies = {}
        for s_cookie in all_cookies:
            cookies[s_cookie["name"]] = s_cookie["value"]
        return cookies
