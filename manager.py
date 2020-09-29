import os
import sys
import tkinter as tk
import re
from datetime import datetime
import csv
import copy

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import openpyxl

from table import tableGUI


def read_csv_settings(file_path) -> dict:
    """ Return dict with key = csv column name, value = csv column value in the 1st row only"""

    with open(file_path, 'r', newline='') as csvfile:
        return next(csv.DictReader(csvfile, delimiter=";"))

#Constants
MANAGER_DIR_PATH = os.path.dirname(__file__)
ORDERS_PATH = os.path.join(MANAGER_DIR_PATH, "Orders.xlsx")
EMPLOYERS_PATH = os.path.join(MANAGER_DIR_PATH, "Employers orders.xlsx")
FREE_MARK = ' '
settings = read_csv_settings(file_path=os.path.join(MANAGER_DIR_PATH, "settings", "settings.csv"))

class Suplier_Manager(object):
    def __init__(self, driver):
        self.driver = driver
        self.__orders = ()
        self.__employers = ()
        self.__listeners = []

        self.table = None

        self.create_widgets()        
        self.read_files()

    def create_widgets(self):
        self.table = tableGUI.TableGUI(master=self, height=int(settings['table rows']))
        self.table.grid(row=0, column=0)
        self.subscribe(self.table)

        save_button = tk.Button(self, text="save files", font=("Calibri", 12), command=self.save_files)
        save_button.grid(row=1, column=0)

    def save_files(self):
        filemanager.save_orders_to_file(orders=self.get_orders(), file_path=ORDERS_PATH, save_backup=settings['save backups'])
        filemanager.save_employers_to_file(employers=self.get_employers(), file_path=EMPLOYERS_PATH)
    
    def read_files(self):
        self.set_employers(employers=filemanager.get_employers_from_file(file_path=EMPLOYERS_PATH))
        for employer in self.get_employers():
            self.subscribe(employer)
        self.set_orders(new_orders=filemanager.get_orders_from_file(file_path=ORDERS_PATH))
       
    def get_orders(self) -> list:
        return list(copy.deepcopy(self.__orders))
    
    def set_orders(self, new_orders):
        self.__orders = tuple(copy.deepcopy(new_orders))
        self.on_orders_changed()

    def on_orders_changed(self):
        """ mark_self_orders must be firts, because it one change orders list """

        for listener in self.__listeners:
            if hasattr(listener, "mark_self_orders"):
                self.__orders = tuple(listener.mark_self_orders(orders=self.get_orders()))
                
        for listener in self.__listeners:
            if hasattr(listener, "on_orders_changed"):
                listener.on_orders_changed(orders=self.get_orders())
    
    def get_free_orders(self) -> list:
        return [order for order in self.get_orders() if order[3] == FREE_MARK]

    def get_employers(self):
        return self.__employers
    
    def set_employers(self, employers:list):
        self.__employers = tuple(employers)
        self.on_employers_changed()
    
    def on_employers_changed(self):
        for listener in self.__listeners:
            if hasattr(listener, "on_employers_changed"):
                listener.on_employers_changed(employers=self.get_employers())
    
    def subscribe(self, listener):
        self.__listeners.append(listener)        
       

class Employer(object):
    def __init__(self, name, orders):
        self.name = name
        self.__orders = tuple(copy.deepcopy(orders))
        self.__listeners = []
    
    def get_orders(self) -> list:
        return list(copy.deepcopy(self.__orders))
    
    def set_orders(self, new_orders):
        self.__orders = tuple(copy.deepcopy(new_orders))
        self.on_employer_orders_changed()
    
    def on_orders_changed(self, orders):
        """ Removes orders that absent in NES(orders) """

        orders_numbers = [order[2] for order in orders]
        clean_orders = self.get_orders()

        for employer_order in self.get_orders():
            if employer_order not in orders_numbers:
                clean_orders.remove(employer_order)
        
        self.set_orders(new_orders=clean_orders)

    def on_employer_orders_changed(self):
        for listener in self.__listeners:
            if hasattr(listener, "on_employer_orders_changed"):
                listener.on_employer_orders_changed(employer=self)
    
    def subscribe(self, listener):
        self.__listeners.append(listener)

    def mark_self_orders(self, orders) -> list:
        " Mark self orders by name in given orders list"

        orders_numbers = [order[2] for order in orders]

        for employer_order in self.get_orders():
            if not employer_order in orders_numbers:
                continue
            index = orders_numbers.index(employer_order)
            orders[index][3] = self.name
        
        return orders

    def __repr__(self):
        class_ = str(self.__class__)[:-1]
        return f"{class_} name={self.name}, orders={self.get_orders()}>'"

