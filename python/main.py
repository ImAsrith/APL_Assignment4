import tkinter as tk
from tkinter import ttk, messagebox
import random

# ==========================
# Scheduling logic
# ==========================
def generate_shift_schedule(employees_dict, days, shifts):
    """
    Generates a weekly shift schedule given a dict of employees, 
    their first/second preferences, the days of the week, and the shifts.
    Each shift is filled by exactly 2 employees if possible.
    """
    def reset_data():
        for data in employees_dict.values():
            data['shifts_assigned'] = []
            data['days_worked'] = 0
        return {day: {shift: [] for shift in shifts} for day in days}

    while True:
        try:
            schedule = reset_data()
            for day in days:
                daily_employees = list(employees_dict.keys())
                random.shuffle(daily_employees)

                for shift in shifts:
                    assigned = 0

                    # First preference pass
                    for emp in daily_employees:
                        data = employees_dict[emp]
                        # data['prefs'][0] is the first preference
                        if (data['days_worked'] < 5 
                            and day not in [d for d, _ in data['shifts_assigned']] 
                            and shift == data['prefs'][0]):
                            schedule[day][shift].append(emp)
                            data['shifts_assigned'].append((day, shift))
                            data['days_worked'] += 1
                            assigned += 1
                            if assigned == 2:
                                break

                    # Second preference pass
                    if assigned < 2:
                        for emp in daily_employees:
                            data = employees_dict[emp]
                            # data['prefs'][1] is the second preference
                            if (data['days_worked'] < 5 
                                and day not in [d for d, _ in data['shifts_assigned']] 
                                and shift == data['prefs'][1] 
                                and emp not in schedule[day][shift]):
                                schedule[day][shift].append(emp)
                                data['shifts_assigned'].append((day, shift))
                                data['days_worked'] += 1
                                assigned += 1
                                if assigned == 2:
                                    break

                    # Random assignment pass (if still not enough)
                    if assigned < 2:
                        eligible_emps = [
                            emp for emp in daily_employees
                            if (employees_dict[emp]['days_worked'] < 5 
                                and day not in [d for d, _ in employees_dict[emp]['shifts_assigned']] 
                                and emp not in schedule[day][shift])
                        ]
                        random.shuffle(eligible_emps)
                        for emp in eligible_emps:
                            if assigned == 2:
                                break
                            schedule[day][shift].append(emp)
                            employees_dict[emp]['shifts_assigned'].append((day, shift))
                            employees_dict[emp]['days_worked'] += 1
                            assigned += 1

                        # If still fewer than 2 assigned for this shift, fail and retry.
                        if assigned < 2:
                            raise Exception(f"Insufficient employees for {day} - {shift}")

            return schedule

        except Exception:
            # If scheduling fails, reset and try again
            continue

# ==========================
# Global data for GUI
# ==========================
employees = {}       # Ex: { "E1": {"name": "Alice", "prefs": ["morning", "afternoon"]}, ... }
schedule = None      # Will store the final schedule after assignment
next_emp_id = 1      # We'll increment this each time we add a new employee

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
shifts = ["morning", "afternoon", "evening"]

# ==========================
# Tkinter GUI
# ==========================
def update_buttons():
    """Enable/disable buttons based on number of employees."""
    num_emps = len(employees)
    # Disable Add Employee if we have >= 42 employees
    if num_emps >= 42:
        add_employee_button.config(state='disabled')
    else:
        add_employee_button.config(state='normal')

    # Disable Assign Shifts if fewer than 9 employees
    if num_emps < 9:
        assign_shifts_button.config(state='disabled')
    else:
        assign_shifts_button.config(state='normal')

