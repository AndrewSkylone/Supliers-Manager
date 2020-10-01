import tkinter as tk
import tkinter.ttk as ttk
import copy
import math
import pyperclip
import webbrowser
from enum import Enum


MYXLNUMB_INDEX = 0
DATE_INDEX = 1
NUMBER_INDEX = 2
EMPLOYER_INDEX= 3

class TableGUI(tk.Frame):
    def __init__(self, master, app, height, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)

        self.app = app
        self.table_height = height
        self.__table_orders = []
        self.table = TreeView(master=self, app=self, height=self.table_height, show="headings")
        self.navigator = Navigator(master=self, app=self)
        self.__listeners = []

        self.subscribe(self.navigator)
        self.navigator.subscribe(self.table)

        self.create_widgets()
    
    def create_widgets(self):
        self.table.grid(row=0, column=0, columnspan=2)
        self.navigator.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        employers_frame = tk.Frame(self)
        employers_frame.grid(row=1, column=1, padx=5, pady=5, sticky='e'+'w'+'n')

        variable = tk.StringVar()
        self.employers_menu = tk.OptionMenu(employers_frame, variable, ' ')
        self.employers_menu.config(font=('Arial', 13), width=16)
        self.employers_menu.variable = variable
        self.employers_menu.grid(row=0, column=0, sticky='w' + 'e')

        send_orders_button = tk.Button(employers_frame, text="send orders", font=('Arial', 12), command=self.send_orders)
        send_orders_button.grid(row=1, column=0, sticky='w' + 'e')

    def get_table_orders(self) -> list:
        return copy.deepcopy(self.__table_orders)
    
    def set_table_orders(self, orders):
        old_orders = self.get_table_orders()
        self.__table_orders = copy.deepcopy(orders)
        self.on_table_orders_changed(old_orders=old_orders)

    def on_filter_orders_changed(self, orders):
        self.set_table_orders(orders=sorted(orders, key=lambda order: order[DATE_INDEX]))

    def on_employers_changed(self, employers):
        menu = self.employers_menu["menu"]
        menu.delete(0, "end")
        employers = [' '] + [employer for employer in employers]        
        for employer in employers:
            menu.add_command(label=employer,
                            command=lambda value=employer:self.employers_menu.variable.set(value))

    def subscribe(self, listener):
        self.__listeners.append(listener)

    def on_table_orders_changed(self, old_orders):
        if len(old_orders) == len(self.get_table_orders()):
            self.table.show_page(page=int(self.navigator.page.get()))
        else:
            self.navigator.page.set(1)  

        for listener in self.__listeners:
            listener.on_table_orders_changed(orders=self.get_table_orders())
    
    def sort_orders_by_date(self):
        orders = self.get_table_orders()
        orders.sort(key = lambda row: (row[DATE_INDEX]))

        self.set_table_orders(orders=orders)
    
    def sort_orders_by_user(self):
        orders = self.get_table_orders()
        orders.sort(key = lambda row: (row[EMPLOYER_INDEX], row[DATE_INDEX]))

        self.set_table_orders(orders=orders)
    
    def send_orders(self):
        orders = self.app.get_orders()
        orders_numbers = [order[MYXLNUMB_INDEX] for order in orders]
        selected_orders = self.table.get_selected_orders()

        for selected in selected_orders:
            order_index = orders_numbers.index(selected[MYXLNUMB_INDEX])
            orders[order_index][EMPLOYER_INDEX] = self.employers_menu.variable.get()
        
        self.app.set_orders(orders=orders)

