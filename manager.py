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
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from table import tableGUI
from filemanager import filemanager
from filtermenu import filterGUI


MYXLNUMB_INDEX = 0
DATE_INDEX = 1
NUMBER_INDEX = 2
EMPLOYER_INDEX = 3
MANAGER_DIR_PATH = os.path.dirname(__file__)
EMPLOYERS_PATH = os.path.join(MANAGER_DIR_PATH, 'employers.txt')
ORDERS_PATH = os.path.join(MANAGER_DIR_PATH, "Orders.xlsx")
FREE_MARK = ' '

settings = filemanager.read_csv_settings(file_path=os.path.join(MANAGER_DIR_PATH, "settings", "settings.csv"))

class Suplier_Manager(object):
    def __init__(self, driver=None):
        self.__driver = None
        self.__listeners = []
        self.__orders = ()
        self.__employers = ()
        
        self.__statusbar = None
        self.table = tableGUI.TableGUI(master=self, app=self, height=int(settings['table rows']))
        self.subscribe(self.table)
        self.filter = filterGUI.FilterGui(tearoff=1)
        self.filter.subscribe(self.table)
        self.subscribe(self.filter)

        self.create_widgets()

        self.set_driver(driver=driver)
        self.set_employers(employers=settings['employers'])
        self.set_orders(self.get_orders_from_file(file_path=ORDERS_PATH))        


    def create_widgets(self):
        self.table.grid(row=0, column=0)

        menubar = tk.Menu()
        menubar.add_cascade(label="Display", menu=self.filter)
        self.config(menu=menubar)

        # buttons
        buttons_frame = tk.Frame(self)
        buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky='w'+'e')

        statusbar = tk.LabelFrame(buttons_frame, text='status')
        statusbar.grid(row=0, column=0, columnspan=3, sticky='w'+'e')
        statusvar = tk.StringVar() 
        self.__statusbar = tk.Entry(statusbar, state='readonly', font=("Calibri", 14), width=40, bd=0, textvariable=statusvar, justify='center')
        self.__statusbar.textvariable = statusvar
        self.__statusbar.grid(row=0, column=0, pady=5, sticky='w'+'e')

        execute_button = tk.Button(buttons_frame, text="execute driver", font=("Calibri", 12), command=self.execute_driver)
        execute_button.grid(row=1, column=0, sticky='w'+'e')

        read_nes_table_button = tk.Button(buttons_frame, text="read NES orders", font=("Calibri", 12), command=self.read_nes_table)
        read_nes_table_button.grid(row=1, column=1, sticky='w'+'e')

        save_button = tk.Button(buttons_frame, text="save file", font=("Calibri", 12), command=self.save_file)
        save_button.grid(row=1, column=2, sticky='w'+'e')


    def save_file(self, file_path=ORDERS_PATH):
        try:
            filemanager.save_orders_to_file(orders=self.get_orders(), file_path=file_path, save_backup=settings['save backups'])
            filemanager.save_employers_data_to_table(employers_data=self.get_employers_data(), table_path=ORDERS_PATH)
        except:
            self.set_status(fg='red', message='Saving file failed')
        else:
            self.set_status(message='The file was saved successfully')
    
    def get_orders_from_file(self, file_path) -> list:
        try:
            orders = filemanager.get_orders_from_file(file_path=file_path)
        except:
            self.set_status(fg='red', message=f'Reading failed {file_path}')
            return []
        else:
            self.set_status(message='File read successfully')
            return orders

    def read_nes_table(self):
        if not self.get_driver():
            self.set_status(fg='red', message='driver error. Execute driver to continue')
            return

        nes_orders = self.get_driver().read_supliers_table()
        marked_orders = self.mark_orders_by_employers(marked_orders=self.get_orders(), clear_orders=nes_orders)

        self.set_orders(orders=marked_orders)
        self.set_status(message='reading succsessfully')

    def execute_driver(self):
        executable_path = os.path.join(MANAGER_DIR_PATH, "chromedriver", "chromedriver.exe")
        profile_path = settings['profile path']

        try:
            driver = Extended_Webdriver.create_profile_chrome_driver(executable_path, profile_path)
        except:
            self.set_status(fg='red', message='driver failed. Close chrome windows to continue')
        else:            
            driver.get("https://nesky.hktemas.com/no-suppliers")
            self.set_driver(driver)
            self.set_status(fg='green', message='driver ready')

    def get_orders(self) -> list:
        return list(copy.deepcopy(self.__orders))
    
    def set_orders(self, orders):
        self.__orders = tuple(copy.deepcopy(orders))
        self.notify()
    
    def mark_orders_by_employers(self, marked_orders, clear_orders) -> list:
        """ Marks orders by name of the employers who have this orders """

        clear_orders = copy.deepcopy(clear_orders)

        for marked in marked_orders:
            for clear in clear_orders:
                if marked[MYXLNUMB_INDEX] == clear[MYXLNUMB_INDEX]:
                    clear[EMPLOYER_INDEX] = marked[EMPLOYER_INDEX]
                    break

        return clear_orders
    
    def get_employer_orders(self, employer) -> list:
        employer_orders = []
        for order in self.get_orders():
            if order[3] == employer:
                employer_orders.append(order)
        
        return employer_orders
    
    def get_employers_data(self) -> dict:
        employers = self.get_employers()
        orders = self.get_orders()
        employers_data = {}

        for employer in employers:
            employers_data[employer] = self.get_employer_orders(employer=employer)

        return employers_data        

    def get_employers(self) -> list:
        return list(copy.deepcopy(self.__employers))
    
    def set_employers(self, employers : list):
        self.__employers = tuple(employers)
        self.notify()
    
    def notify(self):
        for listener in self.__listeners:
            if hasattr(listener, "on_employers_changed"):
                listener.on_employers_changed(employers=self.get_employers())
            if hasattr(listener, "on_orders_changed"):
                listener.on_orders_changed(orders=self.get_orders())
            if hasattr(listener, "on_employers_data_changed"):
                listener.on_employers_data_changed(employers_data=self.get_employers_data())
    
    def subscribe(self, listener):
        self.__listeners.append(listener)
    
    def set_driver(self, driver):
        Extended_Webdriver.extend_driver(driver=driver)
        self.__driver = driver
    
    def get_driver(self) -> webdriver:
        return self.__driver
    
    def set_status(self, fg='green', message='task finished successfully'):
        self.__statusbar.config(fg=fg)
        self.__statusbar.textvariable.set(message)
        self.__statusbar.update()
    
    def config(self, cnf={}, **kw):
        raise NotImplementedError

