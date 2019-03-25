#-*- coding :utf-8 -*-

from selenium import webdriver
import time
import re
import os


class Xuetangx(object):
    def __init__(self):
        self.base_url = 'https://hit.xuetangx.com'

        '''静音'''
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--mute-audio")

        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.maximize_window()

        self.login()

        if os.path.exists('record.data'):
            self.history = open('record.data', 'r').read().strip()
        else:
            self.history = None

        if self.enter_course():
            self.video = self.get_all_video()
            self.text = self.get_all_text()

            if self.video:
                self.play_all_video()

            if self.text:
                self.view_all_text()

    def __del__(self):
        self.driver.quit()

    def load_url(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(5)

    def login(self):
        self.load_url('https://hit.xuetangx.com/#/home')
        if self.driver.find_element_by_link_text('登录'):
            self.driver.find_element_by_link_text('登录').click()
        while True:
            time.sleep(8)
            if 'https://hit.xuetangx.com/manager#/studentcourselist' == self.driver.current_url:
                return

    def enter_course(self):
        if self.driver.find_element_by_link_text('进入课程'):
            self.driver.find_element_by_link_text('进入课程').click()
            time.sleep(10)
            return True
        else:
            print("Can't find courses.")
            return False

    def get_all_video(self):
        return re.findall('href="(.*?videoDiscussion)" class="element-title"', self.driver.page_source)

    def get_all_text(self):
        return re.findall('href="(/lms#/graphic/.*?)" class="element-title"', self.driver.page_source)

    def play(self, url):
        self.load_url(self.base_url + url)
        time.sleep(10)

        course = re.search('class="chapter-name">(.*?)</span>', self.driver.page_source)
        if course:
            print('Playing:', course.group(1))

        re_play_time = re.compile(
            '<div class="xt_video_player_current_time_display fl"><span>(.*?)</span> / <span>(.*?)</span></div>')

        while True:
            play_time = re_play_time.search(self.driver.page_source)
            if play_time and play_time.group(2) != '0:00':
                break
            else:
                print("Can't load the video. Try to reload.")
                self.driver.refresh()
                self.driver.implicitly_wait(5)
                time.sleep(2)

        while True:
            try:
                self.driver.execute_script(
                    "javascript:var video=document.getElementById('video');video.pause=null;video.play();")
                break
            except:
                self.driver.refresh()
                self.driver.implicitly_wait(3)
                time.sleep(2)

        while True:
            play_time = re_play_time.search(self.driver.page_source)
            if play_time:
                print('Current:', play_time.group(1) + '/' + play_time.group(2))
            if play_time and play_time.group(1) == play_time.group(2):
                time.sleep(1)
                self.history = url
                return
            time.sleep(10)

    def record(self):
        open('record.data', 'w').write(self.history)

    def play_all_video(self):
        if self.history:
            try:
                index = self.video.index(self.history)
                self.video = self.video[index + 1:len(self.video)]
            except ValueError as e:
                pass

        for i in self.video:
            self.play(i)
            self.record()

        print("Finish All Video!")

    def view_all_text(self):
        for i in self.text:
            self.load_url(self.base_url + i)
            time.sleep(2)
            text = re.search('class="chapter-name">(.*?)</span>', self.driver.page_source)
            if text:
                print("Viewing:", text.group(1))
        print("Finish All Text.")


if __name__ == '__main__':
    x = Xuetangx()