class TreeView(ttk.Treeview):
    def __init__(self, master, app, **kw):
        ttk.Treeview.__init__(self, master, **kw)

        self.rows = int(self['height'])
        self.app = app

        self["columns"] = (0, 1, 2, 3)
        self.column(0, width=180)
        self.column(1, width=110)
        self.column(2, width=100)
        self.column(3, width=150)

        self.heading(0, text="MYXL number")
        self.heading(1, text="Updated date", command=self.app.sort_orders_by_date)
        self.heading(2, text="№")
        self.heading(3, text="User", command=self.app.sort_orders_by_user)

        for i in range(self.rows):
            self.insert("", "end", iid=i, tags="all")
        self.tag_configure("all", font=("Arial", 11))
        self.tag_bind("all", "<Return>", self.open_selected_in_browser)
        self.tag_bind("all", "<Button-1>", self.on_left_click)
        self.tag_bind("all", "<Control-c>", self.copy_value)

    def show_page(self, page):
        orders = self.app.get_table_orders()

        self.clear()
        index = (page - 1) * self.rows
        for iid, row in enumerate(orders[index : index + self.rows]):
            self.item(iid, values=row)

        self.selection_remove(self.get_children())
    
    def on_page_changed(self, page):
        self.show_page(page=page)

    def clear(self):
        for iid in range(self.rows):
            self.item(iid, value=[" "] * 4)
    
    def open_selected_in_browser(self, event):
        selected = self.selection()
        for iid in selected:
            item = self.item(iid)
            order_number = item["values"][NUMBER_INDEX]
            webbrowser.open_new_tab(f"https://nesky.hktemas.com/orders/{order_number}")
            self.selection_toggle(iid)
    
    def get_selected_orders(self, *args) -> list:
        selected_rows = self.selection()

        selected_orders = []
        for iid in selected_rows:
            item = self.item(iid)
            selected_orders.append(item['values'])
        
        return selected_orders          

    def on_left_click(self, event):
        self.click_posx = event.x
        row = self.identify_row(event.y)
        self.selection_toggle(row)

    def copy_value(self, event):
        selected_orders = self.get_selected_orders()
        result = ''

        for order in selected_orders:
            for col in (MYXLNUMB_INDEX, DATE_INDEX):
                result += str(order[col]) + '\t'
            result += '\n' 
        
        pyperclip.copy(result)
    
class Navigator(tk.Frame):
    def __init__(self, master, app, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)

        self.app = app
        self.__listeners = []

        self.page = tk.StringVar(value=1)
        self.page.trace('w', self.on_page_changed)
        self.pages = tk.StringVar(value="Page: 1 / 1")
        self.orders_num = tk.StringVar(value="Total items: 0")

        self.create_widgets()
    
    def create_widgets(self):
        buttons = ["First", "Previous", "Next", "Last"]

        for column, goto in zip((0, 1, 3, 4), buttons):
            button = tk.Button(self, text=goto, font=("Calibri", 12), width=7)
            button.config(command=lambda goto=goto: self.goto_page(goto_page=goto))
            button.grid(row=0, column=column, sticky="w"+"e")

        self.page_entry = tk.Entry(self, width=5, font=("Calibri", 16), justify="center")
        self.page_entry.bind("<Return>", lambda e: self.goto_page(goto_page=self.page_entry.get()))
        self.page_entry.grid(row=0, column=2, sticky="w"+"e")

        pages_entry = tk.Entry(self, state="readonly", textvariable=self.pages, bd=0, justify="left")
        pages_entry.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

        total_entry = tk.Entry(self, state="readonly", textvariable=self.orders_num, bd=0, justify="left")
        total_entry.grid(row=2, column=0, columnspan=2, sticky="w")

    def goto_page(self, goto_page : str):
        pages = self.get_pages_num()
        page = int(self.page.get())

        if goto_page == "Last":
            page = pages
        if goto_page == "First":
            page = 1
        if goto_page == "Previous":
            page -= 1
        if goto_page == "Next":
            page += 1
        if goto_page.isnumeric():
            page = int(goto_page)
        
        if 1 <= page and page <= pages:
            self.page.set(page)
    
    def subscribe(self, listener):
        self.__listeners.append(listener)    
    
    def on_page_changed(self, *args):
        pages = self.get_pages_num()
        page = int(self.page.get())        

        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, page)
        self.pages.set(f"Page: {page} / {pages}")

        for listener in self.__listeners:
            listener.on_page_changed(page=int(self.page.get()))
    
    def get_pages_num(self) -> int:
        orders_num = len(self.app.get_table_orders())
        table_rows = self.app.table_height  

        return math.ceil(orders_num / table_rows)
 
    def on_table_orders_changed(self, orders):
        self.orders_num.set(f"Total items: {len(orders)}")