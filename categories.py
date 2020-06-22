import abc
from typing import *
from logging import Logger


class Finder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def doLogin(self) -> bool:
        """
        Performs a Login to the desired Social Media Website.

        :return: Returns True or False (True for a successful login)
        """

    @abc.abstractmethod
    def getProfiles(self, first_name: str, last_name: str) -> List:
        """
        Performs a search on desired Social Media Website and returns possible matches.

        :param first_name: First name of the person you are searching for.
        :param last_name: Last name of the person you are searching for.
        :return: Returns a list of Social Media Profiles including URLs to the Profile Picture
                 In following format: [link, profilepic, 1.0]
        """

    @abc.abstractmethod
    def getPicture(self, profile: str, tries: int) -> str:
        """
        Downloads the Profile Picture and saves it to a temporary file.

        :param profile: Profile URL
        :param tries: Retries to download the picture
        :return: Returns the path to the Profile Picture
        """

    @abc.abstractmethod
    def setCredentials(self, username: str, password: str):
        """
        Sets the Credentials for the Plugin to use.

        :param username: Username
        :param password: Password
        :return: none
        """

    @abc.abstractmethod
    def setConfigParams(self, tempfolder: str):
        """
        Sets the params defined in the config file.

        :param tempfolder: Temporary folder to save images in.
        :return: none
        """

    @abc.abstractmethod
    def setLogger(self, logger: Logger):
        """
        Set's the Logger for the Plugin.

        :param logger: Logger
        :return: none
        """

    @abc.abstractmethod
    def kill(self):
        """
        Kills the active selenium session
        :return: none
        """

class Crawler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def doLogin(self) -> bool:
        """
        Performs a Login to the desired Social Media Website.

        :return: Returns True or False (True for a successful login)
        """

    @abc.abstractmethod
    def getInfo(self, url: str) -> Dict:
        """
        Performs a search on desired Social Media Website and returns possible matches.

        :param url: URL of the Profile you want the info from.
        :return: Returns a dict with the Information.
        """

    @abc.abstractmethod
    def setCredentials(self, username: str, password: str):
        """
        Sets the Credentials for the Plugin to use.

        :param username: Username
        :param password: Password
        :return: none
        """

    @abc.abstractmethod
    def setLogger(self, logger: Logger):
        """
        Set's the Logger for the Plugin.

        :param logger: Logger
        :return: none
        """

    @abc.abstractmethod
    def kill(self):
        """
        Kills the active selenium session
        :return: none
        """