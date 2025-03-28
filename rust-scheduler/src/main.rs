use std::collections::HashMap;
//use std::hash::Hash;
use rand::seq::SliceRandom;
use rand::thread_rng;
use serde_derive::Deserialize;
use serde_derive::Serialize;
use std::fs;
use std::path::Path;
// Define Employee struct
#[derive(Serialize, Deserialize, Debug)]
struct Employee {
    name: String,
    prefs: [String; 2],
    days_worked: u32,
    shifts_assigned: Vec<(String, String)>, // or Vec<[String; 2]> if you prefer arrays
}

fn save_to_file(employees: &HashMap<String, Employee>) -> Result<(), Box<dyn std::error::Error>> {
    // Serialize the HashMap to a JSON string
    let json_data = serde_json::to_string_pretty(employees)?;
    // Write it to file
    fs::write("employees.json", json_data)?;
    Ok(())
}

fn save_to_file_schedule(
    schedule: &HashMap<String, HashMap<String, Vec<String>>>,
) -> Result<(), Box<dyn std::error::Error>> {
    // Serialize the HashMap to a JSON string
    let json_data = serde_json::to_string_pretty(schedule)?;
    // Write it to file
    fs::write("schedule.json", json_data)?;
    Ok(())
}

fn load_from_file_schedule() -> Result<HashMap<String, HashMap<String, Vec<String>>>, Box<dyn std::error::Error>> {
    let path = "schedule.json";

    // If file doesn't exist, create an empty one automatically
    if !Path::new(path).exists() {
        fs::write(path, "{}")?;
    }

    // Read the file into a string
    let contents = fs::read_to_string(path)?;
    // Deserialize the JSON back into a HashMap
    let schedule_map: HashMap<String, HashMap<String, Vec<String>>> = serde_json::from_str(&contents)?;
    Ok(schedule_map)
}

// 2) Load employees from "employees.json" (create file if missing)
fn load_from_file() -> Result<HashMap<String, Employee>, Box<dyn std::error::Error>> {
    let path = "employees.json";

    // If file doesn't exist, create an empty one automatically
    if !Path::new(path).exists() {
        fs::write(path, "{}")?;
    }

    // Read the file into a string
    let contents = fs::read_to_string(path)?;
    // Deserialize the JSON back into a HashMap
    let employees_map: HashMap<String, Employee> = serde_json::from_str(&contents)?;
    Ok(employees_map)
}

