import re
import json
import requests as rq

from typing import *
from logging import Logger
from categories import Crawler


class InstagramCrawler(Crawler):
    USER_AGENT = "Instagram 123.0.0.21.114"
    PROFILE_REGEX: re.Pattern
    logger: Logger

    def __init__(self):
        self.PROFILE_REGEX = re.compile(
            '(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am)\/([A-Za-z0-9-_\.]+)\/$')

    def doLogin(self) -> bool:
        return True

    def getInfo(self, url: str) -> Dict:
        info = dict()

        self.logger.debug("Checking if Instagram Profile")
        if self.PROFILE_REGEX.match(url):
            self.logger.debug(f"Getting Info for {url}")
            headers = {
                'User-Agent': self.USER_AGENT
            }

            profile_json = json.loads(rq.get(url + "?__a=1", headers=headers).content)

            info["id"] = profile_json["graphql"]["user"]["id"]
            info["full_name"] = profile_json["graphql"]["user"]["full_name"]
            info["follower"] = profile_json["graphql"]["user"]["edge_followed_by"]["count"]
            info["following"] = profile_json["graphql"]["user"]["edge_follow"]["count"]
            info["biography"] = profile_json["graphql"]["user"]["biography"]
            info["posts"] = profile_json["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]

        return info

    def setCredentials(self, username: str, password: str):
        pass

    def setLogger(self, logger: Logger):
        self.logger = logger

    def kill(self):
        pass
