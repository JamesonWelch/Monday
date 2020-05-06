import os
import bs4
import requests
from bs4 import BeautifulSoup

class DictateWikipedia:

    def __init__(self, keyphrase):
        self.keyphrase = keyphrase

    def getArticle(self):
        GOOGLE_URL = f"https://www.google.com/search?q={self.keyphrase}"
        WIKI_URL = f"https://en.wikipedia.org/wiki/{self.keyphrase}"

        response = requests.get(WIKI_URL)
        print(f'Received {WIKI_URL}')
        if response.status_code != 200:
            print(f'Failed: Status Code: {response.status_code}')
            return False
        else:
            wiki = BeautifulSoup(response.text, "html.parser")

            data = wiki.find_all('p').text
            print(data)

            self.article = ""
            for i in wiki.select('p'):
                print(i.getText())
                self.article + self.article + '\n' + i.getText()
                # print(article)

                return data



t = DictateWikipedia('User_Datagram_Protocol').getArticle()
print(t)

