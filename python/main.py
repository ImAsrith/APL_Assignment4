import random

def generate_shift_schedule(employees, days, shifts):
    def reset_data():
        for data in employees.values():
            data['shifts_assigned'] = []
            data['days_worked'] = 0
        return {day: {shift: [] for shift in shifts} for day in days}

    while True:
        try:
            schedule = reset_data()
            for day in days:
                daily_employees = list(employees.keys())
                random.shuffle(daily_employees)

                for shift in shifts:
                    assigned = 0

                    # First preference pass
                    for emp in daily_employees:
                        data = employees[emp]
                        if data['days_worked'] < 5 and day not in [d for d, _ in data['shifts_assigned']] and shift == data['prefs'][0]:
                            schedule[day][shift].append(emp)
                            data['shifts_assigned'].append((day, shift))
                            data['days_worked'] += 1
                            assigned += 1
                            if assigned == 2:
                                break

                    # Second preference pass
                    if assigned < 2:
                        for emp in daily_employees:
                            data = employees[emp]
                            if data['days_worked'] < 5 and day not in [d for d, _ in data['shifts_assigned']] and shift == data['prefs'][1] and emp not in schedule[day][shift]:
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
                            if employees[emp]['days_worked'] < 5 and day not in [d for d, _ in employees[emp]['shifts_assigned']] and emp not in schedule[day][shift]
                        ]
                        random.shuffle(eligible_emps)
                        for emp in eligible_emps:
                            if assigned == 2:
                                break
                            schedule[day][shift].append(emp)
                            employees[emp]['shifts_assigned'].append((day, shift))
                            employees[emp]['days_worked'] += 1
                            assigned += 1

                        if assigned < 2:
                            raise Exception(f"Insufficient employees for {day} - {shift}")

            return schedule

        except Exception as e:
            continue  # Reset and retry

# Example Usage
employees = {
    'E1': {'prefs': ['morning', 'afternoon']},
    'E2': {'prefs': ['afternoon', 'evening']},
    'E3': {'prefs': ['evening', 'morning']},
    'E4': {'prefs': ['morning', 'evening']},
    'E5': {'prefs': ['afternoon', 'morning']},
    'E6': {'prefs': ['evening', 'afternoon']},
    'E7': {'prefs': ['morning', 'afternoon']},
    'E8': {'prefs': ['afternoon', 'evening']},
    'E9': {'prefs': ['evening', 'morning']}
}

# Days and shifts
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
shifts = ['morning', 'afternoon', 'evening']

final_schedule = generate_shift_schedule(employees, days, shifts)

# Print schedule
for day, shifts_assigned in final_schedule.items():
    print(f"\n{day}:")
    for shift, emps in shifts_assigned.items():
        print(f"  {shift.capitalize()}: {', '.join(emps)}")


print('The final schedule is:', final_schedule)
