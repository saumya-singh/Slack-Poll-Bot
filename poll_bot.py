import os
import time
import re, json
import requests
from random import randint
from slackclient import SlackClient


# slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient("xoxb-370962232400-371666328802-wMxdEM9gulNBXD1m6hvXbb0M")
starterbot_id = None

RTM_READ_DELAY = 1
COMMAND = ["help", "create_poll", "add_options", "host_poll", "result"]
BOT_MESSAGE_REGEX = r"^<@(|[WU].+?)>(.*)"
POLLS = {}


def parse_bot_commands(slack_events):
    print("****************************")
    print(slack_events)
    print("****************************")
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message_list = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message_list, event["channel"], event["user"]
    return [], None, None


def parse_direct_mention(message_text):
    print("=====================")
    matches = re.search(BOT_MESSAGE_REGEX, message_text)
    try:
        print(matches.groups())
        print("=====================")
        message_list = re.compile("\s+").split(matches.group(2).strip(), 1)
        print(message_list)
        return (matches.group(1), message_list) if matches else (None, [])
    except:
        return (None, [])


def handle_command(message_list, channel, user_id):
    default_response = "Not sure what you mean. Try commands 'help',\
     'create_poll', 'add_option', 'delete_option', 'list_options', \
     'host_poll', 'show_poll', 'result'"
    response = None
    attachment_response = None

    if message_list[0] == "create_poll":
        if len(message_list) == 1:
            response = "Please provide the Issue for the poll."
        else:
            new_poll_id = create_poll_id()
            POLLS[new_poll_id] = {"poll_issue": message_list[1], "options":{}, "host_var": 0}
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print(POLLS)
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
            response = "You have created a new poll. Poll_ID is {}".format(new_poll_id)

    elif message_list[0] == "add_option":
        if len(message_list) == 1:
            response = "Please provide the option and Poll ID"
        else:
            try:
                poll_id, option_msg = re.compile("\s+").split(message_list[1], 1)
                if poll_id in POLLS:
                    if POLLS[poll_id]["host_var"] == 1:
                        response = "This poll has been hosted, options cannot be added"
                    else:
                        if option_msg in POLLS[poll_id]["options"]:
                            response = "This option is already present"
                        else:
                            POLLS[poll_id]["options"][option_msg] = {}
                            print("&&&&&&&&&&&&&&&&&&&&&&&")
                            print(POLLS)
                            response = "[{}] option has been added to the poll".format(option_msg)
                else:
                    response = "Not a valid POLL ID"
            except ValueError:
                response = "Please provide an option to be added and ID"


    elif message_list[0] == "delete_option":
        if len(message_list) == 1:
            response = "Please provide the option and Poll ID"
        else:
            try:
                poll_id, option_msg = re.compile("\s+").split(message_list[1], 1)
                if poll_id in POLLS:
                    if POLLS[poll_id]["host_var"] == 1:
                        response = "This poll has been hosted, options cannot be deleted"
                    else:
                        if option_msg not in POLLS[poll_id]["options"]:
                            response = "This option is not present for the given ID"
                        else:
                            del POLLS[poll_id]["options"][option_msg]
                            print("&&&&&&&&&&&&&&&&&&&&&&&")
                            print(POLLS)
                            response = "[{}] option has been removed from the poll".format(option_msg)
                else:
                    response = "Not a valid POLL ID"
            except ValueError:
                response = "Please provide an option to be added and ID"


    elif message_list[0] == "list_options":
        if len(message_list) == 1:
            response = "Please provide the Poll ID"
        else:
            poll_id = message_list[1]
            if poll_id not in POLLS:
                response = "Not a valid POLL ID"
            else:
                options_list = POLLS[poll_id]["options"].keys()
                if options_list:
                    response = "List of options for the poll - {}".format(POLLS[poll_id]["poll_issue"])
                    attachment_resp = []
                    for option in options_list:
                        attachment_resp.append({"text": option})
                    attachment_response = attachment_resp
                else:
                    response = "Options are yet to be added"

    elif message_list[0] == "host_poll":
        if len(message_list) == 1:
            response = "Please provide the Poll ID"
        else:
            poll_id = message_list[1]
            if poll_id not in POLLS:
                response = "Not a valid POLL ID"
            else:
                if POLLS[poll_id]["host_var"] == 1:
                    response = "This poll has already been hosted"
                else:
                    POLLS[poll_id]["host_var"] = 1
                    poll_details = POLLS[poll_id]
                    poll = {poll_id: poll_details}
                    attachment_response = None
                    url = "https://shrouded-chamber-98821.herokuapp.com/create_new_poll"
                    payload = json.dumps(poll)
                    headers = {
                        'content-type': "application/json",
                        'cache-control': "no-cache"
                        }
                    response = requests.post(url, data=payload, headers=headers)

    elif message_list[0] == "show_poll":
        if len(message_list) == 1:
            response = "Please provide the Poll ID"
        else:
            poll_id = message_list[1]
            if poll_id not in POLLS:
                response = "Not a valid POLL ID"
            else:
                if POLLS[poll_id]["host_var"] == 0:
                    response = "This poll has not been hosted yet"
                else:
                    poll_option_dict = POLLS[poll_id]["options"]
                    response = POLLS[poll_id]["poll_issue"]
                    attachment_response = make_attachment_response(poll_option_dict, poll_id)

        slack_client.api_call(
            "chat.postEphemeral",
            channel=channel,
            user=user_id,
            text=response,
            attachments=attachment_response
        )
        return


    elif message_list[0] == "result":
        if len(message_list) == 1:
            response = "Please provide the Poll ID"
        else:
            poll_id = message_list[1]
            if poll_id not in POLLS:
                response = "Not a valid POLL ID"
            else:
                url = "https://shrouded-chamber-98821.herokuapp.com/result_info"
                payload = json.dumps({"poll_id": poll_id})
                headers = {
                    'content-type': "application/json",
                    'cache-control': "no-cache"
                    }
                result_json = requests.post(url, data=payload, headers=headers)
                print("=========", result_json.text, "==========")
                calculate_result(result_json.text)


    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response ,
        attachments=attachment_response
    )


def calculate_result(updated_polls_dict):
    total_votes = 0
    no_of_voters = {}
    no_of_options = len(updated_polls_dict["options"])
    for option, voters_dict in updated_polls_dict["options"]:
        no_of_voters[option] = len(voters_dict)
        total_votes += len(voters_dict)




def make_attachment_response(poll_option_dict, poll_id):
    attachment_response = [
            {
                "text": "Give your vote by choosing from the given options",
                "fallback": "You are unable to choose an option",
                "callback_id": poll_id,
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": []
            }
        ]

    poll_option_list = poll_option_dict.keys()
    for option in poll_option_list:
        one_action = {
            "name": "poll",
            "text": option,
            "type": "button",
            "value": option
        }
        print(one_action)
        attachment_response[0]["actions"].append(one_action)
    return attachment_response


def create_poll_id():
    new_poll_id = str(randint(100000, 999999))
    if new_poll_id in POLLS:
        create_poll_id()
    else:
        return new_poll_id


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            message_list, channel, user_id = parse_bot_commands(slack_client.rtm_read())
            if message_list:
                handle_command(message_list, channel, user_id)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
