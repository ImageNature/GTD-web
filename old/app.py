from flask import Flask, request, redirect, render_template
from datetime import datetime
from collections import defaultdict
from itertools import islice
import os
import csv
from chardet.universaldetector import UniversalDetector


def detect_encoding(file_path):
  detector = UniversalDetector()
  with open(file_path, 'rb') as f:
    for line in f:
      detector.feed(line)
      if detector.done:
        break
  detector.close()
  return detector.result['encoding']


app = Flask(__name__)
directory = 'task'
os.makedirs(directory, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
  page = request.args.get('page', default=1, type=int)
  tasks = defaultdict(list)
  for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as f:
      reader = csv.reader(f)
      for row in reader:
        tasks[filename.replace('.csv', '')].append(row[0])
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
  datetime_string = now.strftime("%H:%M")
  filename = os.path.join(directory, f"{date_string}.csv")
  mode = 'a' if os.path.exists(filename) else 'w'
  with open(filename, mode, encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([f'{datetime_string} {task_content}'])
  return redirect('/')


@app.route('/history', methods=['GET'])
def history():
  # 历史任务信息的逻辑
  return render_template('history.html')  # 另一个处理历史任务的模板，位于 template 文件夹下


if __name__ == '__main__':
  app.run(port=4000)