from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import time
import calmap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
import glob
import json

app = Flask(__name__)
CORS(app)  # enable CORS


@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    task_contents = request.form['task_contents']

    # 如果任务内容为空，直接返回不进行后续处理
    if not task_contents.strip():
      return render_template('index.html')

    task_created = datetime.now()
    task_time = task_created.strftime('%H:%M')
    task_state = 'open'
    task_id = int(time.time())

    task = {
        'task_id': task_id,
        'task_created': task_created.strftime('%Y-%m-%d %H:%M:%S'),
        'task_time': task_time,  # 新的字段，仅显示到分钟
        'task_contents': task_contents,
        'task_state': task_state
    }

    directory = 'task'
    if not os.path.exists(directory):
      os.makedirs(directory)
    file_name = f"./{directory}/{task_created.date()}.json"

    data = []
    if os.path.isfile(file_name):
      with open(file_name, 'r') as file:
        data = json.load(file)
        file.close()

    # 先 flag 这个任务是需要被添加的，如果在后续检查中，存在重复且时间间隔小于30s的任务，我们不添加当前任务
    to_be_appended = True
    for existing_task in data:
      if (existing_task['task_contents'] == task_contents):
        time_gap = datetime.strptime(
            task['task_created'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                existing_task['task_created'], '%Y-%m-%d %H:%M:%S')
        if abs(time_gap.total_seconds()) < 30:
          to_be_appended = False
          break

    if to_be_appended:
      data.append(task)

    with open(file_name, 'w') as file:
      file.write(json.dumps(data, indent=4))

  return render_template('index.html')


@app.route('/getTaskFiles', methods=['GET'])
def get_task_files():
  directory = 'task'
  files = []
  if os.path.exists(directory):
    files = os.listdir(directory)
  return jsonify(files)


@app.route('/getTasks/<filename>', methods=['GET'])
def get_tasks(filename):
  directory = 'task'
  file_path = os.path.join(directory, filename)
  open_tasks = []
  closed_tasks = []

  if os.path.isfile(file_path):
    with open(file_path, 'r') as file:
      tasks = json.load(file)

    for task in tasks:
      if task['task_state'] == 'open':
        open_tasks.append(task)
      elif task['task_state'] == 'closed':
        closed_tasks.append(task)

    return jsonify(open_tasks)
  else:
    return jsonify({"error": "File not found"}), 404


@app.route('/doneTasks/<filename>', methods=['GET'])
def get_done_tasks(filename):
  directory = 'task'
  file_path = os.path.join(directory, filename)

  if os.path.exists(file_path):
    with open(file_path, 'r') as file:
      tasks = json.load(file)
    closed_tasks = [task for task in tasks if task['task_state'] == 'closed']

    return jsonify(closed_tasks)
  else:
    return jsonify({"error": "File not found"}), 404


@app.route('/closeTask/<id>', methods=['POST'])
def close_task(id):
  directory = 'task'
  if os.path.exists(directory):
    files = os.listdir(directory)
    for file_name in files:
      file_path = os.path.join(directory, file_name)
      if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
          tasks = json.load(file)

        # 查找并更新任务状态
        for task in tasks:
          if task['task_id'] == int(id):
            task['task_state'] = 'closed'
            break

        # 写回文件
        with open(file_path, 'w') as file:
          file.write(json.dumps(tasks, indent=4))

  response = jsonify({"message": "Task closed"})
  response.headers[
      'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = '-1'
  return response, 200


def get_done_tasks(filename):
  directory = 'task'
  file_path = os.path.join(directory, filename)

  if os.path.exists(file_path):
    with open(file_path, 'r') as file:
      tasks = json.load(file)
    closed_tasks = [task for task in tasks if task['task_state'] == 'closed']

    return closed_tasks  # 直接返回列表，而不再将其封装成Response
  else:
    return []  # 如果文件不存在，则返回空列表


@app.route('/history')
def history():
  directory = 'task'
  done_tasks_all_files = []
  for filename in os.listdir(directory):
    if filename.endswith('.json'):
      done_tasks = get_done_tasks(filename)
      done_tasks_all_files.extend(done_tasks)
  return render_template('history.html', tables=done_tasks_all_files)


@app.route('/statistics')
def stats():
  return render_template('statistics.html')


@app.route("/get_task_days_data")
def get_task_days_data():
  # We will store our task data in this list
  task_dates = []

  # Get all paths to json files in the 'task' directory
  json_files = glob.glob("task/*.json")

  for json_file in json_files:
    with open(json_file, "r") as file:
      tasks = json.load(file)
      for task in tasks:
        task_dates.append(
            task["task_created"][:10])  # Take the date part of the timestamp

  task_date_counts = Counter(task_dates)  # Count all unique dates

  # Convert the Counter object to a list of dictionaries
  task_day_data = [{
      "date": date,
      "count": count
  } for date, count in task_date_counts.items()]

  # Return data as JSON
  return jsonify(task_day_data)


@app.route("/get_task_hours_data")
def get_task_hours_data():
  # We will store our task data in a dict with default values 0
  task_dates = defaultdict(int)

  # Get all paths to json files in the 'task' directory
  json_files = glob.glob("task/*.json")

  for json_file in json_files:
    with open(json_file, "r") as file:
      tasks = json.load(file)
      for task in tasks:
        # Take the date and hour part of the timestamp
        date_hour_string = task['task_created'][:13]
        task_dates[
            date_hour_string] += 1  # Increase count for the specific hour

  # Convert the dict object to a list of dictionaries
  task_hours_data = [{
      "date": date_hour,
      "count": count
  } for date_hour, count in task_dates.items()]

  # Return data as JSON
  return jsonify(task_hours_data)


def create_heatmap():
  all_days = pd.date_range('1/1/2020', periods=1020, freq='D')
  days = np.random.choice(all_days, 500)
  data = np.random.randint(low=0, high=10, size=len(days))
  events = pd.Series(data, index=days)

  plt.figure(figsize=(10, 3), dpi=300)
  calmap.calendarplot(
      data=events,
      cmap='Greens',
      fig_kws={'figsize': (16, 10)},
      yearlabel_kws={
          'color': 'black',
          'fontsize': 24
      },
  )

  filename = f'heatmap.svg'
  filepath = os.path.join(app.static_folder,
                          filename)  # Modify this path as needed
  plt.savefig(filepath, dpi=200, bbox_inches="tight")
  plt.close(
  )  # Important, because plt keeps the figure in memory until explicitly closed

  return filepath


heatmap_path = create_heatmap()


@app.route('/heatmap')
def heatmap():
  return send_file(heatmap_path, mimetype='image/svg+xml', cache_timeout=0)


if __name__ == "__main__":
  app.run(host='0.0.0.0',port=5000,debug=True)
