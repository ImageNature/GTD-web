from flask import Flask, request, redirect, render_template
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)
directory = 'task'
os.makedirs(directory, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
  tasks = defaultdict(list)
  for filename in os.listdir(directory):
    date = filename.replace('.txt', '')
    with open(os.path.join(directory, filename), 'r') as f:
      lines = f.readlines()
      for line in lines:
        tasks[date].append(line.strip())
  return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
  task_content = request.form.get('content')
  now = datetime.now()
  file_string = now.strftime("%Y-%m-%d")
  task_string = now.strftime("%Y-%m-%d-%H-%M") + ' ' + task_content
  with open(os.path.join(directory, f"{file_string}.txt"), 'a') as f:
    f.write(f'{task_string}\n')
  return redirect('/')


if __name__ == '__main__':
  app.run(port=4000)
