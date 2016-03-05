from splinter.browser import Browser
from time import sleep

#URL = 'https://hr-qas.nsrp.com.vn:8000/Home/Login'
URL = 'https://acompayroll.com:6900/Home/Login'
USERNAME = 'ibm.hung.pt'
PASSWORD = '123'


def main():
    br = Browser('firefox')
    br.visit(URL)
    sleep(3)
    #if br.is_text_present('Connection', wait_time=7):
    br.fill('UserName', USERNAME)
    br.fill('Password', PASSWORD)
    button = br.find_by_id("btnLogin")
    button.click()
    sleep(30)
    br.quit()

if __name__ == "__main__":
    n = 2
    while n > 0:
        main()
        n = n - 1
        sleep(20)