class Suplier_Manager_TopLevel(Suplier_Manager, tk.Toplevel):
    """ Singleton """

    def __init__(self, master, driver, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self, driver)

        self.__class__.instance = self

        mouseX, mouseY = self.get_mouse_position()
        self.geometry(f"+{mouseX}+{mouseY}")
        self.resizable(False, False)
                
    def get_mouse_position(self):
        return self.master.winfo_pointerx(), self.master.winfo_pointery()

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "instance"):
            cls.instance.destroy()
        return tk.Toplevel.__new__(cls)
    
    def title(self, title):
        tk.Toplevel.title(self, title)

class Suplier_Manager_Frame(Suplier_Manager, tk.Frame):
    def __init__(self, master, driver, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self, driver)

        self.master.resizable(False, False)
   
    def title(self, title):
        self.master.title(title)

class filemanager(object):

    @staticmethod
    def save_orders_to_file(orders, file_path, save_backup=False):        
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        for row in orders:
            sheet.append(row)

        workbook.save(filename=file_path)

        if save_backup == "Yes":
            date = datetime.today().strftime(r"%H.%M %d-%m-%Y")
            dir_path = os.path.dirname(file_path)
            workbook.save(filename=os.path.join(dir_path, 'Backups', f'{date}.xlsx'))

    @staticmethod
    def save_employers_to_file(employers, file_path):
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        for col in range(len(employers)):
            sheet.cell(row=1, column=col + 1, value=employers[col].name)
            orders = employers[col].get_orders()
            for row in range(len(orders)):
                sheet.cell(row=row + 2, column=col + 1, value=orders[row])

        workbook.save(file_path)
    
    @staticmethod
    def get_employers_from_file(file_path) -> list:
        workbook = openpyxl.load_workbook(filename=file_path)
        sheet = workbook.active
        employers = []

        for column in sheet.columns:
            employer_name = column[0].value

            employer_orders = []
            for cell in column[1:]:
                if not cell.value:
                    break
                employer_orders.append(cell.value) 

            employers.append(Employer(name=employer_name, orders=employer_orders))
        
        return employers
    
    @staticmethod
    def get_orders_from_file(file_path):
        workbook = openpyxl.load_workbook(filename=file_path)
        sheet = workbook.active
        orders = []

        for row in sheet.rows:
            order = []
            for col in row:
                order.append(col.value)
            
            orders.append(order)

        return orders   

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

        ###############test###################
        last_page = 3
        ###############test###################

        if current_page != 1:
            self.goto_nes_table_first_page(table_element=table_element)

        for current in range(last_page):
            orders += self.read_supliers_page_orders(table_element=table_element)
            if current < last_page - 1:
                self.goto_nes_table_next_page(table_element=table_element)
    
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
        """ Read supliers 1, 2, 5 columns data. Using search all td elements instead selector because it faster.
            Mark all orders as free by FREE_MARK """

        tbody_element = table_element.find_element(By.CSS_SELECTOR, "tbody")
        rows = len(tbody_element.find_elements(By.CSS_SELECTOR, "tr"))
        td_elements = tbody_element.find_elements(By.CSS_SELECTOR, "td")
        COLUMNS = 8
        
        orders = []

        for row in range(rows):
            order = []
            for col in (0, 1, 4):
                index = row * COLUMNS + col
                order.append(td_elements[index].text)
            orders.append(order + [FREE_MARK])

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

    driver = None
    # root.protocol("WM_DELETE_WINDOW", on_closing)    

    # driver = create_profile_chrome_driver()
    # driver.get("https://nesky.hktemas.com/no-suppliers")
    
    frame = Suplier_Manager_Frame(root, driver=driver)
    frame.grid()    
    root.mainloop()