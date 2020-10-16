import os
import sys
import tkinter as tk
import re
from datetime import datetime
import csv
import copy
import json
import requests
import threading
import traceback

import openpyxl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from table import tableGUI
from filtermenu import filterGUI
from diagrams import diagramsGUI
from filemanager import filemanager


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
    def __init__(self):
        self.title(title='Suplier Manager')
        self.__listeners = []
        self.__orders = []
        self.__employers = []
        self.__statusbar = None
        
        self.table = tableGUI.TableGUI(master=self, app=self, height=int(settings['table rows']))
        self.subscribe(self.table)
        self.filter = filterGUI.FilterGui(tearoff=1)
        self.filter.subscribe(self.table)
        self.subscribe(self.filter)
        self.diagrams = diagramsGUI.Diagrams_Frame(master=self, app=self)
        self.subscribe(self.diagrams)

        self.create_widgets()

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
        statusbar.grid(row=0, column=0, columnspan=2, sticky='w'+'e')
        statusvar = tk.StringVar() 
        self.__statusbar = tk.Entry(statusbar, state='readonly', font=("Calibri", 14), width=40, bd=0, textvariable=statusvar, justify='center')
        self.__statusbar.textvariable = statusvar
        self.__statusbar.grid(row=0, column=0, pady=5, sticky='w'+'e')

        read_nes_table_button = tk.Button(buttons_frame, text="read NES orders", font=("Calibri", 12), command=self.read_nes_table)
        read_nes_table_button.grid(row=1, column=0, sticky='w'+'e')

        save_button = tk.Button(buttons_frame, text="save file", font=("Calibri", 12), command=self.save_file)
        save_button.grid(row=1, column=1, sticky='w'+'e')

        # diagrams
        self.diagrams.grid(row=0, column=1, rowspan=2)
        
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
        self.set_status(fg='green', message='start reading table...')

        try:
            nes_orders = Supliers_Table(app=self).get_orders()
        except Exception as e:
            print(e)
            self.set_status(fg='red', message='reading failed')
        else:
            marked_orders = self.mark_orders_by_employers(marked_orders=self.get_orders(), clear_orders=nes_orders)

            self.set_orders(orders=marked_orders)
            self.set_status(fg='green', message='reading succsessfully')

    def get_orders(self) -> list:
        return copy.deepcopy(self.__orders)
    
    def set_orders(self, orders):
        self.__orders = copy.deepcopy(orders)

        self.notify_for_dublicates(orders)
        self.notify(changed='orders')
    
    def notify_for_dublicates(self, orders):
        dublicates = {}
        orders_numbers = [order[MYXLNUMB_INDEX] for order in orders]
        for i, number in enumerate(orders_numbers):
            if orders_numbers.count(number) > 1:
                dublicates[i] = orders[i]
        
        if dublicates:
            message = ''.join([str(k) + ' : ' + str(v) + '\n' for k, v in dublicates.items()])
            tk.messagebox.showwarning(title='dublicates found', message=message)
    
    def mark_orders_by_employers(self, marked_orders, clear_orders) -> list:
        """ Marks orders by name of the employers who have this orders """

        clear_orders = copy.deepcopy(clear_orders)

        for marked in marked_orders:
            for clear in clear_orders:
                if clear[MYXLNUMB_INDEX] == marked[MYXLNUMB_INDEX]:
                    clear[EMPLOYER_INDEX] = marked[EMPLOYER_INDEX]
                    break

        return clear_orders
    
    def get_free_orders(self) -> list:
        free = []

        for order in self.get_orders():
            if order[EMPLOYER_INDEX] == FREE_MARK:
                free.append(order)
        
        return free

    def get_employer_orders(self, employer) -> list:
        employer_orders = []
        for order in self.get_orders():
            if order[EMPLOYER_INDEX] == employer:
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
        return copy.deepcopy(self.__employers)
    
    def set_employers(self, employers : list):
        self.__employers = employers
        self.notify(changed='employers')
    
    def notify(self, changed : str):
        """ Notify listeners about intresting events. Argument changed need for call only one function in listener """

        for listener in self.__listeners:
            if changed == 'employers' and hasattr(listener, "on_employers_changed"):
                listener.on_employers_changed(employers=self.get_employers())
            if changed == 'orders' and hasattr(listener, "on_orders_changed"):
                listener.on_orders_changed(orders=self.get_orders())
    
    def subscribe(self, listener):
        self.__listeners.append(listener)
    
    
    def set_status(self, fg='green', message='task finished successfully'):
        def clear_status_if_contain(text):
            if statusbar.textvariable.get() == text:
                statusbar.textvariable.set('')

        display_time = 6000
        statusbar = self.__statusbar

        statusbar.config(fg=fg)
        statusbar.textvariable.set(message)
        statusbar.update()     
        statusbar.after(display_time, clear_status_if_contain, message)       
    
    def config(self, cnf={}, **kw):
        raise NotImplementedError
    
    def title(self, title):
        raise NotImplementedError

