import csv
import os
import tkinter as tk


SETTINGS_DIR_PATH = os.path.dirname(__file__)

class Settings_TopLevel(tk.Toplevel):
    """ Singleton """

    def __init__(self, master, cfg={}, **kw):
        tk.Toplevel.__init__(self, master, cfg, **kw)

        self.settings = {}

        self.create_widgets()
    
    def create_widgets(self):
        pass



