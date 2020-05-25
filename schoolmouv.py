"""
@author:t0pl
This tool isn't affiliated to SchoolMouv in any way
"""
import requests
from bs4 import BeautifulSoup
import json
import os
import webbrowser
import time


class resource:
    """Parent class
    Argument : url (str)
    Functions : validate -> bool : validation tests
                download -> None : download 'url' into 'into' (folder) as 'save_as' (filename, default:None)
                relevant_filename -> str : suggests a nice formatted filename
    """

    def __init__(self, url: str):
        self.url = url.split("#")[0].split("?")[0]

    def validate(self, url: str):
        # no to be used for security improvement
        pass

    def download(self, url: str, into: str, save_as=None):
        if type(url) != str:
            print(f'URL needs to be a string, not a {type(url).__name__}')
            return
        if not os.path.exists(into):
            print(f'ain\'t such folder bro, consider changing the value passed in the \'into\' parameter')
            return
        assert self.validate(url)
        _ = requests.get(url)
        assert _.status_code == 200
        save_as = self.relevant_filename(url) if save_as == None else save_as
        abs_path = os.path.abspath(os.path.join(into, save_as))
        if os.path.exists(abs_path):
            print(
                f'This will overwrite existing file {abs_path}, press Ctrl+c to cancel')
        time.sleep(2)
        with open(abs_path, 'wb') as file_to_write:
            file_to_write.write(_.content)

    def relevant_filename(self, url: str):
        _ = ''
        __ = url.split('/')[-2].capitalize().replace('-',' ')
        already_done = 0
        for caract in __:
            if already_done == 0 and caract.isnumeric():
                _ += ' '+caract
                already_done+=1
            else:
                _ += caract
        _ = _.replace('  ',' ')
        return _+'pdf' if url.endswith('.pdf') else _+'.mp4'

    def see(self, url: str):
        webbrowser.open_new_tab(url)


class video(resource):
    """
    Argument : url (str), for eg: https://www.schoolmouv.fr/cours/little-red-riding-hood/cours-video
    Functions : extract_json
                get_source
                get_direct_links
                get_soup
                ----------------
                validate
                download
    """

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url
        self.useful_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.6,zh;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'player.vimeo.com',
            'Pragma': 'no-cache',
            'Referer': self.url,
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4130.0 Safari/537.36'
        }
        self.basic_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4130.0 Safari/537.36 Edg/84.0.502.0'
        }

    def get_soup(self, url, headers={}):
        headers = self.basic_headers if headers == {} else headers
        for _ in range(5):
            po = requests.get(url, headers=headers)
            if po.status_code == 200:
                break
        return BeautifulSoup(po.content, 'html.parser')

    def extract_json(self, mess_up):
        mess_up = str(mess_up)
        mess_up = mess_up.split('};')[0]+'}'
        try:
            mess_up = '{'+mess_up.split('= {')[1]
        except IndexError:
            mess_up = '{'+mess_up.split('={')[1]
        mess_up = json.loads(mess_up)
        return mess_up

    def get_source(self, mess_up):
        assert 'sheet' in mess_up.keys()
        _r = []
        for _ in mess_up['sheet']['resources']:
            _source = mess_up['sheet']['resources'][_]['source']
            _r.append(_source)
        return list(set(_r))

    def get_direct_links(self, json_):
        # print(json_)
        assert 'request' in json_.keys()
        return list(set([i['url'] for i in json_['request']['files']['progressive']]))
        #keys : ['profile', 'width', 'mime', 'fps', 'url', 'cdn', 'quality', 'id', 'origin', 'height']

    def run(self):
        # 1st part
        # GET https://www.schoolmouv.fr/cours/little-red-riding-hood/cours-video
        soup = self.get_soup(self.url)
        script_tag_containing_json = [
            i for i in soup.find_all('script') if str(i).count("{") > 9]
        #assert len(script_tag_containing_json)==1
        # parsing json from <script> tag
        self.script_tag_containing_json = self.extract_json(
            script_tag_containing_json[0])
        # extract unique 9-digit id, different for each video
        sources = self.get_source(self.script_tag_containing_json)

        # 2nd part
        for _source in sources:
            assert len(_source) == 9 and _source.isalnum()
            # GET https://player.vimeo.com/video/9-DIGIT_ID?app_id=schoolmouv_app_id
            soup__ = self.get_soup(
                f'https://player.vimeo.com/video/{_source}', headers=self.useful_headers)  # ?app_id=122963
            script_tag_containing_mp4 = [
                i for i in soup__.find_all('script') if '.mp4' in str(i)]
            #assert len(script_tag_containing_mp4_content) == 1
            self.script_tag_containing_mp4 = self.extract_json(
                script_tag_containing_mp4)
            self.result = self.get_direct_links(self.script_tag_containing_mp4)

    def validate(self, url: str) -> bool:
        return url.endswith('.mp4') and url.startswith('https://vod-progressive.akamaized.net')


class pdf(resource):
    """
    Argument : url (str), for eg: https://www.schoolmouv.fr/cours/little-red-riding-hood/fiche-de-cours
    Functions : run
                download
    """

    def __init__(self, url):
        super().__init__(url)
        self.valids = ['fiche-de-cours', 'fiche-de-revision', 'carte', 'definition', 'fiche-annale', 'lecon', 'fiche-de-lecture', 'auteur', 'formule-ses', 'fiche-methode', 'fiche-methode-bac', 'fiche-materiel', 'fiche-pratique', 'figure-de-style', 'mouvement-litteraire',
                       'registre-litteraire', 'genre-litteraire', 'personnages-historique', 'evenement-historique', 'scientifique', 'algorithme', 'bien-rediger', 'savoir-faire', 'fiche-calculatrice', 'schema-bilan', 'demonstration', 'courant-philosophique', 'repere', 'notion', 'philosophe']
        self.url = url

    def run(self):
        if len([i for i in self.valids if i in self.url]) > 0:
            if self.url.startswith("https://www.schoolmouv.fr/"):
                TO_BE_REPLACED = "www.schoolmouv.fr/eleves" if "/eleves/" in self.url else "www.schoolmouv.fr"
                self.result = f"{self.url.replace(TO_BE_REPLACED,'pdf-schoolmouv.s3.eu-west-1.amazonaws.com')}.pdf"

    def validate(self, url: str) -> bool:
        return url.endswith('.pdf') and url.startswith('https://pdf-schoolmouv.s3.eu-west-1.amazonaws.com/')
