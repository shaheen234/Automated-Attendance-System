import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, StringVar, OptionMenu, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('attendance.db')

# Sample data
data_query = "SELECT * FROM attendance"  # Use the correct table name 'attendance'
df = pd.read_sql_query(data_query, conn)

# Close the database connection
conn.close()

# Function to update the plot based on selected employee
def update_plot():
    selected_employee = employee_var.get()
    plot_working_hours(selected_employee)

# Function to plot working hours for the selected employee
def plot_working_hours(employee):
    ax.clear()  # Clear previous plot

    employee_data = df[df['class_label'] == employee]

    # List of all days of the week
    all_days = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5', 'day 6', 'day 7']

    for day in all_days:
        try:
            # If there is a record for the day, plot it
            working_hours = sum(employee_data[employee_data['day_of_week'] == day]['total_time_spent'].values)
            color = 'green' if working_hours > 7 else ('red' if working_hours < 4 else 'yellow')
            ax.bar(day, working_hours, color=color)
        except IndexError:
            # If there is no record for the day, plot zero working hours
            ax.bar(day, 0, color='gray')

    ax.set_title(f'Working Hours for {employee}')
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Working Hours')
    canvas.draw()

# Create GUI
root = Tk()
root.title('Working Hours Dashboard')

# Employee selection
employees = df['class_label'].unique()
employee_var = StringVar(root)
employee_var.set(employees[0])  # Set the default employee
employee_menu = OptionMenu(root, employee_var, *employees)
employee_menu_label = Label(root, text='Select Employee:')
employee_menu_label.pack()
employee_menu.pack()

# Update button
update_button = Button(root, text='Update Plot', command=update_plot)
update_button.pack()

# Matplotlib plot
fig, ax = plt.subplots(figsize=(8, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Initialize the plot
plot_working_hours(employees[0])

root.mainloop()
