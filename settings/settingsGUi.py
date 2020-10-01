import csv
import os
import tkinter as tk


SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.csv')
TEST_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'test settings.csv')

class Settings_Gui():
    def __init__(self):
        self.settings = read_csv_settings(file_path=SETTINGS_PATH)

        write_csv_settings(settings=self.settings, file_path=TEST_SETTINGS_PATH)
        self.create_widgets()
    
    def create_widgets(self):
        pass

class Settings_TopLevel(Settings_Gui, tk.Toplevel):
    """ Singleton """

    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)


def read_csv_settings(file_path) -> dict:

    settings = {}
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        settings = {k:[v] for k, v in next(reader).items()}
            
        for row in reader:
            for header in settings:
                if row[header]:
                    settings[header] += [row[header]]

    # change {key : [one value]} to {key : one value}
    for header in settings:
        if len(settings[header]) <= 1:
            settings[header] = settings[header][0]       
    
    return settings

def write_csv_settings(settings : dict, file_path=SETTINGS_PATH):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = list(settings.keys())
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)

        writer.writeheader()

        for header in settings:
            if type(settings[header]) == list:
                for row in settings[header]:
                    writer.writerow({header : row})
            else:
                writer.writerow({header : settings[header]})

if __name__ == "__main__":
    settings = Settings_Gui()