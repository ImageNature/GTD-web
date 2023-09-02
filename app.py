from flask import Flask, request, redirect, render_template
from datetime import datetime
import os

app = Flask(__name__)
directory = 'task'
os.makedirs(directory, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
  tasks = []
  for filename in os.listdir(directory):
    with open(os.path.join(directory, filename), 'r') as f:
      lines = f.readlines()
      for line in lines:
        tasks.append(line.strip())
  return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
  task_content = request.form.get('content')
  now = datetime.now()
  date_string = now.strftime("%Y-%m-%d")
  time_string = now.strftime("%H:%M:%S")
  with open(os.path.join(directory, f"{date_string}.txt"), 'a') as f:
    f.write(f'{time_string} {task_content}\n')
  return redirect('/')


if __name__ == '__main__':
  app.run(port=4000)
