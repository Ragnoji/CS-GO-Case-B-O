from selenium import webdriver
from steam_data import steam_login, steam_password
import time
import pickle

options = webdriver.ChromeOptions()

binary_yandex_driver_file = 'yandexdriver.exe'

driver = webdriver.Chrome(binary_yandex_driver_file, options=options)

try:
    url = 'https://steamcommunity.com/login/home/?goto=market'
    driver.get(url)

    login_input = driver.find_element_by_id("input_username")
    login_input.clear()
    login_input.send_keys(steam_login)
    time.sleep(1)

    password_input = driver.find_element_by_id("input_password")
    password_input.clear()
    password_input.send_keys(steam_password)
    time.sleep(1)

    login_button = driver.find_element_by_xpath('//*[@id="login_btn_signin"]/button').click()
    time.sleep(3)

    sda_input = driver.find_element_by_xpath('//*[@id="twofactorcode_entry"]')
    sda_input.send_keys(input('Введите SteamGuard:\n'))
    sda_button = driver.find_element_by_xpath('//*[@id="login_twofactorauth_buttonset_entercode"]/div[1]').click()
    time.sleep(10)

    pickle.dump(driver.get_cookies(), open('steam_cookies', 'wb'))

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
