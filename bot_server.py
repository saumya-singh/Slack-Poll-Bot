#!usr/bin/env python3
from flask import Flask, request, jsonify
import json
import urllib

app = Flask(__name__)
POLLS = {}


@app.route('/create_new_poll', methods=['POST'])
def new_poll():
    content = request.get_json()
    POLLS.update(content)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
    print(POLLS)
    return "Your poll has been hosted"


@app.route('/result_info', methods=['POST'])
def poll_result():
    content = request.get_json()
    print("ID", content)
    poll_id = content["poll_id"]
    print("pppppppppppppppppppppooooollll", poll_id)
    result = json.dumps(POLLS[poll_id])
    return jsonify(POLLS[poll_id])


@app.route('/', methods=['POST'])
def polled_option():
    print(POLLS)
    content = request.get_data()
    print("***********************************")
    print(content)
    decode_content = content.decode("utf-8")
    str_content = urllib.parse.unquote_plus(urllib.parse.unquote(decode_content))
    required_str_content = (str_content.split("="))[1]
    content_dict = json.loads(required_str_content)
    print("======================", content_dict)

    print("################33", POLLS)
    poll_id = content_dict["callback_id"]
    user_id = content_dict["user"]["id"]
    print("=================user_id: ", type(user_id))
    user_name = content_dict["user"]["name"]
    vote_by_user = content_dict["actions"][0]["value"]
    user_dict = {user_id: user_name}

    if user_id in POLLS[poll_id]["options"][vote_by_user]:
        return 'You have already opted for this option !!!'
    else:
        POLLS[poll_id]["options"][vote_by_user].update(user_dict)
        print("#############################", POLLS)
        return 'You have cast your vote!!!'
    # return 'You are welcome!!!'


@app.route('/', methods=['GET'])
def message():
    return "WELCOME !!!!"
