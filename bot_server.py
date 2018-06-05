#!usr/bin/env python3
from flask import Flask, request, Response

app = Flask(__name__)
POLLS = {}


@app.route('/create_new_poll', methods=['POST', 'GET'])
def new_poll():
    content = request.get_json()
    print("==========", type(content))
    POLLS.update(content)
    return "Your poll has been hosted"


@app.route('/result_info', methods=['POST', 'GET'])
def poll_result():
    pass



@app.route('/getdata')
def get_data_from_slack():
    content = request.get_json()
    query_params = request.args
    print("===============", content)
    print("===============", query_params)


if __name__ == '__main__':
    app.run(debug=True)
