import json

import html2text
import requests
import selenium.common.exceptions as Exceptions
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

##from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class NovelHiHandler:
    NOVELHI_WEBSITE = "https://novelhi.com/s/Nine-Star-Hegemon-Body-Art"
    TRANSLATE_URL = "https://novelhi.com/book/translate"
    transkey_xq = '//*[@id="transKeyTag"]'

    login_xq = '//button[//div[text()="Log in"]]'
    continue_xq = '//button[text()="Continue"]'
    next_cq = "prose"
    button_tq = "button"
    # next_xq     = '//button[//div[text()="Next"]]'
    done_xq = '//button[//div[text()="Done"]]'

    chatbox_cq = "text-base"
    wait_cq = "text-2xl"
    reset_xq = '//a[text()="New chat"]'

    def __init__(
        self,
        headless: bool = True,
    ):
        self.translate_token = None

        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
        self.browser = uc.Chrome(options=options)
        self.browser.set_page_load_timeout(5)

        self.browser.get(self.NOVELHI_WEBSITE)
        # if not cold_start:
        #     self.pass_verification()
        # self.login(username, password)

    def _get_translate_token(self) -> str:
        if self.translate_token is None:
            token_element = self.browser.find_element(By.XPATH, self.transkey_xq)
            self.translate_token = token_element.get_attribute("value")
        return self.translate_token

    def translate_text(self, chinese_text: str) -> str:
        payload = {"content": f"{chinese_text}"}
        url = f"{self.TRANSLATE_URL}/{self._get_translate_token()}"
        headers = {
            "content-type": "application/json",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(response.content)
        content = json.loads(response.content)
        html_text = content.get("data", {}).get("content")
        while "<br><br>" in html_text:
            html_text = html_text.replace("<br><br>", "")

        translated_text = html2text.html2text(html_text)
        # while '\n\n' in translated_text:
        #     translated_text = translated_text.replace('\n\n', '')
        # translated_text = BeautifulSoup(html_text).get_text()
        print(translated_text)

        return translated_text

    # def pass_verification(self):
    #     while self.check_login_page():
    #         verify_button = self.browser.find_elements(By.ID, "challenge-stage")
    #         if len(verify_button):
    #             try:
    #                 verify_button[0].click()
    #             except Exceptions.ElementNotInteractableException:
    #                 pass
    #         time.sleep(1)
    #     return

    # def check_login_page(self):
    #     login_button = self.browser.find_elements(By.XPATH, self.login_xq)
    #     return len(login_button) == 0

    # def login(self, username: str, password: str):
    #     """To enter system"""

    #     # Find login button, click it
    #     login_button = self.sleepy_find_element(By.XPATH, self.login_xq)
    #     login_button.click()
    #     time.sleep(1)

    #     # Find email textbox, enter e-mail
    #     email_box = self.sleepy_find_element(By.ID, "username")
    #     email_box.send_keys(username)

    #     # Click continue
    #     continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
    #     continue_button.click()
    #     time.sleep(1)

    #     # Find password textbox, enter password
    #     pass_box = self.sleepy_find_element(By.ID, "password")
    #     pass_box.send_keys(password)
    #     # Click continue
    #     continue_button = self.sleepy_find_element(By.XPATH, self.continue_xq)
    #     continue_button.click()
    #     time.sleep(1)

    #     # Pass introduction
    #     next_button = self.browser.find_element(By.CLASS_NAME, self.next_cq)
    #     next_button = next_button.find_elements(By.TAG_NAME, self.button_tq)[0]
    #     next_button.click()
    #     time.sleep(1)
    #     next_button = self.browser.find_element(By.CLASS_NAME, self.next_cq)
    #     next_button = next_button.find_elements(By.TAG_NAME, self.button_tq)[1]
    #     next_button.click()
    #     time.sleep(1)
    #     next_button = self.browser.find_element(By.CLASS_NAME, self.next_cq)
    #     done_button = next_button.find_elements(By.TAG_NAME, self.button_tq)[1]
    #     done_button.click()

    # def sleepy_find_element(
    #     self, by, query, attempt_count: int = 20, sleep_duration: int = 1
    # ):
    #     """If the loading time is a concern, this function helps"""
    #     for _ in range(attempt_count):
    #         item = self.browser.find_elements(by, query)
    #         if len(item) > 0:
    #             item = item[0]
    #             break
    #         time.sleep(sleep_duration)
    #     return item

    # def wait_to_disappear(self, by, query, sleep_duration=1):
    #     """Wait until the item disappear, then return"""
    #     while True:
    #         thinking = self.browser.find_elements(by, query)
    #         if len(thinking) == 0:
    #             break
    #         time.sleep(sleep_duration)
    #     return

    # def interact(self, question: str):
    #     """Function to get an answer for a question"""
    #     text_area = self.browser.find_element(By.TAG_NAME, "textarea")
    #     for each_line in question.split("\n"):
    #         text_area.send_keys(each_line)
    #         text_area.send_keys(Keys.SHIFT + Keys.ENTER)
    #     text_area.send_keys(Keys.RETURN)
    #     self.wait_to_disappear(By.CLASS_NAME, self.wait_cq)
    #     answer = self.browser.find_elements(By.CLASS_NAME, self.chatbox_cq)[-1]
    #     return answer.text

    # def reset_thread(self):
    #     """the conversation is refreshed"""
    #     self.browser.find_element(By.XPATH, self.reset_xq).click()


if __name__ == "__main__":
    novelhi = NovelHiHandler()
    print("loaded website")
    novelhi.translate_text(chinese_text="真的吗？？为什么你么迷妹这么差")
    print("got token")
