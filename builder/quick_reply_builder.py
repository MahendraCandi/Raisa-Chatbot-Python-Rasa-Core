import json
import logging
from abc import ABC
from typing import Text, Dict, List


class IQuickReplies(ABC):
    @staticmethod
    def set_content_type(value):
        '''set content type'''

    @staticmethod
    def set_text(value):
        '''set text quick replies'''

    @staticmethod
    def set_content(title, payload):
        '''set dictionary for title and payload'''

    @staticmethod
    def set_content_by_dictionary(content_dictionary):
        '''set title and payload by dictionary'''

    @staticmethod
    def channel(channel):
        '''looking for channel'''

    @staticmethod
    def build():
        '''return quick replies'''


class QuickRepliesBuilder(IQuickReplies):
    def __init__(self):
        self.__quick_reply = QuickReply()
        self.__content = None
        self.__channelName = None

    def set_text(self, value):
        self.__quick_reply.text = value
        return self

    def set_content(self, title: Text, payload: Text, content_type=None, image_url=None):
        self.__content = Content()
        if content_type is not None:
            self.__content.content_type = content_type
        if image_url is not None:
            self.__content.image_url = image_url
        self.__content.title = title
        self.__content.payload = payload
        content = vars(self.__content)
        self.__quick_reply.quick_replies.append(content)
        return self

    def set_content_by_dictionary(self, content_dictionary: List):
        quick_replies = []
        for content in content_dictionary:
            self.__content = Content()
            for key in content:
                if key == 'title':
                    self.__content.title = content.get(key)
                if key == 'payload':
                    self.__content.payload = content.get(key)
            content = vars(self.__content)
            quick_replies.append(content)
        self.__quick_reply.quick_replies = quick_replies
        return self

    def channel(self, channel):
        self.__channelName = channel
        return self

    def build(self) -> Dict:
        quick_reply = vars(self.__quick_reply)
        if self.__channelName != 'facebook':
            quick_reply['button'] = quick_reply.pop('quick_replies')
        logging.debug(f"BUILD MESSAGE: {quick_reply}")
        return quick_reply


class QuickReply:
    def __init__(self):
        self.text = None
        self.quick_replies = []
        
        
class Content:
    def __init__(self):
        self.content_type = "text"
        self.image_url = "https://i.ibb.co/5G023yb/eunha.jpg"
        self.title = None
        self.payload = None