fn generate_schedule(
    employees: &mut HashMap<String, Employee>,
    days: &[&str],
    shifts: &[&str],
) -> HashMap<String, HashMap<String, Vec<String>>> {
    // Create a hashmap to store the schedule
    let mut schedule: HashMap<String, HashMap<String, Vec<String>>> = HashMap::new();

    'outer: loop {

        // Clear the schedule
        schedule.clear();
        // Clear the employees
        for emp in employees.values_mut() {
            emp.days_worked = 0;
            emp.shifts_assigned.clear();
        }
        // Assign shifts to employees
        // Loop through the days
        for day in days.iter() {
            let mut daily_emps: Vec<String> = employees.keys().cloned().collect(); // get the keys of the employees
            daily_emps.shuffle(&mut thread_rng()); // shuffle the employees

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
                        && !emp.shifts_assigned.iter().any(|(d, _)| d == day)
                    {
                        //println!("Assigning {} to {} shift", emp.name, shift);
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

                if assign < 2 {
                    for emp_id in daily_emps.iter() {
                        let emp = employees.get_mut(emp_id).unwrap();
                        // Check the second preference
                        if emp.days_worked < 5
                            && emp.prefs[1] == shift.to_string()
                            && !emp.shifts_assigned.iter().any(|(d, _)| d == day)
                        {
                            //println!("Assigning {} to {} shift", emp.name, shift);
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
                    for emp_id in eligible.iter() {
                        if assign == 2 {
                            break;
                        }
                        let emp = employees.get_mut(emp_id).unwrap();
                        //println!("Assigning {} to {} shift", emp.name, shift);
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
                    if assign < 2 {
                        println!(
                            "Not enough employees available for {} shift on {}",
                            shift, day
                        );
                        continue 'outer;
                    }
                }
            }
        }
        return schedule;
    }
    //schedule
}

// Function to print the menu
fn menu() {
    println!("Menu:");
    println!("------------------------------");
    println!("1. Add Employee");
    println!("2. Remove Employee");
    println!("3. View Employees");
    println!("4. Generate Schedule");
    println!("5. Clear Schedule");
    println!("6. View Schedule");
    println!("7. Exit");
    println!("------------------------------");
}

fn clear_schedule_from_employees(employees: &mut HashMap<String, Employee>) {
    for emp in employees.values_mut() {
        emp.days_worked = 0;
        emp.shifts_assigned.clear();
    }
}

fn main() {
    // Create a hashmap to store employees
    let mut employees: HashMap<String, Employee> = match load_from_file() {
        Ok(map) => map,
        Err(e) => {
            eprintln!("Error loading file: {}", e);
            HashMap::new() // fallback
        }
    };

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
    let mut schedule: HashMap<String, HashMap<String, Vec<String>>> = match load_from_file_schedule() {
        Ok(map) => map,
        Err(e) => {
            eprintln!("Error loading file: {}", e);
            HashMap::new() // fallback
        }
    };
    // Print the welcome message
    println!("Welcome to the Employee Scheduler!");
    println!("--------------------------------");
    println!("This program will help you schedule employees for shifts.");
    println!("You can add, remove, and view employees.");
    println!("You can also generate and view the schedule.");
    println!("--------------------------------");

    loop {
        // Print the menu
        menu();
        // Get the choice from the user
        println!("Enter your choice: ");
        let mut choice = String::new();
        std::io::stdin()
            .read_line(&mut choice)
            .expect("Failed to read line");
        let choice: u32 = choice.trim().parse().expect("Please type a number!");
        // Match the choice
        match choice {
            1 => {
                //Add Employee
                println!("Enter the name of the employee: ");
                let mut name = String::new();
                std::io::stdin()
                    .read_line(&mut name)
                    .expect("Failed to read line");
                name = name.trim().to_string();
                // Get the preferences of the employee
                println!("Enter the first preference of employee: ");
                let mut prefs: [String; 2] = [String::new(), String::new()];
                std::io::stdin()
                    .read_line(&mut prefs[0])
                    .expect("Failed to read line");
                println!("Enter the second preference of employee: ");
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
                let id = format!("employee{}", employees.len() + 1);
                employees.insert(id, employee);
                println!("Employee added successfully!");
            }
            2 => {
                //Remove Employee
                println!("Enter the id of the employee to remove: ");
                let mut id = String::new();
                std::io::stdin()
                    .read_line(&mut id)
                    .expect("Failed to read line");
                id = id.trim().to_string();
                if employees.remove(&id).is_some() {
                    println!("Employee removed successfully!");
                } else {
                    println!("Employee not found!");
                }
            }
            3 => {
                //View Employees
                println!("Employees: ");
                for (id, employee) in employees.iter() {
                    println!("------------------------------");
                    println!("Name: {:?}", employee.name);
                    println!("Preferences: {:?}", employee.prefs.join(","));
                    println!("Days Worked: {:?}", employee.days_worked);
                    println!("Shifts Assigned: {:?}", employee.shifts_assigned);
                    println!("------------------------------");
                }
            }
            4 => {
                //Generate Schedule
                println!("Generating schedule...");
                schedule = generate_schedule(&mut employees, &days, &shifts);
                println!("Schedule generated successfully!");
            }
            5 => {
                //Clear Schedule
                println!("Clearing schedule...");
                clear_schedule_from_employees(&mut employees);
                schedule.clear();
                println!("Schedule cleared successfully!");
            }
            6 => {
                //View Schedule
                println!("Schedule: ");
                for day in days.iter() {
                    println!("{}:", day);
                    for shift in shifts.iter() {
                        if let Some(shifts_map) = schedule.get(*day) {
                            if let Some(emps) = shifts_map.get(*shift) {
                                println!("\t{}:\t\t{}", shift, emps.join(","));
                            } else {
                                println!("\t\tNo employees for this shift");
                            }
                        } else {
                            println!("Day '{}' not found in schedule", day);
                        }
                    }
                }
            }
            7 => {
                //Exit
                println!("Exiting...");
                break;
            }
            _ => {
                println!("Invalid choice!");
            }
        }
    }

    // Save the employees to file
    match save_to_file(&employees) {
        Ok(_) => println!("Employees saved to file!"),
        Err(e) => eprintln!("Error saving employees: {}", e),
    }

    // Save the schedule to file
    match save_to_file_schedule(&schedule) {
        Ok(_) => println!("Schedule saved to file!"),
        Err(e) => eprintln!("Error saving schedule: {}", e),
    }
}
