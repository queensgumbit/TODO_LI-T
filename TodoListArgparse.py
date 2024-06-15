#to do list using argparse libary! COMMAND-LIKE PROJECT

#add <Text for the >   ->> Will add a task
#modify <ID> <New text>    ->> Will change an existing task
# show <ID>                 ->> Will show a single task text

#list  ->> Will show all tasks

# done -> Will mark the task done
#new feature - set time to do each task
#new feature - how much time has passed
#new feature - set the task to half done
#new feature - priority

#STORING THROUGH PICKLE LIBRARY



import argparse
import pickle
import time
import threading

class TaskEntry:
    def __init__(self, task_id, task, status="TODO", timer_duration=None, timer_start_time=None, priority="undefined", due_date=None, tags=None, timestamp=None):
        self.task_id = task_id
        self.task = task
        self.status = status
        self.timer_duration = timer_duration
        self.timer_start_time = timer_start_time
        self.priority = priority
        self.due_date = due_date
        self.tags = tags if tags else []
        self.timestamp = timestamp if timestamp else time.time()

    def to_dict(self):
        return {
            "id": self.task_id,
            "task": self.task,
            "status": self.status,
            "timer_duration": self.timer_duration,
            "timer_start_time": self.timer_start_time,
            "priority": self.priority,
            "due_date": self.due_date,
            "tags": self.tags,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data):
        return TaskEntry(
            task_id=data["id"],
            task=data["task"],
            status=data.get("status", "TODO"),
            timer_duration=data.get("timer_duration"),
            timer_start_time=data.get("timer_start_time"),
            priority=data.get("priority"),
            due_date=data.get("due_date"),
            timestamp=data.get("timestamp", time.time())
        )

    def set_timer(self, duration):
        self.timer_duration = duration
        self.timer_start_time = time.time()

    def get_remaining_time(self):
        if self.timer_duration and self.timer_start_time:
            elapsed_time = time.time() - self.timer_start_time
            remaining_time = self.timer_duration - elapsed_time
            if remaining_time > 0:
                return remaining_time
            else:
                return 0
        return None


class TaskDb:
    def __init__(self, filename='tasks.pkl'):
        self.filename = filename

    def load_tasks(self):
        try:
            with open(self.filename, 'rb') as file:
                tasks_data = pickle.load(file)
                return [TaskEntry.from_dict(task) for task in tasks_data]
        except FileNotFoundError:
            return []

    def save_tasks(self, tasks):
        with open(self.filename, 'wb') as file:
            pickle.dump([task.to_dict() for task in tasks], file)