class Suplier_Manager_TopLevel(Suplier_Manager, tk.Toplevel):
    """ Singleton """

    def __init__(self, master, driver=None, cnf={}, **kw):
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
    
    def config(self, cnf={}, **kw):
        tk.Toplevel.config(self, cnf=cnf, **kw)

class Suplier_Manager_Frame(Suplier_Manager, tk.Frame):
    def __init__(self, master, driver=None, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self, driver)

        self.master.resizable(False, False)
    
    def config(self, cnf={}, **kw):
        self.master.config(cnf=cnf, **kw)

class Extended_Webdriver(object):
    @classmethod
    def extend_driver(cls, driver):
        """ Extending driver functional to all Extended_Webdriver functions """

        if not driver:
            return

        for attr in cls.__dict__:
            if not hasattr(driver.__class__, attr):
                setattr(driver.__class__, attr, cls.__dict__[attr])

    @staticmethod
    def create_profile_chrome_driver(executable_path, profile_path) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument(fr"user-data-dir={profile_path}")
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"

        return webdriver.Chrome(desired_capabilities=caps, executable_path=executable_path, options=chrome_options)          

    def read_supliers_table(self) -> list:
        table_element = self.find_element_by_class_name("table-primary")
        pages_element = table_element.find_element(By.TAG_NAME, "pre")        
        pages = re.search('Page: (\d+) / (\d+)', pages_element.text)
        current_page = int(pages.group(1))
        last_page = int(pages.group(2))
        orders = []

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
        self.execute_script("arguments[0].click()", first_button)        
        WebDriverWait(self, 5).until_not(EC.text_to_be_present_in_element((By.CLASS_NAME, "table-primary"), table_element.text))
    
    def goto_nes_table_next_page(self, table_element):
        """ Press next button in NES table. Checking if table text changed, else page not switched """

        next_button = table_element.find_element_by_link_text("Next")
        self.execute_script("arguments[0].click()", next_button)
        WebDriverWait(self, 5).until_not(EC.text_to_be_present_in_element((By.CLASS_NAME, "table-primary"), table_element.text))

    def read_supliers_page_orders(self, table_element) -> list:
        """ Read supliers MYXLnumber, update date, number columns data. Using search all td elements instead selector because it faster.
            Mark all orders as free by FREE_MARK """

        tbody_element = table_element.find_element(By.CSS_SELECTOR, "tbody")
        rows = len(tbody_element.find_elements(By.CSS_SELECTOR, "tr"))
        td_elements = tbody_element.find_elements(By.CSS_SELECTOR, "td")
        COLUMNS = 8
        
        orders = []

        for row in range(rows):
            order = []
            order.append(td_elements[row * COLUMNS + 4].text)
            order.append(td_elements[row * COLUMNS + 2].text.split(' ')[0])
            order.append(td_elements[row * COLUMNS + 0].text)
            orders.append(order + [FREE_MARK])

        return orders
    
if __name__ == "__main__":

    def on_closing():
            root.destroy()
            plot.close('all')

    root = tk.Tk()

    root.protocol("WM_DELETE_WINDOW", on_closing)    
    
    frame = Suplier_Manager_Frame(root)
    frame.grid()    
    
    root.mainloop()