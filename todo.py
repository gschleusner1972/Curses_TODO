import curses
from datetime import datetime
import csv
import os

def format_row(row, widths):
    """ Format a single row based on column widths """
    return " | ".join(str(field).ljust(width) for field, width in zip(row, widths))

def load_tasks(filename):
    """ Load tasks from a CSV file """
    tasks = []
    if os.path.exists(filename):
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # Check if the row is not empty
                    task = {
                        "name": row[0],
                        "completed": row[1].lower() == 'true',
                        "priority": int(row[2]),
                        "description": row[3]
                    }
                    tasks.append(task)
    return tasks

def save_tasks(filename, tasks):
    """ Save tasks to a CSV file """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for task in tasks:
            row = [task['name'], task['completed'], task['priority'], task['description']]
            writer.writerow(row)

def main(stdscr):
    # Initialize color schemes
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Active task color
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Completed task color
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # Incomplete task color
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Edit text color
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlighted task color

    # Load tasks from file
    tasks_file = "G:/Git_2/Curses_TODO/tasks.csv"
    tasks = load_tasks(tasks_file)

    current_row = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if current_row >= len(tasks):
            current_row = len(tasks) - 1

        # Prepare table data without sorting
        table_data = []
        for task in tasks:  # Using the tasks list directly
            row = [task['name'],
                   'Yes' if task['completed'] else 'No',
                   task.get('priority', '1'),
                   task.get('description', 'No description'),
                   datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            table_data.append(row)

        # Calculate column widths
        headers = ["Task Name", "Completed", "Priority", "Description", "Timestamp"]
        col_widths = [max(len(str(row[i])) for row in table_data + [headers]) for i in range(len(headers))]

        # Print table headers
        stdscr.addstr(0, 0, format_row(headers, col_widths))

        # Print the tasks
        for idx, row in enumerate(table_data):
            formatted_row = format_row(row, col_widths)
            if idx == current_row:
                stdscr.attron(curses.color_pair(5))  # Highlight selected row
                stdscr.addstr(idx + 2, 0, formatted_row)
                stdscr.attroff(curses.color_pair(5))
            else:
                stdscr.addstr(idx + 2, 0, formatted_row)

        # Draw a line to separate the tasks and the bottom text
        stdscr.hline(height - 4, 0, '-', width)

        # Instructions
        stdscr.addstr(height - 2, 0, "Arrows to navigate, 'a' add, 'd' delete, 't' toggle, 'e' edit desc, 'p' edit prio, 's' save, 'q' exit.")

        # Refresh the screen
        stdscr.refresh()

        # Handle user input
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(tasks) - 1:
            current_row += 1
        elif key == ord('a'):
            task_name = "Task " + str(len(tasks) + 1)
            tasks.append({"name": task_name, "completed": False, "priority": 1, "description": ""})
        elif key == ord('d') and tasks:
            tasks.pop(current_row)
            if current_row > 0:
                current_row -= 1
        elif key == ord('t') and tasks:
            tasks[current_row]['completed'] = not tasks[current_row]['completed']
        elif key == ord('e') and tasks:  # Edit description
            curses.echo()
            stdscr.attron(curses.color_pair(4))  # Edit text color
            stdscr.addstr(height - 3, 0, "Enter new description: ")
            stdscr.attroff(curses.color_pair(4))
            stdscr.refresh()
            description = stdscr.getstr(height - 3, 21, 60).decode('utf-8')
            tasks[current_row]['description'] = description.strip()
            curses.noecho()
        elif key == ord('p') and tasks:  # Edit priority
            curses.echo()
            stdscr.attron(curses.color_pair(4))  # Edit text color
            stdscr.addstr(height - 3, 0, "Enter new priority (1-5): ")
            stdscr.attroff(curses.color_pair(4))
            stdscr.refresh()
            priority_str = stdscr.getstr(height - 3, 26, 3).decode('utf-8')
            priority = int(priority_str) if priority_str.isdigit() else 1
            tasks[current_row]['priority'] = max(1, min(priority, 5))
            curses.noecho()
        elif key == ord('s'):  # Save tasks to file
            save_tasks(tasks_file, tasks)
            stdscr.addstr(height - 3, 0, "Tasks saved successfully.")
            stdscr.refresh()
            curses.napms(1500)  # Display message for 1.5 seconds
        elif key == ord('q'):
            break

curses.wrapper(main)
