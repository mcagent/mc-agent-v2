from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from openpyxl import load_workbook
import time

workBook = load_workbook(filename='E:\Catur File\Makassar Coding\MC_Agent_V2\mcsystem.xlsx')
sheetRange = workBook['Raw']

driver = webdriver.Chrome()
driver.get('http://127.0.0.1:5000/menu')
driver.maximize_window()
driver.implicitly_wait(10)

# looping input A/T
i = 3

while i <= len(sheetRange['CH']):
    provinsi = sheetRange['CH' + str(i)].value
    
    driver.find_element_by_id('tambah').click()
    
    try:
        WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'/html/body/main/div/div[2]/div')))
        
        driver.find_element_by_id('tambahKota').send_keys(provinsi)
        driver.find_element_by_id('tes').click()
        
    except TimeoutException:
        print('Error')
        pass
    
    time.sleep(1)
    i = i + 1
    
print('berhasil')