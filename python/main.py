import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

# ==========================
# 1) Scheduling Logic
# ==========================
def generate_shift_schedule(employees_dict, days, shifts):
    """
    Generates a weekly shift schedule given a dict of employees, 
    their first/second preferences, the days of the week, and the shifts.
    Each shift must be filled by exactly 2 employees if possible.
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
                daily_emps = list(employees_dict.keys())
                random.shuffle(daily_emps)

                for shift in shifts:
                    assigned = 0

                    # First preference pass
                    for emp in daily_emps:
                        data = employees_dict[emp]
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
                        for emp in daily_emps:
                            data = employees_dict[emp]
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
                        eligible = [
                            emp for emp in daily_emps
                            if (employees_dict[emp]['days_worked'] < 5
                                and day not in [d for d, _ in employees_dict[emp]['shifts_assigned']]
                                and emp not in schedule[day][shift])
                        ]
                        random.shuffle(eligible)
                        for emp in eligible:
                            if assigned == 2:
                                break
                            schedule[day][shift].append(emp)
                            employees_dict[emp]['shifts_assigned'].append((day, shift))
                            employees_dict[emp]['days_worked'] += 1
                            assigned += 1

                        if assigned < 2:
                            raise Exception(f"Insufficient employees for {day} - {shift}")
            return schedule
        except Exception:
            # If scheduling fails, reset and try again
            continue


# ==========================
# 2) Global Data & Persistence
# ==========================
# Internally, we still store employees in a dict keyed by "E1," "E2," etc.,
# but each entry has a "name" that we display to the user.
employees = {}
schedule = None
next_emp_id = 1
DATA_FILE = "data.json"

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
shifts = ["Morning", "Afternoon", "Evening"]

def load_data():
    """Load employees and schedule from data.json if it exists."""
    global employees, schedule, next_emp_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        employees = data.get("employees", {})
        schedule = data.get("schedule", None)
        # Determine next_emp_id from the highest ID used
        if employees:
            max_id = max(int(eid[1:]) for eid in employees.keys())  # assume "E" prefix
            next_emp_id = max_id + 1
        else:
            next_emp_id = 1
    else:
        employees = {}
        schedule = None
        next_emp_id = 1

def save_data():
    """Save employees and schedule to data.json."""
    data = {
        "employees": employees,
        "schedule": schedule
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==========================
# 3) Main Window & Frames
# ==========================
root = tk.Tk()
root.title("Employee Shift Scheduler")
root.geometry("1200x700")  # plenty of space for columns
root.resizable(False, False)

# --------------------------
# Apply a Style so grid lines are visible in the Treeviews
style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview",
                background="white",
                foreground="black",
                rowheight=26,
                fieldbackground="white",
                bordercolor="black",
                borderwidth=1)
style.configure("Treeview.Heading",
                relief="solid",
                bordercolor="black",
                borderwidth=1)
style.layout("Treeview", [
    ("Treeview.treearea", {"sticky": "nswe"})
])
# --------------------------

# Top Frame: main buttons
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

btn_add_employee = tk.Button(top_frame, text="Add Employee")
btn_add_employee.pack(side=tk.LEFT, padx=5)

btn_employees = tk.Button(top_frame, text="View Employees")
btn_employees.pack(side=tk.LEFT, padx=5)

btn_assign_shifts = tk.Button(top_frame, text="Assign Shifts")
btn_assign_shifts.pack(side=tk.LEFT, padx=5)

btm_clear_schedule = tk.Button(top_frame, text="Clear Schedule")
btm_clear_schedule.pack(side=tk.LEFT, padx=5)

btn_schedule = tk.Button(top_frame, text="View Schedule")
btn_schedule.pack(side=tk.LEFT, padx=5)


# Center Frame: We will switch between employees_frame and schedule_frame
center_frame = tk.Frame(root)
center_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

employees_frame = tk.Frame(center_frame)
schedule_frame = tk.Frame(center_frame)

# ==========================
# 4) Employees Table
# ==========================
# Columns: S.No, Name, AssignedDays, Pref1, Pref2
emp_columns = ("SNo", "Name", "AssignedDays", "Pref1", "Pref2")
employees_tree = ttk.Treeview(employees_frame, columns=emp_columns, show="headings")

employees_tree.heading("SNo", text="S.No")
employees_tree.heading("Name", text="Name")
employees_tree.heading("AssignedDays", text="Assigned Days")
employees_tree.heading("Pref1", text="1st Pref")
employees_tree.heading("Pref2", text="2nd Pref")

employees_tree.column("SNo", width=60, anchor=tk.CENTER)
employees_tree.column("Name", width=200, anchor=tk.CENTER)
employees_tree.column("AssignedDays", width=120, anchor=tk.CENTER)
employees_tree.column("Pref1", width=120, anchor=tk.CENTER)
employees_tree.column("Pref2", width=120, anchor=tk.CENTER)

# Scrollbar for the employees table
emp_scrollbar = ttk.Scrollbar(employees_frame, orient=tk.VERTICAL, command=employees_tree.yview)
employees_tree.configure(yscroll=emp_scrollbar.set)

employees_placeholder_label = tk.Label(employees_frame, text="No employees found. Add some!")
employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
emp_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

# Button to edit a selected employee
edit_employee_button = tk.Button(employees_frame, text="Edit Selected")

def populate_employees_tree():
    """Clear and re-populate the employees treeview showing S.No, Name, assigned days, prefs."""
    for item in employees_tree.get_children():
        employees_tree.delete(item)
    idx = 1
    for eid, data in employees.items():
        emp_name = data.get("name", eid)  # fallback if name is missing
        p1, p2 = data["prefs"]
        assigned_days = data.get("days_worked", 0)
        employees_tree.insert(
            "",
            tk.END,
            iid=eid,
            values=(idx, emp_name, assigned_days, p1, p2)
        )
        idx += 1

def toggle_employees_view():
    """Show the tree + edit button if employees exist, else show a placeholder."""
    num_emps = len(employees)
    if num_emps == 0:
        employees_tree.pack_forget()
        emp_scrollbar.pack_forget()
        edit_employee_button.pack_forget()
        employees_placeholder_label.pack(pady=20)
    else:
        employees_placeholder_label.pack_forget()
        employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        emp_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        edit_employee_button.pack(side=tk.TOP, anchor="w", pady=5, padx=5)

def show_employees_frame():
    """Show the employees frame, hide schedule frame."""
    schedule_frame.pack_forget()
    populate_employees_tree()
    toggle_employees_view()
    employees_frame.pack(fill=tk.BOTH, expand=True)

# ==========================
# 5) Schedule Table
# ==========================
# Columns: Shift + Monday..Sunday
sched_columns = ("Shift",) + tuple(days)
schedule_tree = ttk.Treeview(schedule_frame, columns=sched_columns, show="headings")

for col in sched_columns:
    schedule_tree.heading(col, text=col)
    if col == "Shift":
        schedule_tree.column(col, width=120, anchor=tk.CENTER)
    else:
        schedule_tree.column(col, width=140, anchor=tk.CENTER)

schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
schedule_scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=schedule_tree.yview)
schedule_tree.configure(yscroll=schedule_scrollbar.set)
schedule_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

schedule_placeholder_label = tk.Label(schedule_frame, text="No schedule found. Please assign shifts!")

def populate_schedule_tree():
    """Populate schedule tree with columns: Shift + each day, rows for each shift."""
    for item in schedule_tree.get_children():
        schedule_tree.delete(item)

    if not schedule:
        return

    # For each shift, create a row with 'Shift' in the first col and the employee NAMES for each day
    for shift_name in shifts:
        row_values = [shift_name.capitalize()]
        for day in days:
            emp_ids = schedule[day][shift_name]  # list of keys like "E1", "E2"
            # Convert each EID to the employee's name
            name_list = []
            for eid in emp_ids:
                e_data = employees.get(eid, {})
                e_name = e_data.get("name", eid)
                name_list.append(e_name)
            row_values.append(", ".join(name_list))
        schedule_tree.insert("", tk.END, iid=shift_name, values=row_values)

def toggle_schedule_view():
    """Show the schedule tree if schedule is present, else show placeholder."""
    if not schedule or len(schedule) == 0:
        schedule_tree.pack_forget()
        schedule_scrollbar.pack_forget()
        schedule_placeholder_label.pack(pady=20)
    else:
        schedule_placeholder_label.pack_forget()
        schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        schedule_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

def show_schedule_frame():
    """Show the schedule frame, hide employees frame."""
    employees_frame.pack_forget()
    populate_schedule_tree()
    toggle_schedule_view()
    schedule_frame.pack(fill=tk.BOTH, expand=True)

# ==========================
# 6) Button Actions
# ==========================
def update_buttons():
    """Enable/disable main buttons based on employee count."""
    num_emps = len(employees)
    if num_emps >= 42:
        btn_add_employee.config(state='disabled')
    else:
        btn_add_employee.config(state='normal')

    if num_emps < 9:
        btn_assign_shifts.config(state='disabled')
    else:
        btn_assign_shifts.config(state='normal')

def add_employee():
    """Open a window for adding a new employee (name + 1st pref, 2nd pref)."""
    add_win = tk.Toplevel(root)
    add_win.title("Add Employee")
    add_win.geometry("300x240")
    add_win.resizable(False, False)

    tk.Label(add_win, text="Name:").pack(pady=5)
    name_var = tk.StringVar()
    name_entry = tk.Entry(add_win, textvariable=name_var)
    name_entry.pack()

    tk.Label(add_win, text="1st Preference:").pack(pady=5)
    pref1_var = tk.StringVar()
    pref1_combo = ttk.Combobox(add_win, textvariable=pref1_var, values=shifts, state="readonly")
    pref1_combo.pack()

    tk.Label(add_win, text="2nd Preference:").pack(pady=5)
    pref2_var = tk.StringVar()
    pref2_combo = ttk.Combobox(add_win, textvariable=pref2_var, values=shifts, state="readonly")
    pref2_combo.pack()

    def on_pref1_selected(event):
        sel = pref1_var.get()
        pref2_combo['values'] = [sh for sh in shifts if sh != sel]
        if pref2_var.get() == sel:
            pref2_var.set("")
    pref1_combo.bind("<<ComboboxSelected>>", on_pref1_selected)

    def on_pref2_selected(event):
        sel = pref2_var.get()
        pref1_combo['values'] = [sh for sh in shifts if sh != sel]
        if pref1_var.get() == sel:
            pref1_var.set("")
    pref2_combo.bind("<<ComboboxSelected>>", on_pref2_selected)

    def save_new_employee():
        nonlocal name_var
        global next_emp_id

        name = name_var.get().strip()
        p1 = pref1_var.get().strip()
        p2 = pref2_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Please enter a name.")
            return
        if not p1 or not p2:
            messagebox.showerror("Error", "Please choose both preferences.")
            return

        # Internally, store as E{id}, but we display only the name in the UI
        emp_id = f"E{next_emp_id}"
        next_emp_id += 1

        employees[emp_id] = {
            "name": name,
            "prefs": [p1, p2],
            "days_worked": 0,
            "shifts_assigned": []
        }
        save_data()
        update_buttons()
        populate_employees_tree()
        toggle_employees_view()
        messagebox.showinfo("Success", f"Employee '{name}' added.")
        add_win.destroy()

    tk.Button(add_win, text="Save", command=save_new_employee).pack(pady=10)

def edit_employee():
    """Edit or delete the selected employee (change name/prefs)."""
    sel = employees_tree.selection()
    if not sel:
        messagebox.showerror("Error", "No employee selected.")
        return
    eid = sel[0]

    emp_data = employees[eid]
    old_name = emp_data.get("name", eid)
    old_prefs = emp_data["prefs"]

    edit_win = tk.Toplevel(root)
    edit_win.title(f"Edit Employee")
    edit_win.geometry("400x300")
    edit_win.resizable(False, False)

    tk.Label(edit_win, text="Name:").pack(pady=5)
    name_var = tk.StringVar(value=old_name)
    name_entry = tk.Entry(edit_win, textvariable=name_var)
    name_entry.pack()

    tk.Label(edit_win, text="1st Preference:").pack(pady=5)
    pref1_var = tk.StringVar(value=old_prefs[0])
    pref1_combo = ttk.Combobox(edit_win, textvariable=pref1_var, values=shifts, state="readonly")
    pref1_combo.pack()

    tk.Label(edit_win, text="2nd Preference:").pack(pady=5)
    pref2_var = tk.StringVar(value=old_prefs[1])
    pref2_combo = ttk.Combobox(edit_win, textvariable=pref2_var, values=shifts, state="readonly")
    pref2_combo.pack()

    def on_edit_pref1_changed(event):
        s = pref1_var.get()
        pref2_combo['values'] = [sh for sh in shifts if sh != s]
        if pref2_var.get() == s:
            pref2_var.set("")
    pref1_combo.bind("<<ComboboxSelected>>", on_edit_pref1_changed)

    def on_edit_pref2_changed(event):
        s = pref2_var.get()
        pref1_combo['values'] = [sh for sh in shifts if sh != s]
        if pref1_var.get() == s:
            pref1_var.set("")
    pref2_combo.bind("<<ComboboxSelected>>", on_edit_pref2_changed)

    def save_changes():
        new_name = name_var.get().strip()
        p1 = pref1_var.get().strip()
        p2 = pref2_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Please enter a name.")
            return
        if not p1 or not p2:
            messagebox.showerror("Error", "Please choose both preferences.")
            return

        employees[eid]["name"] = new_name
        employees[eid]["prefs"] = [p1, p2]
        # If the user changes prefs or name, we reset days_worked & shifts_assigned
        # so the next assignment can consider the new data cleanly.
        #employees[eid]["days_worked"] = 0
        #employees[eid]["shifts_assigned"] = []

        save_data()
        update_buttons()
        populate_employees_tree()
        toggle_employees_view()
        edit_win.destroy()

    def delete_employee():
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{emp_data.get('name', eid)}'?")
        if confirm:
            employees.pop(eid, None)
            save_data()
            update_buttons()
            populate_employees_tree()
            toggle_employees_view()
            edit_win.destroy()

    tk.Button(edit_win, text="Save Changes", command=save_changes).pack(pady=5)
    tk.Button(edit_win, text="Delete Employee", command=delete_employee).pack()

def assign_shifts():
    """Generates a new schedule, updates employees' days_worked, saves data."""
    global schedule
    if len(employees) < 9:
        messagebox.showwarning("Warning", "Need at least 9 employees to assign shifts.")
        return

    # Build a minimal dict for the scheduling function
    sched_emps = {}
    for eid, data in employees.items():
        sched_emps[eid] = {
            "prefs": data["prefs"]
        }

    try:
        new_schedule = generate_shift_schedule(sched_emps, days, shifts)
        # Copy back days_worked/shifts_assigned
        for eid in sched_emps:
            employees[eid]["days_worked"] = sched_emps[eid]["days_worked"]
            employees[eid]["shifts_assigned"] = sched_emps[eid]["shifts_assigned"]

        schedule = new_schedule
        save_data()
        messagebox.showinfo("Success", "Shifts assigned successfully!")
        populate_schedule_tree()
        toggle_schedule_view()

        # Also refresh employees table so "Assigned Days" updates
        populate_employees_tree()
        toggle_employees_view()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_schedule():
    """Clear the current schedule, reset employees' days_worked, save data."""
    global schedule
    if not schedule:
        messagebox.showwarning("Warning", "No schedule to clear.")
        return

    for eid in employees:
        employees[eid]["days_worked"] = 0
        employees[eid]["shifts_assigned"] = []
    schedule = None
    save_data()
    messagebox.showinfo("Success", "Schedule cleared successfully.")
    populate_schedule_tree()
    toggle_schedule_view()

# ==========================
# 7) Wire Up Buttons
# ==========================
btn_employees.config(command=show_employees_frame)
btn_schedule.config(command=show_schedule_frame)
btn_add_employee.config(command=add_employee)
btn_assign_shifts.config(command=assign_shifts)
edit_employee_button.config(command=edit_employee)
btm_clear_schedule.config(command=clear_schedule)

# ==========================
# 8) Start Up
# ==========================
def main():
    load_data()
    update_buttons()  # enable/disable buttons
    show_employees_frame()  # default page
    root.mainloop()

if __name__ == "__main__":
    main()
