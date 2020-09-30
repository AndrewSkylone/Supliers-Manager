import openpyxl
import os
from datetime import datetime


def save_orders_to_file(orders, file_path, save_backup=False):        
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    for row in orders:
        sheet.append(row)

    workbook.save(filename=file_path)

    if save_backup == "Yes":
        date = datetime.today().date()
        dir_path = os.path.dirname(file_path)
        workbook.save(filename=os.path.join(dir_path, 'Backups', f'{date}.xlsx'))

def save_employers_data_to_table(employers : dict, table_path):
    workbook = openpyxl.load_workbook(table_path)
    workbook.create_sheet(title='Employers')
    sheet = workbook['Employers']

    for col, name in enumerate(employers):
        sheet.cell(row=1, column=col + 1, value=name)
        orders = employers[name]
        for row in range(len(orders)):
            sheet.cell(row=row + 2, column=col + 1, value=orders[row])

    workbook.save(table_path)

def get_employers_from_file(file_path) -> list:
    with open(file_path, 'r') as f:
        print([line.strip() for line in f.readlines()])
        return [line.strip() for line in f.readlines()]

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
