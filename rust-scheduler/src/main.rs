use std::collections::HashMap;
use rand::seq::SliceRandom;
use rand::thread_rng;

// Define Employee struct
#[derive(Debug)]
struct Employee {
    name: String,
    prefs: [String; 2],
    days_worked: u32,
    shifts_assigned: Vec<(String, String)>, // or Vec<[String; 2]> if you prefer arrays
}

fn main() {
    // Create a hashmap to store employees
    let mut employees: HashMap<String, Employee> = HashMap::new();
    
    // Define the days and shifts
    let days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ];
    let shifts = ["Morning", "Afternoon", "Evening"];
    // Create a hashmap to store the schedule
    let mut schedule: HashMap<String, HashMap<String, Vec<String>>> = HashMap::new();
    // Get the number of employees
    println!("Enter the number of employees: ");
    let mut num_employees = String::new();
    std::io::stdin()
        .read_line(&mut num_employees)
        .expect("Failed to read line");
    let num_employees: u32 = num_employees.trim().parse().expect("Please type a number!");


    // Loop through the number of employees and get their details
    for i in 0..num_employees {
        // Get the name of the employee
        println!("Enter the name of employee {}: ", i + 1);
        let mut name = String::new();
        std::io::stdin()
            .read_line(&mut name)
            .expect("Failed to read line");

        // Get the preferences of the employee
        println!("Enter the first preference of employee {}: ", i + 1);
        let mut prefs: [String; 2] = [String::new(), String::new()];
        std::io::stdin()
            .read_line(&mut prefs[0])
            .expect("Failed to read line");

        println!("Enter the second preference of employee {}: ", i + 1);
        std::io::stdin()
            .read_line(&mut prefs[1])
            .expect("Failed to read line");

        // Create an employee object and add it to the hashmap
        let employee = Employee {
            name,
            prefs,
            days_worked: 0,
            shifts_assigned: Vec::new(),
        };
        let id = format!("employee{}", i + 1);
        employees.insert(id, employee);
    }

    

    // Assign shifts to employees
    // Loop through the days
    for day in days.iter() {
        let mut daily_emps: Vec<String> = employees.keys().cloned().collect();// get the keys of the employees
        daily_emps.shuffle(&mut thread_rng());// shuffle the employees

        // Loop through the shifts
        for shift in shifts.iter() {
            let mut assign = 0;

            // Loop through the employees
            for emp_id in daily_emps.iter() {
                let emp = employees.get_mut(emp_id).unwrap();
                //println!("Just looking whats there in each employee: {:?}", emp);

                // Check the first preference
                if emp.days_worked < 5
                    && emp.prefs[0] == shift.to_string()
                    && emp.shifts_assigned.iter().any(|(d, _)| d != day)
                {
                    println!("Assigning {} to {} shift", emp.name, shift);
                    schedule
                        .entry(day.to_string())
                        .or_insert(HashMap::new())
                        .entry(shift.to_string())
                        .or_insert(Vec::new())
                        .push(emp.name.to_string());
                    emp.days_worked += 1;
                    emp.shifts_assigned
                        .push((day.to_string(), shift.to_string()));
                    assign += 1;
                    if assign == 2 {
                        break;
                    }
                }
            }

            if assign <2 {
                for emp_id in daily_emps.iter() {
                    let emp = employees.get_mut(emp_id).unwrap();
                    // Check the second preference
                    if emp.days_worked < 5
                        && emp.prefs[1] == shift.to_string()
                        && emp.shifts_assigned.iter().any(|(d, _)| d != day)
                    {
                        println!("Assigning {} to {} shift", emp.name, shift);
                        schedule
                            .entry(day.to_string())
                            .or_insert(HashMap::new())
                            .entry(shift.to_string())
                            .or_insert(Vec::new())
                            .push(emp.name.to_string());
                        emp.days_worked += 1;
                        emp.shifts_assigned
                            .push((day.to_string(), shift.to_string()));
                        assign += 1;
                        if assign == 2 {
                            break;
                        }
                    }
                }
            }

            //Random assignment pass
            if assign < 2 {

                let mut eligible: Vec<String> = daily_emps
                .iter()
                .filter(|emp_id| {
                    // 1) Check days_worked < 5
                    let emp_data = employees.get(*emp_id).unwrap();
                    if emp_data.days_worked >= 5 {
                        return false;
                    }

                    // 2) Check day not in assigned days
                    //    i.e., employee hasn't been assigned to `day`
                    let already_assigned_to_day = emp_data
                        .shifts_assigned
                        .iter()
                        .any(|(assigned_day, _)| assigned_day == day);
                    if already_assigned_to_day {
                        return false;
                    }

                    // 3) Check if employee not already in schedule[day][shift]
                    //    i.e., `emp_id` isn't in that list
                    let empty = Vec::new();
                    let shift_emps = schedule
                        .get(*day)
                        .and_then(|shifts_map| shifts_map.get(*shift))
                        .unwrap_or(&empty);
                    if shift_emps.contains(&emp_data.name) {
                        return false;
                    }

                    // If all checks pass:
                    true
                })
                // Convert &String references into owned Strings
                .cloned()
                // Finally collect
                .collect();

                // Randomly select an employee from `eligible`
                eligible.shuffle(&mut thread_rng());
                for emp_id in eligible.iter(){
                    if assign == 2 {
                        break;
                    }
                    let emp = employees.get_mut(emp_id).unwrap();
                    println!("Assigning {} to {} shift", emp.name, shift);
                    schedule
                        .entry(day.to_string())
                        .or_insert(HashMap::new())
                        .entry(shift.to_string())
                        .or_insert(Vec::new())
                        .push(emp.name.to_string());
                    emp.days_worked += 1;
                    emp.shifts_assigned
                        .push((day.to_string(), shift.to_string()));
                    assign += 1;
                }

            }
        }
    }

    // Print the schedule
    println!("{:?}", schedule);
}
