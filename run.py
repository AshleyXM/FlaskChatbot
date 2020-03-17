from flask import Flask, request, render_template
from handle_message import handle_text
import json
app = Flask(__name__)

@app.route('/handle_msg',methods=['POST'])
def handle_msg():
  jsondata = json.loads(request.get_data(as_text=True))  #request.get_data(as_text=True):获取前端POST请求传过来的json 数据
  data=jsondata["input_text"]
  return handle_text(data)

@app.route('/', methods=['GET', 'POST'])
def demo():
  if request.method == 'GET':
    return render_template('index.html', input_text = '', output_text = '')

if __name__ == '__main__':
    app.run()