class Suplier_Manager_TopLevel(Suplier_Manager, tk.Toplevel):
    """ Singleton """

    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self)

        self.__class__.instance = self

        mouseX, mouseY = self.get_mouse_position()
        self.geometry(f"+{mouseX}+{mouseY}")
        self.resizable(True, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)   

    def on_closing(self):
            self.destroy()
            plt.close('all') 
                
    def get_mouse_position(self):
        return self.master.winfo_pointerx(), self.master.winfo_pointery()

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "instance"):
            cls.instance.destroy()
        return tk.Toplevel.__new__(cls)
    
    def config(self, cnf={}, **kw):
        tk.Toplevel.config(self, cnf=cnf, **kw)
    
    def title(self, title):
        tk.Toplevel.title(self, title)

class Suplier_Manager_Frame(Suplier_Manager, tk.Frame):
    def __init__(self, master, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)
        Suplier_Manager.__init__(self)

        self.master.resizable(True, False)
    
    def config(self, cnf={}, **kw):
        self.master.config(cnf=cnf, **kw)

    def title(self, title):
        self.master.title(title)

class Supliers_Table(object):    
    """ Singleton """
    
    def __init__(self, app):
        self.app = app
        self.table_url = 'https://apines.hktemas.com/api/orders?noSupplier=1&with=customer;orderItems;shop;bucket&page=%d&limit=5&orderBy=id&sortedBy=desc'
        self.session = requests.Session()
        self.__orders = []

        self.authorize_session(session=self.session)
        self.read_supliers_table()

    def get_orders(self) -> list:
        return copy.deepcopy(self.__orders)
    
    def set_orders(self, orders):
        self.__orders = copy.deepcopy(orders)
        
    def read_supliers_table(self):        
        first_page_data = self.session.get(self.table_url % 1)
        pages = json.loads(first_page_data.text)['last_page']
        orders = []
        threads = []

        orders_dict = {}
        for page in range(1, pages + 1):
            thread = threading.Thread(target=self.get_orders_from_page, args=(page, orders_dict))
            threads.append(thread)
            thread.start()
        
        for index, thread in enumerate(threads):
            thread.join()
            self.app.set_status(fg='black', message='Reading table: page %d / %d' % (index + 1, pages))
        
        for page in range(1, pages + 1):
            orders += orders_dict[page]

        self.set_orders(orders=orders)

    def get_orders_from_page(self, page : int, out_dict : dict):
        page_data = self.session.get(self.table_url % page) 
        orders_data = json.loads(page_data.text)['data']

        orders = []
        for data in orders_data:
            order = []
            order.append(data['number'])
            order.append(data['created_at'].split()[0])
            order.append(data['id'])

            orders.append(order + [FREE_MARK])
        
        out_dict.update({page : orders})

    def authorize_session(self, session):
        user_agent = settings['user agent']
        email = settings['email'] 
        password = settings['password']
        url = "https://apines.hktemas.com/api/signin"

        session.headers.update({'Referer':url, 'User-Agent': user_agent})
        data = {'email' : email, 'password' : password}
        r = session.put(url, data)
        session.headers.update({'authorization' : 'Bearer ' + json.loads(r.text)['token']})

    def __new__(cls, *args, **kw):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
        return cls.instance
    
    
if __name__ == "__main__":

    def on_closing():
            root.destroy()
            plt.close('all')

    root = tk.Tk()

    root.protocol("WM_DELETE_WINDOW", on_closing)    
    
    frame = Suplier_Manager_Frame(root)
    frame.grid()    
    
    root.mainloop()