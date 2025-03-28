# Shift Scheduler

This repository contains two versions of a simple program that schedules employees for a 7-day workweek. One implementation is in Python, and another is in Rust. Both versions use similar scheduling logic to distribute employees across morning, afternoon, and evening shifts.

## What Does It Do?
- Collects employees and their preferred shifts
- Assigns employees to shifts over a 7-day period
- Ensures no employee works more than one shift per day
- Ensures each employee works at most 5 days total
- Ensures each shift has two employees
- Resolves conflicts by reassigning employees based on preference, and then randomly if needed

## How the Scheduling Algorithm Works
1. **Shuffle Employees Daily**: Avoids bias by randomizing the order in which employees are considered each day.
2. **First-Preference Assignment**: For each shift, the algorithm first tries to place employees who selected that shift as their first preference.
3. **Second-Preference Assignment**: If a shift still needs spots, employees who chose that shift as their second preference are considered next.
4. **Random Assignment**: Any remaining vacancies are filled randomly, ensuring each day’s shift is fully staffed.
5. **Constraints**: The algorithm checks that no employee exceeds 5 total shifts in the week and that no one is assigned to multiple shifts in the same day.
6. **Retries if Conflicts**: If at any point the constraints aren’t met (e.g., not enough employees for a shift), the scheduler resets and tries again.

---

## Repository Structure

```
Repo
│
├── python-scheduler
│    └── main.py
│
└── rust-scheduler
     └── src
         └── main.rs
```

### Python Version
- **File**: `python-scheduler/main.py`
- **Language**: Python 3
- **Usage**:
    1. Open a terminal.
    2. Navigate to the `python-scheduler` folder.
    3. Run `python main.py` (or `python3 main.py`), depending on your setup.
    4. The script will generate a schedule and print it to your console.

### Rust Version
- **Folder**: `rust-scheduler`
- **Language**: Rust
- **Usage**:
    1. If not already done, initialize a Rust project with `cargo new rust-scheduler`.
    2. Place your scheduling logic into `rust-scheduler/src/main.rs`.
    3. Navigate to the `rust-scheduler` folder.
    4. Run `cargo run`.
    5. The program will compile and then produce the schedule output.

