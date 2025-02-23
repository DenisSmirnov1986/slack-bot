from get_random_user import get_random_reviewer, create_reviewer, mark_reviewer, add_group, \
                            get_all_reviwers, get_all_users, add_to_command, add_email
from user import User
import os
# Use the package we installed
from slack_bolt import App
from slack_sdk import WebClient
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
import sys
import secrets
import re

# Slack bolt - wtf
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN", ""),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET", "")
)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))


def get_user_info(user_id):
    result = client.users_info(user=user_id)
    return result["user"]["profile"]["display_name"]

def parseParameters(text):
    results = re.findall(r'[\w]*:', text)
    parameterDict = {}
    for i in range(len(results)):
        result = results[i]
        key = result[:-1]
        index = text.find(result)
        nextIndex = len(text)
        if i + 1 < len(results):
            nextResult = results[i + 1]
            nextIndex = text.find(nextResult)
        start = index + len(result)
        end = int(nextIndex)
        value = text[start : end]
        parameterDict[key] = value
    return parameterDict

def get_user_info_by_login(user_login):
    result = client.users_list()
    for user in result["members"]:
        print(user)
        # Key user info on their unique user ID
        # user_id = user["id"]
        # # Store the entire user object (you may not need all of the info)
        # users_store[user_id] = user


@app.command("/random-reviewer")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    random_users = get_random_reviewer(command["user_id"])
    if len(random_users) == 2:
        if 'text' in command:
            say(f"{name} Ваш ревьювер <@{random_users[0].id}> и <@{random_users[1].id}> {command['text']} 🤘")
        else:
            say(f"{name} Ваш ревьювер <@{random_users[0].id}> и <@{random_users[1].id}> 🤘")
        if random_users[0].email != "" and random_users[0].email is not None:
            say(f"{random_users[0].email.decode('utf-8')}")
        if random_users[1].email != "" and random_users[1].email is not None:
            say(f"{random_users[1].email.decode('utf-8')}")
    elif len(random_users) == 3:
        if 'text' in command:
            say(f"{name} Ваш ревьювер <@{random_users[0].id}> и <@{random_users[1].id}> и <@{random_users[2].id}> {command['text']} 🤘")
        else:
            say(
                f"{name} Ваш ревьювер <@{random_users[0].id}> и <@{random_users[1].id}> и <@{random_users[2].id}> 🤘")
    else:
        say(f"{name} Что-то пошло не так - напиши Денису")


@app.command("/all_users")
def all_users(ack, say, command):
    ack()
    users = get_all_users()
    for user in users:
        name = get_user_info(user.id)
        say(f"{name} ({user.id}) в стриме {user.group} в команде {user.command} активный {user.is_active} email {user.email}")


@app.command("/add_me_to_reviewers")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    parameters = parseParameters(command["text"])
    stream = parameters.get("stream","none").casefold().strip()
    team = parameters.get("team", "ios").casefold().strip()
    email = parameters.get("email", "").casefold().strip()
    create_reviewer(command["user_id"], name, stream, team, email)
    say(f"{name} Вы успешно добавлены как ревьювер. Стрим {stream}; команда {team}")

@app.command("/on_vacation")
def on_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    mark_reviewer(command["user_id"], "False")
    say(f"{name} Вы успешно временно удалены из ревьюверов")


@app.command("/add_group")
def on_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    group = command["text"].casefold().strip()
    add_group(command["user_id"], group)
    say(f"{name} Вы успешно добавлены в стрим {group}")


@app.command("/returned_from_vacation")
def returned_from_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    mark_reviewer(command["user_id"], "True")
    say(f"{name} Вы успешно вернулись в ревьюверы")


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler runs App's dispatch method
    return handler.handle(request)


@flask_app.route("/users", methods=["GET"])
def users():
    return "OK"


@flask_app.route("/add_users", methods=["GET"])
def add_users():
    return "OK"


@flask_app.route("/back_vacation", methods=["GET"])
def back_vacation():
    return "OK"


