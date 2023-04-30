import json

import html2text
import requests
import undetected_chromedriver as uc

##from selenium import webdriver
from selenium.webdriver.common.by import By


class NovelHiHandler:
    NOVELHI_WEBSITE = "https://novelhi.com/s/Nine-Star-Hegemon-Body-Art"
    TRANSLATE_URL = "https://novelhi.com/book/translate"
    transkey_xq = '//*[@id="transKeyTag"]'

    def __init__(
        self,
        headless: bool = True,
    ):
        self.translate_token = None

        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        if headless:
            options.add_argument("--headless")
            # PROXY = "37.187.88.32:8001"
            # options.add_argument(f'--proxy-server={PROXY}')
        self.browser = uc.Chrome(options=options)
        self.browser.set_page_load_timeout(15)

        self.browser.get(self.NOVELHI_WEBSITE)
        print(self.browser.find_element(By.TAG_NAME, 'body').text)
        self._get_translate_token()

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


if __name__ == "__main__":
    novelhi = NovelHiHandler()
    print("loaded website")
    novelhi.translate_text(chinese_text="真的吗？？为什么你么迷妹这么差")
    print("got token")
