import time
import requests
import traceback
import json
import os
import os.path as osp
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.request import urlopen
from config import params, cookies, headers


class TikTok_Crawl:
    def __init__(self, link_crawl_video: str):
        # Settings
        options = Options()
        options.add_argument("start-maximized")
        # options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=options)
        self.valid_url = False
        self.link_crawl_video = link_crawl_video
        self.check_url()
        if self.valid_url:
            self.id = self.link_crawl_video.split('/')[-1]
            self.driver.get(link_crawl_video)
            time.sleep(1)
            self.scroll_page()
            # create folder with name id and contains all video of id.
            folder = osp.join(os.getcwd(), self.id)
            if not osp.exists(folder):
                os.makedirs(folder)
    
    
    # check url is valid or not valid
    def check_url(self):
        req = requests.get(self.link_crawl_video)
        if req.status_code == 200:
            self.valid_url = True
        

    # Scroll page
    def scroll_page(self):
        scroll_pause_time = 1
        screen_height = self.driver.execute_script("return window.screen.height;")
        i = 1
        while True:
            self.driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
            i += 1
            time.sleep(scroll_pause_time)
            scroll_height = self.driver.execute_script("return document.body.scrollHeight;")  
            if (screen_height) * i > scroll_height:
                break 
    
    
    # get all video contains in page url
    def find_videos_in_url(self):
        list_tag_a = self.driver.find_elements(By.TAG_NAME, "a")
        links = []
        for tag_a in list_tag_a:
            if 'video' in tag_a.get_attribute('href'):
                links.append(tag_a.get_attribute('href'))
        return links
    
    
    # convert video have logo tiktok to not logo tiktok
    def cvt_video_without_watermark(self):
        link_videos_from_tiktok = self.find_videos_in_url()
        # init url video from titktok
        data = {
            'id': '',
            'locale': '',
            'tt': ''
        }
        # save output
        results = {}
        for link_video in link_videos_from_tiktok:
            try:
                data['id'] = link_video
                # Request post
                response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data, timeout=(10, 10))
                downloadSoup = BeautifulSoup(response.text, "html.parser")
                downloadLink = downloadSoup.a["href"]
                videoTitle = downloadSoup.p.getText().strip()
                results[data['id']] = {
                    'link_watermark': data['id'],
                    'link_without_watermark': downloadLink,
                    'videoTitle': videoTitle,
                    'time_crawl': time.time()
                }
                time.sleep(20)
            except Exception as err:
                pass
        # write file json
        with open(osp.join(os.getcwd(), self.id, 'data.json'), 'w') as f:
            json.dump(results, f)
        
        return results
    
    # Crawl data
    def download_video(self, downloadLink, videoTitle):
        mp4File = urlopen(downloadLink)
        # Feel free to change the download directory
        f_video = osp.join(os.getcwd(), self.id, f'{videoTitle}.mp4')
        with open(f_video, "wb") as output:
            while True:
                data = mp4File.read(4096)
                if data:
                    output.write(data)
                else:
                    break
    

if __name__ == '__main__':
    link = 'https://www.tiktok.com/discover/Cristiano-Ronaldo'
    crawl_vid_TikTok = TikTok_Crawl(link)
    list_video = crawl_vid_TikTok.cvt_video_without_watermark()
    print(len(list_video), list_video)