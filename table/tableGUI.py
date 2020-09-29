import tkinter as tk
import tkinter.ttk as ttk
import copy
import math
import pyperclip
import webbrowser


class TableGUI(tk.Frame):
    def __init__(self, master, height, cnf={}, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)

        self.table_height = height
        self.__table_orders = ()
        self.table = None
        self.navigator = None
        self.__listeners = []

        self.create_widgets()
    
    def create_widgets(self):
        self.table = TreeView(master=self, app=self, height=self.table_height, show="headings")
        self.table.grid(row=0, column=0)

        self.navigator = Navigator(master=self, app=self)
        self.subscribe(self.navigator)
        self.navigator.subscribe(self.table)
        self.navigator.grid(row=1, column=0, padx=5, pady=5, sticky='w')

    def get_table_orders(self) -> list:
        return list(copy.deepcopy(self.__table_orders))
    
    def set_table_orders(self, orders):
        old_orders = self.get_table_orders()
        self.__table_orders = tuple(copy.deepcopy(orders))
        self.on_table_orders_changed(old_orders=old_orders)

    def on_orders_changed(self, orders):
        self.set_table_orders(orders=orders)     

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
        if hasattr(self, 'date_reverse'):
            self.date_reverse = not self.date_reverse
        else:
            self.date_reverse = False

        orders = self.get_table_orders()
        orders.sort(key = lambda row: (row[1]), reverse=self.date_reverse)

        self.set_table_orders(orders=orders)
    
    def sort_orders_by_user(self):
        if hasattr(self, 'user_reverse'):
            self.user_reverse = not self.user_reverse
        else:
            self.user_reverse = False
        orders = self.get_table_orders()
        orders.sort(key = lambda row: (row[3], row[1]), reverse=self.user_reverse)

        self.set_table_orders(orders=orders)

class TreeView(ttk.Treeview):
    def __init__(self, master, app, **kw):
        ttk.Treeview.__init__(self, master, **kw)

        self.rows = int(self['height'])
        self.app = app

        self["columns"] = (0, 1, 2, 3)
        self.column(0, width=100)
        self.column(1, width=180)
        self.column(2, width=180)
        self.column(3, width=150)

        self.heading(0, text="№")
        self.heading(1, text="Creation date", command=self.app.sort_orders_by_date)
        self.heading(2, text="MYXL number")
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
            order_number = item["values"][0]
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
        column = int(self.identify_column(self.click_posx)[1:]) - 1
        item = self.item(self.selection()[0])
        pyperclip.copy(item["values"][column])
    
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