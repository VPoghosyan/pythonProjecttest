from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from selenium.webdriver.chrome.options import Options
import pyautogui
from selenium.webdriver.common.keys import Keys
import os
from email.message import EmailMessage
import imghdr
from selenium.webdriver.common.action_chains import ActionChains
import datetime


options = Options()
options.add_argument('--headless')
# options.add_argument("--no-proxy-server")
# options.add_argument("--proxy-server='direct://'")
# options.add_argument("--proxy-bypass-list=*")
options.add_argument('--no-sandbox')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
#options.add_argument(r"user-data-dir=C:\Users\vahan\PycharmProjects\pythonProjecttest\Selenium web scraper\selenium")
options.add_argument("--start-maximized")
PATH = r"C:\Program Files (x86)\chromedriver"
oldFreeSlots = []
newFreeSlots = []
tempOldSlots = []
checks = 0
fails = 0
emptyArray = []
fileLocation = r'C:\Users\vahan\PycharmProjects\pythonProjecttest\Selenium web scraper'



driver = webdriver.Chrome(PATH, options=options)
driver.get('https://www.schedulista.com/schedule/presidentialbarbershop/choose_time?mode=widget&provider_id=1073797361&service_id=1073967328')


def compSlots():
    if len(newFreeSlots) != 0:
        for k in newFreeSlots:
            if k not in tempOldSlots:
                tempOldSlots.append(k)
                oldFreeSlots.append(k)
            else:
                if os.path.exists(fileLocation + "/" + k + '.png'):
                    os.remove(fileLocation + "/" + k + '.png')
    if len(tempOldSlots) != 0:
        for j in tempOldSlots:
            if j not in newFreeSlots:
                tempOldSlots.pop(tempOldSlots.index(j))



def sendEmail(attachments,subject, message):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'vpserver7777@gmail.com'
    msg['To'] = 'vpoghosyan7777@gmail.com'
    msg.set_content(message)

    if len(attachments) != 0:
        for a in attachments:
            img = open(a + '.png', 'rb')
            img_data = img.read()
            img_type = imghdr.what(img.name)
            img_name = img.name
            msg.add_attachment(img_data, maintype='image', subtype=img_type, filename=img_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('vpserver7777@gmail.com', 'Server7777')
        smtp.send_message(msg)

def barbershopScraper():

    global checks
    time.sleep(3)
    checks += 1

    def findDays():

        for m in range(2):
            days = driver.find_elements_by_tag_name("td")
            month = driver.find_element_by_xpath('//*[@id="datepicker"]/div/div/div/span[1]').text

            freeDays = []

            for i in days:
                txt = i.get_attribute("onclick")
                if isinstance(txt, str):
                    day = i.text
                    freeDays.append(day)

            if len(freeDays) != 0:
                for c in range(len(freeDays)):
                    element = driver.find_element_by_link_text(freeDays[c])
                    element.click()
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="buttons"]/table/tbody/tr')))
                    hours = driver.find_element_by_xpath('//*[@id="buttons"]/table/tbody').text.replace(":00","").replace(
                        "\n", "").replace(" ", "").replace("am", "am_").replace("pm", "pm_")[:-1]

                    appointScreenShot = driver.find_element_by_id('choose-time-container')
                    freeSlots = month + "_" + freeDays[c] + "_" + hours
                    appointScreenShot.screenshot(freeSlots + ".png")
                    newFreeSlots.append(freeSlots)
                    time.sleep(2)
            if m == 0:
                driver.execute_script(
                    'document.querySelector("#datepicker > div > div > a.ui-datepicker-next.ui-corner-all").click()')

    findDays()
    compSlots()
    time.sleep(3)
    print('newFreeSlots: ', newFreeSlots)
    print('oldFreeSlots: ', oldFreeSlots)
    print('tempOldSlots: ', tempOldSlots)

    if len(oldFreeSlots) != 0:
        sendEmail(oldFreeSlots, 'barbershop appointment', 'Find attached available appointment dates and times')

while True:
    try:
        date = datetime.datetime.now()
        barbershopScraper()
        print('Number of checks: ', checks, "   ", date.strftime("%X"), "  ", date.strftime("%x"))
        time.sleep(10)
        driver.refresh()
        time.sleep(3)
        oldFreeSlots = []
        newFreeSlots = []

    except Exception as e:
        fails += 1
        failMsg = str(e) + 2*'\n' + 'Number of checks: ' + str(checks) + 2*'\n' + 'Number of fails: ' + str(fails)
        print('Number of fails: ', fails, "   ", date.strftime("%X"), "  ", date.strftime("%x"))
        sendEmail(emptyArray, '⚠️ fail', failMsg)


        driver.quit()
        time.sleep(5)
        driver = webdriver.Chrome(PATH, options=options)
        driver.get(
            'https://www.schedulista.com/schedule/presidentialbarbershop/choose_time?mode=widget&provider_id=1073797361&service_id=1073967328')






