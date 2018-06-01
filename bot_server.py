#!usr/bin/env python3
from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/api/getdata')
def bank_data():
    content = request.get_json()
    query_params = request.args
    print("===============", content)
    print("===============", query_params)
    
    # query_dict = query_helper.params_to_dict(query_params)
    # result = query_helper.get_bank_details(query_dict)
    # json_result, status_code = result
    # resp = Response(response=json_result,
    #                 status=status_code,
    #                 mimetype="application/json")
    # print("Sending the final response to the client")
    # return resp


if __name__ == '__main__':
    app.run(debug=True)
