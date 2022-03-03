#This program check other sellers stock quantities.
#Benefits: 1.You can find hot products and verify it by this bot, everday.
#          2.You may see your competitors sellers rate by each day.
#          3.Or you can check how much a particular product is selling from day to day.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException        
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime
import pandas as pd
import os.path
from Config import ASIN, Saved_file

#ASIN 
Saved_file = f'{Saved_file}.xlsx'
ASIN_number = len(ASIN)
Day=datetime.today().strftime('%d.%m.%Y')
Runningtime=datetime.now()

#LIST AND URLS
Stock_Array =[]
Price_Array=[]
Date_Array= []
Out_of_stock = 'O.S.' #Out of Stock
In_stock1 = 'In stock.'
In_stock2 = 'In Stock.'
In_stock3 = 'left in stock - order soon.'
urlamazon= "https://www.amazon.com/"
cart_url = "https://www.amazon.com/gp/cart/view.html?ref_=nav_cart"


#OPTIONS
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--headless') #hide chrome
options.add_argument('--no-sandbox') # Bypass OS security model
options.add_argument('--disable-gpu')  # applicable to windows os only
options.add_argument('--log-level=1') #to not get error for hide. "Error with Permissions-Policy header: Unrecognized feature: 'interest-cohort'.", source:  (0)
#options.add_argument('--enable-logging --v=3')

#Automatically install chromedrivermanager
s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# xpath function
def get_xpath(xpath_name):
  return wait.until(EC.presence_of_element_located((By.XPATH, xpath_name)))

# class name function
def get_class(class_name):
  return wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# name function 
def get_name(name):
  return wait.until(EC.presence_of_element_located((By.NAME, name)))
  
#PART 1 - START
print("Loading..")
driver.get(urlamazon)

# location settings
get_xpath('//*[@id="nav-global-location-slot"]').click()
get_xpath('//*[@id="GLUXZipUpdateInput"]').send_keys('10001', Keys.ENTER)
driver.get(urlamazon)
sleep(30) #Program must wait 30 seconds(only first time for location), because Amazon may give error because of location.


for i in range(ASIN_number):
 url = f"https://www.amazon.com/dp/{ASIN[i]}/"
 driver.get(url)
 
 #PART 2 - check availability of product
 try:
   Availabilitwait = get_xpath('//*[@id="availability"]/span')
   Availability = Availabilitwait.text
 except:
   print(f"-ERROR- ASIN: {ASIN[i]} IS DELETED")
   Availability ="DELETED"

 #PART 3 - get price of product - price xpath changing for some categories
 if In_stock1 in Availability or In_stock2 in Availability or In_stock3 in Availability:
       try:
         Price = get_xpath('//*[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]/span[2]').text
         exact_price = Price                                                           
  
       except (NoSuchElementException, TimeoutException):                                 
         Price = get_xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/span[2]/span[2]').text
         exact_price = Price
         Price = get_xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/span[2]/span[3]').text
         exact_price = "$" + exact_price + "." + Price

       Price_Array.append(exact_price)

       #NEW version of addtocard to not get error: element is not clickable.
       get_xpath('//*[@id="add-to-cart-button"]')
       driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="add-to-cart-button"]'))))

       #PART 4 - get stock's quantity strategy
       get_xpath('//*[@id="nav-cart-count-container"]').click()  #Cart wait
       get_class('sc-action-quantity').click() # Quantity
       get_xpath('//*[@id="quantity_10"]').click() #Select 10+
       get_name('quantityBox').send_keys(Keys.BACK_SPACE,'999', Keys.ENTER)
       sleep(1) #for read exact stock value.
 
     #PART 5 - take stock's quantity number and save it to array.
       Stock_number = get_name('quantityBox').get_attribute('value')
       Stock_Array.append(Stock_number)
       Date_Array.append(Day)
       get_xpath('//input[@data-action="delete"]')
       driver.execute_script("arguments[0].click();", wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@data-action="delete"]'))))

       
      

 else:
     Stock_Array.append(Out_of_stock)
     Price_Array.append(Out_of_stock)
     Date_Array.append(Day)
     #PART 6 - display product price, quantity, date etc. command file
 print(f"NO:{i+1}\t ASIN:\t{ASIN[i]}\t STOCK:\t{Stock_Array[i]}\t PRICE:\t{Price_Array[i]}\t DATE: {Day}")

 if i == ASIN_number-1:
     break

#FINAL

#Check if file exist
file_exists = os.path.exists(Saved_file) 

#If file exist update excel file with date and stock quantities
if file_exists == True:
 try:
   df = pd.read_excel(Saved_file)
   df.insert(df.columns.size, Day, Stock_Array ,allow_duplicates=True)
   print("#UPDATE FILE")
 except ValueError:
   print("-ERROR- You must have deleted an asin. Rows x Columns are not match")
   exit()

#Otherwise it will create new excel file
else:
 df = pd.DataFrame({'ASIN':ASIN, 'PRICE': Price_Array, Day :Stock_Array})
 print("#NEW FILE")

#Save it to excel
df.to_excel(Saved_file, index = False, header=True)
print("Running time:", datetime.now()-Runningtime)
print("Excel File saved, Program is closing..")
driver.quit()
exit()