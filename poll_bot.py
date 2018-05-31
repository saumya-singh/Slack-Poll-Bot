import os
import time
import re, json
from slackclient import SlackClient
from random import randint


slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
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
                return message_list, event["channel"]
    return [], None


def parse_direct_mention(message_text):
    print("=====================")
    matches = re.search(BOT_MESSAGE_REGEX, message_text)
    print(matches.groups())
    print("=====================")
    message_list = re.compile("\s+").split(matches.group(2).strip())
    print(message_list)
    return (matches.group(1), message_list) if matches else (None, [])


def handle_command(message_list, channel):
    default_response = "Not sure what you mean. Try commands @help, @create_poll, @add_options, 'host_poll', 'result'"
    response = None
    attachment_response = None

    if message_list[0] == "create_poll":
        new_poll_id = create_poll_id()
        POLLS[new_poll_id] = {"poll_issue": message_list[1], "options":{}, "host_var": 0}
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(POLLS)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$")
        response = "You have created a new poll. Poll_ID is {}".format(new_poll_id)
        attachment_response = None

    elif message_list[0] == "add_option":
        option_msg = message_list[1]
        poll_id = message_list[2]
        if poll_id in POLLS:
            if POLLS[poll_id]["host_var"] == 1:
                response = "This poll has been hosted, options cannot be added"
            else:
                if option_msg in POLLS[poll_id]["options"]:
                    response = "This option is already present"
                else:
                    POLLS[poll_id]["options"][option_msg] = 0
                    print("&&&&&&&&&&&&&&&&&&&&&&&")
                    print(POLLS)
                    response = "[{}] option has been added to the poll".format(option_msg)
        else:
            response = "Not a valid POLL ID"
        attachment_response = None

    elif message_list[0] == "delete_option":
        option_msg = message_list[1]
        poll_id = message_list[2]
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
        attachment_response = None

    elif message_list[0] == "host_poll":
        poll_id = message_list[1]
        if poll_id not in POLLS:
            response = "Not a valid POLL ID"
        else:
            poll_option_dict = POLLS[poll_id]["options"]
            POLLS[poll_id]["host_var"] = 1
            response = POLLS[poll_id]["poll_issue"]
            attachment_response = make_attachment_response(poll_option_dict)

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response ,
        attachments=attachment_response
    )


def make_attachment_response(poll_option_dict):
    attachment_response = [
            {
                "text": "Give your vote by choosing from the given options",
                "fallback": "You are unable to choose an option",
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
            "confirm": {
                "title": "Are you sure?",
                "text": "Wouldn't you prefer a good game of chess?",
                "ok_text": "Yes",
                "dismiss_text": "No"
            }
        }
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
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
            message_list, channel = parse_bot_commands(slack_client.rtm_read())
            if message_list:
                handle_command(message_list, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
