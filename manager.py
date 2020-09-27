import os
import sys
import tkinter as tk
import re
from datetime import datetime


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import openpyxl


# wb = openpyxl.load_workbook(os.path.join(os.path.dirname(__file__), "supliers.xlsx"))
# ws = wb.active
# ws['A1'] = 42
# ws.append([1, 2, 3])
# wb.save(os.path.join(os.path.dirname(__file__), "supliers.xlsx"))

def benchmark(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        func(*args, **kwargs)
        print(f"{str(func)}:", (datetime.now() - start))

    return wrapper

class Suplier_Manager(object):
    def __init__(self, driver):
        self.driver = driver

        self.create_widgets()
        
    def create_widgets(self):
        tk.Button(self, text="test button", command=self.read_supliers_table).grid()
    
    def read_supliers_table(self):
        self.driver.read_supliers_table()

class Suplier_Manager_TopLevel(Suplier_Manager, tk.Toplevel):
    """ Singleton """

    def __init__(self, master, driver, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self, driver)

        self.__class__.instance = self

        mouseX, mouseY = self.get_mouse_position()
        self.geometry(f"+{mouseX}+{mouseY}")
        self.resizable(False, False)
            
    def title(self, title):
        tk.Toplevel.title(self, title)
    
    def get_mouse_position(self):
        return self.master.winfo_pointerx(), self.master.winfo_pointery()

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "instance"):
            cls.instance.destroy()
        return tk.Toplevel.__new__(cls)

class Suplier_Manager_Frame(Suplier_Manager, tk.Frame):
    def __init__(self, master, driver, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self, driver)

        self.master.resizable(False, False)
   
    def title(self, title):
        self.master.title(title)

class Extended_Webdriver(webdriver.Chrome):
    def __init__(self, executable_path="chromedriver", port=0, options=None, service_args=None, desired_capabilities=None, service_log_path=None, chrome_options=None, keep_alive=True):
        webdriver.Chrome.__init__(self, executable_path, port, options, service_args, desired_capabilities, service_log_path, chrome_options, keep_alive)

    def read_supliers_table(self) -> list:
        orders = []
        table_element = driver.find_element_by_class_name("table-primary")
        pages_element = table_element.find_element(By.TAG_NAME, "pre")        
        pages = re.search('Page: (\d+) / (\d+)', pages_element.text)
        current_page = int(pages.group(1))
        last_page = int(pages.group(2))

        if current_page != 1:
            self.goto_nes_table_first_page(table_element=table_element)
            orders += self.read_supliers_page_orders(table_element=table_element)

        for i in range(1, last_page):
            self.goto_nes_table_next_page(table_element=table_element)
            orders += self.read_supliers_page_orders(table_element=table_element)
    
        return orders

    def goto_nes_table_first_page(self, table_element):
        """ Press first button in NES table. Checking if table text changed, else page not switched """

        first_button = table_element.find_element_by_link_text("First")
        driver.execute_script("arguments[0].click()", first_button)        
        WebDriverWait(driver, 5).until_not(EC.text_to_be_present_in_element((By.CLASS_NAME, "table-primary"), table_element.text))
        
    def goto_nes_table_next_page(self, table_element):
        """ Press next button in NES table. Checking if table text changed, else page not switched """

        next_button = table_element.find_element_by_link_text("Next")
        driver.execute_script("arguments[0].click()", next_button)
        WebDriverWait(driver, 5).until_not(EC.text_to_be_present_in_element((By.CLASS_NAME, "table-primary"), table_element.text))
        
    def read_supliers_page_orders(self, table_element) -> list:
        tbody_element = table_element.find_element(By.CSS_SELECTOR, "tbody")
        rows = len(tbody_element.find_elements(By.CSS_SELECTOR, "tr"))
        td_elements = tbody_element.find_elements(By.CSS_SELECTOR, "td")
        
        orders = []

        for row in range(1, rows + 1):
            order = []
            for col in (1, 2, 5):
                order.append(td_elements[row * col].text)
            orders.append(order)

        return orders

if __name__ == "__main__":

    def create_profile_chrome_driver() -> Extended_Webdriver:
        """ Create chrome webdriver with default user profile """
        
        os.chdir(sys.path[0])
        executable_path = os.path.join("chromedriver","chromedriver.exe")

        chrome_options = Options()
        chrome_options.add_argument(r"user-data-dir=C:\Users\andre\AppData\Local\Google\Chrome\User Data")
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"

        return Extended_Webdriver(desired_capabilities=caps, executable_path=executable_path, options=chrome_options)

    def on_closing():
            driver.quit()
            root.destroy()

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)    

    driver = create_profile_chrome_driver()
    driver.get("https://nesky.hktemas.com/no-suppliers")
    frame = Suplier_Manager_Frame(root, driver=driver)
    frame.grid()    
    root.mainloop()