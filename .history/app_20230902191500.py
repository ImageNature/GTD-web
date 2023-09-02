from flask import Flask, request, redirect, render_template
from datetime import datetime
from collections import defaultdict
from itertools import islice
import os

app = Flask(__name__)
directory = 'task'
os.makedirs(directory, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
  page = request.args.get('page', default=1, type=int)
  tasks = defaultdict(list)
  for filename in os.listdir(directory):
    with open(os.path.join(directory, filename), 'r') as f:
      lines = f.readlines()
      for line in lines:
        tasks[filename.replace('.txt', '')].append(line.strip())
  task_items = list(tasks.items())
  start = (page - 1) * 50
  end = start + 50
  page_tasks = dict(islice(task_items, start, end))
  last_page = len(task_items) <= end
  return render_template(
      'index.html', tasks=page_tasks, page=page, last_page=last_page)


@app.route('/add', methods=['POST'])
def add():
  task_content = request.form.get('content')
  now = datetime.now()
  date_string = now.strftime("%Y-%m-%d")
  datetime_string = now.strftime("%Y-%m-%d-%H-%M")
  with open(os.path.join(directory, f"{date_string}.txt"), 'a') as f:
    f.write(f'{datetime_string} {task_content}\n')
  return redirect('/')


if __name__ == '__main__':
  app.run(port=4000)