class TaskManager:
    def __init__(self):
        self.task_db = TaskDb()
        self.todo_list = self.task_db.load_tasks()
        self.task_id_counter = max((task.task_id for task in self.todo_list), default=0) + 1

    def add_task(self, task_description, priority="undefined", due_date=None):
        task = TaskEntry(self.task_id_counter, task_description, priority=priority, due_date=due_date)
        self.todo_list.append(task)
        self.task_db.save_tasks(self.todo_list)
        print(f"Added: {task_description} - Priority: {priority} - Due Date: {due_date} - Task <ID>: {self.task_id_counter}")
        self.task_id_counter += 1

    def modify_task(self, task_id, new_description):
        for task in self.todo_list:
            if task.task_id == task_id:
                task.task = new_description
                self.task_db.save_tasks(self.todo_list)
                print(f"Modified task with ID {task_id}. New text: {new_description}")
                return
        print(f"No task found with ID {task_id}")

    def list_tasks(self):
        if not self.todo_list:
            print("No tasks in the todo list.")
        else:
            for task in self.todo_list:
                print(f"ID: {task.task_id}, Task: {task.task}, Priority: {task.priority}")

    def show_task(self, task_id):
        for task in self.todo_list:
            if task.task_id == task_id:
                current_time = time.time()
                elapsed_time = current_time - task.timestamp
                minutes, seconds = divmod(elapsed_time, 60)
                remaining_time = task.get_remaining_time()
                if remaining_time is not None:
                    timer_minutes, timer_seconds = divmod(remaining_time, 60)
                    timer_str = f", Timer: {int(timer_minutes)} minutes and {int(timer_seconds)} seconds remaining"
                else:
                    timer_str = ""
                print(f"Task ID: {task.task_id} - Task: {task.task} - Status: {task.status} - priority: {task.priority} - Time Passed: {int(minutes)} minutes and {int(seconds)} seconds{timer_str}")
                return
        print(f"No task found with ID {task_id}")

    def mark_done(self, task_id):
        for task in self.todo_list:
            if task.task_id == task_id:
                task.status = "DONE"
                self.task_db.save_tasks(self.todo_list)
                print(f'Marking the task with ID {task_id} as done.')
                return
        print('No task found with this ID')

    def mark_halfdone(self, task_id):
        for task in self.todo_list:
            if task.task_id == task_id:
                task.status = "HALF DONE"
                self.task_db.save_tasks(self.todo_list)
                print(f'Marking the task with ID {task_id} as half done.')
                return
        print('No task found with this ID')

    def set_timer(self, task_id, seconds):
        for task in self.todo_list:
            if task.task_id == task_id:
                task.set_timer(seconds)
                timer_thread = threading.Timer(seconds, self.mark_halfdone, args=[task_id]) # the task's status to be automatically updated to "HALF DONE" after the specified amount of time has elapsed.
                timer_thread.start()
                self.task_db.save_tasks(self.todo_list)
                print(f"Timer set for task ID {task_id} to be done in {seconds} seconds.")
                return
        print('No task found with this ID')

    def time_passed(self, task_id):
        for task in self.todo_list:
            if task.task_id == task_id:
                current_time = time.time()
                elapsed_time = current_time - task.timestamp
                minutes, seconds = divmod(elapsed_time, 60)
                print(f"The time that has passed since you added the task '{task.task}' is {int(minutes)} minutes and {int(seconds)} seconds.")
                return
        print(f"No task found with ID {task_id}")

    def priority(self, task_id, new_priority):
        for task in self.todo_list:
            if task.task_id == task_id:
                task.priority = new_priority
                self.task_db.save_tasks(self.todo_list)
                print(f'changing the priority the task with ID {task_id} to {new_priority}.')
                return
        print('No task found with this ID')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-add', nargs='+', type=str, help='Add task to the todo list')
    parser.add_argument('-priority', type=str, help='Priority of the task', default='low')
    parser.add_argument('-due_date', type=str, help='Due date of the task')
    parser.add_argument('-modify', nargs='+', type=str, metavar=('ID', 'new_text'), help='Modify an existing task. Enter task ID and the new text.')
    parser.add_argument('-list', action='store_true', help='Show the whole todo list')
    parser.add_argument('-show', type=int, metavar='ID', help='Show a single task by ID')
    parser.add_argument('-done', type=int, help='Mark task as done')
    parser.add_argument('-halfdone', type=int, help='Mark the task as half done')
    parser.add_argument('-set_timer', nargs=2, type=int, help='Set a timer for a task. Provide task ID and seconds.')
    parser.add_argument('-timepassed', type=int, help='Check how much time has passed since you added the task')
    parser.add_argument('-set_priority',nargs='+', type= str, help= 'Specify the priority of the task')


    args = parser.parse_args()


    task_manager = TaskManager()



    if args.add:
        task_description = ' '.join(args.add)
        task_manager.add_task(task_description, priority=args.priority, due_date=args.due_date)

    if args.modify and len(args.modify) >= 2:
        task_id = int(args.modify[0])
        new_description = ' '.join(args.modify[1:])
        task_manager.modify_task(task_id, new_description)

    if args.list:
        task_manager.list_tasks()

    if args.show is not None:
        task_manager.show_task(args.show)

    if args.done is not None:
        task_manager.mark_done(args.done)

    if args.halfdone is not None:
        task_manager.mark_halfdone(args.halfdone)

    if args.set_timer is not None:
        task_id, seconds = args.set_timer
        task_manager.set_timer(task_id, seconds)

    if args.timepassed is not None:
        task_manager.time_passed(args.timepassed)

    if args.set_priority and len(args.set_priority) == 2:
        task_id = int(args.set_priority[0])
        priority = args.set_priority[1]
        task_manager.priority(task_id, priority)



if __name__ == "__main__":
    main()