def add_employee():
    """Open a window that collects employee name (optional) and prefs, then saves."""
    add_win = tk.Toplevel(root)
    add_win.title("Add Employee")

    # Name (optional)
    tk.Label(add_win, text="Employee Name (optional):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    name_entry = tk.Entry(add_win)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    # First preference
    tk.Label(add_win, text="First Preference:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    pref1_var = tk.StringVar()
    pref1_combo = ttk.Combobox(add_win, textvariable=pref1_var, values=shifts, state='readonly')
    pref1_combo.grid(row=1, column=1, padx=5, pady=5)

    # Second preference
    tk.Label(add_win, text="Second Preference:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    pref2_var = tk.StringVar()
    pref2_combo = ttk.Combobox(add_win, textvariable=pref2_var, values=shifts, state='readonly')
    pref2_combo.grid(row=2, column=1, padx=5, pady=5)

    # When user picks first preference, remove that from second preference
    def update_pref2_options(event):
        p1 = pref1_var.get()
        new_options = [sh for sh in shifts if sh != p1]
        pref2_combo['values'] = new_options
        pref2_var.set("")
    pref1_combo.bind("<<ComboboxSelected>>", update_pref2_options)

    def save_employee():
        global next_emp_id  # Use the global variable, so we can increment it
        e_name = name_entry.get().strip()
        p1 = pref1_var.get().strip()
        p2 = pref2_var.get().strip()

        if not p1 or not p2:
            messagebox.showerror("Error", "Please choose both preferences.")
            return

        emp_id = f"E{next_emp_id}"
        next_emp_id += 1

        # If name was not provided, just store the ID
        employees[emp_id] = {
            "name": e_name if e_name else emp_id,
            "prefs": [p1, p2]
        }

        messagebox.showinfo("Success", f"Employee '{emp_id}' added!")
        add_win.destroy()
        update_buttons()

    tk.Button(add_win, text="Save", command=save_employee).grid(row=3, column=0, columnspan=2, pady=10)

def view_employees():
    """Open a window showing all employees in a text box."""
    view_win = tk.Toplevel(root)
    view_win.title("View Employees")

    text_area = tk.Text(view_win, width=60, height=15)
    text_area.pack(padx=10, pady=10)

    if not employees:
        text_area.insert(tk.END, "No employees available.\n")
    else:
        for idx, (eid, data) in enumerate(employees.items(), start=1):
            text_area.insert(tk.END, f"{idx}. {eid} - Name: {data['name']}, Prefs: {data['prefs']}\n")

    text_area.config(state='disabled')

def assign_shifts_action():
    """Generate the weekly schedule by calling generate_shift_schedule."""
    global schedule

    if len(employees) < 9:
        messagebox.showwarning("Not Enough Employees", "Need at least 9 employees to assign shifts.")
        return

    # The function expects each employee's dict to have a "prefs" key
    # We'll build a fresh dictionary with only "prefs" (the function doesn't need the "name")
    sched_emps = {eid: {"prefs": data["prefs"]} for eid, data in employees.items()}

    try:
        schedule = generate_shift_schedule(sched_emps, days, shifts)
        messagebox.showinfo("Success", "Shifts assigned successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Could not assign shifts: {str(e)}")

def view_shifts():
    """Display the assigned schedule in a table if it exists."""
    if schedule is None:
        messagebox.showerror("Error", "No schedule found. Please assign shifts first.")
        return

    view_shifts_win = tk.Toplevel(root)
    view_shifts_win.title("View Shifts")

    header_font = ("Arial", 10, "bold")

    # Create table header: empty cell on top-left, then each day across columns
    tk.Label(view_shifts_win, text="Day/Shift", borderwidth=1, relief="solid", width=16)\
        .grid(row=0, column=0)
    for col_idx, day_name in enumerate(days, start=1):
        tk.Label(view_shifts_win, text=day_name, borderwidth=1, relief="solid",
                 width=16, font=header_font)\
            .grid(row=0, column=col_idx)

    # For each shift (row), for each day (column), show the assigned employees
    for row_idx, shift_name in enumerate(shifts, start=1):
        # Shift name on first column
        tk.Label(view_shifts_win, text=shift_name.capitalize(), borderwidth=1, relief="solid", 
                 width=16, font=header_font)\
            .grid(row=row_idx, column=0)

        for col_idx, day_name in enumerate(days, start=1):
            # schedule[day_name][shift_name] is a list of employee IDs
            assigned_emp_ids = schedule[day_name][shift_name]
            # Build a string that shows EID + (Name) if available
            cell_entries = []
            for eid in assigned_emp_ids:
                if eid in employees:
                    cell_entries.append(f"{eid}({employees[eid].get('name', eid)})")
                else:
                    cell_entries.append(eid)
            cell_text = ", ".join(cell_entries)

            tk.Label(view_shifts_win, text=cell_text, borderwidth=1, relief="solid", width=12)\
                .grid(row=row_idx, column=col_idx)

# ============================================
# Initialize the main Tkinter window
# ============================================
root = tk.Tk()
root.title("Employee Shift Scheduler")

# Main buttons
add_employee_button = tk.Button(root, text="Add Employee", command=add_employee)
add_employee_button.grid(row=0, column=0, padx=10, pady=10)

view_employees_button = tk.Button(root, text="View Employees", command=view_employees)
view_employees_button.grid(row=0, column=1, padx=10, pady=10)

assign_shifts_button = tk.Button(root, text="Assign Shifts", command=assign_shifts_action)
assign_shifts_button.grid(row=0, column=2, padx=10, pady=10)

view_shifts_button = tk.Button(root, text="View Shifts", command=view_shifts)
view_shifts_button.grid(row=0, column=3, padx=10, pady=10)

# Set initial button states
update_buttons()

# Start the GUI event loop
root.mainloop()
