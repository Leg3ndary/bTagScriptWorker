"""
MIT License

Copyright (c) 2022 Ben

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

import json
import os
import sys
import urllib
from datetime import datetime
from random import randint
from urllib.parse import unquote

import bTagScript as tse
import redis
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

client = redis.from_url(
    url=os.getenv("url"),
    username="default",
    password=os.getenv("password"),
    decode_responses=True,
)

class FakeAvatar:
    """
    Creating a fake avatar object
    """

    def __init__(self) -> None:
        """
        Initializing the fake avatar object
        """
        self.url = None


class FakeMember:
    """
    Creating a fake discord.py member
    """

    def __init__(self, user: dict) -> None:
        """
        Initializing the fake member
        """
        self.name = user.get("username", "")
        self.created_at = datetime.fromtimestamp(
            int(user.get("created_at", 0))
            if user.get("created_at", "").isdigit()
            else 0
        )
        self.id = user.get("id", "")  # pylint: disable=C0103
        self.timestamp = datetime.now()
        self.color = user.get("color", "")
        self.display_name = user.get("name", "")
        self.display_avatar = FakeAvatar()
        self.display_avatar.url = user.get("avatar", "")
        self.discriminator = user.get("discriminator", "0001")
        self.joined_at = datetime.fromtimestamp(
            int(user.get("joined_at", 0)) if user.get("joined_at", "").isdigit() else 0
        )
        self.mention = user.get("mention", "")
        self.bot = False
        self.banner = FakeAvatar()


class FakeChannel:
    """
    Creating a fake discord.py channel

    {
        "channel_type": "textchannel",
        "nsfw": self.object.nsfw,
        "mention": self.object.mention,
        "topic": self.object.topic or None,
        "slowmode": self.object.slowmode_delay,
        "id": base.id,
        "created_at": base.created_at,
        "timestamp": int(base.created_at.timestamp()),
        "name": getattr(base, "name", str(base)),
    }"""

    def __init__(self, channel: dict) -> None:
        """
        Initializing the fake channel
        """
        self.nsfw = channel.get("nsfw", False) if channel.get("nsfw") is bool else False
        self.mention = channel.get("mention", "")
        self.topic = channel.get("topic", "")
        self.slowmode_delay = channel.get("slowmode", 0)
        self.id = channel.get("id", "")  # pylint: disable=C0103
        self.created_at = datetime.fromtimestamp(
            int(channel.get("created_at", 0))
            if channel.get("created_at", "").isdigit()
            else 0
        )
        self.timestamp = datetime.now()
        self.name = channel.get("name", "")


tse_blocks = [
    tse.block.MathBlock(),
    tse.block.RandomBlock(),
    tse.block.RangeBlock(),
    tse.block.AnyBlock(),
    tse.block.IfBlock(),
    tse.block.AllBlock(),
    tse.block.BreakBlock(),
    tse.block.StrfBlock(),
    tse.block.StopBlock(),
    tse.block.VarBlock(),
    tse.block.LooseVariableGetterBlock(),
    tse.block.EmbedBlock(),
    tse.block.ReplaceBlock(),
    tse.block.PythonBlock(),
    tse.block.URLEncodeBlock(),
    tse.block.URLDecodeBlock(),
    tse.block.RequireBlock(),
    tse.block.BlacklistBlock(),
    tse.block.CommandBlock(),
    tse.block.OverrideBlock(),
    tse.block.RedirectBlock(),
    tse.block.CooldownBlock(),
    tse.block.LengthBlock(),
    tse.block.CountBlock(),
    tse.block.CommentBlock(),
    tse.block.OrdinalAbbreviationBlock(),
    tse.block.DebugBlock(),
    tse.block.DeleteBlock(),
    tse.block.ReactBlock(),
]
tsei = tse.interpreter.Interpreter(blocks=tse_blocks)

app = Flask("bTagScriptWorker")
CORS(app)


def decode_tagscript(tagscript: str) -> str:
    """
    clean the tagscript
    """
    tagscript = (
        tagscript.replace("Ꜳ", "\\")
        .replace("₩", "/")
        .replace("ꜳ", "<")
        .replace("ꜵ", ">")
        .replace("Ꜷ", ".")
    )
    return tagscript


def encode_tagscript(tagscript: str) -> str:
    """
    clean the tagscript
    """
    tagscript = (
        tagscript.replace("\\", "Ꜳ")
        .replace("/", "₩")
        .replace("<", "ꜳ")
        .replace(">", "ꜵ")
        .replace(".", "Ꜷ")
    )
    return tagscript


def clean_seeds(seeds: str) -> dict:
    """
    Clean the seeds
    """
    cleaned_seed = {
        "args": tse.StringAdapter(seeds.get("args", "")),
        "user": tse.MemberAdapter(FakeMember(seeds.get("user"))),
        "target": tse.MemberAdapter(FakeMember(seeds.get("target"))),
        "channel": tse.ChannelAdapter(FakeChannel(seeds.get("channel"))),
    }
    return cleaned_seed


@app.route("/")
def main() -> None:
    """
    Main function to return "Status"
    """
    return {"Status": "Alive"}


@app.route("/v1/process/<string:tagscript>")
def v1_process(tagscript: str) -> None:
    """
    v1 Process
    """
    output = tsei.process(decode_tagscript(unquote(tagscript)) + r"{debug}")

    actions = {}

    for i, v in output.actions.items():
        if i == "embed":
            actions[i] = v.to_dict()
        else:
            actions[i] = v
    response = {
        "body": encode_tagscript(output.body),
        "actions": actions,
        "extras": output.extras,
    }
    return jsonify(response)


@app.route("/v2/process/", methods=["POST"])
def v2_process() -> None:
    """
    v2 Processor

    Uses get as post requires you to encode params and decode them, which is a pain.
    """
    uses = str(int(client.get("uses")) + 1)
    client.set("uses", uses)

    body = request.form
    seeds = clean_seeds(json.loads(decode_tagscript(body.get("seeds", ""))))
    output = tsei.process(
        decode_tagscript(body.get("tagscript", "")) + r"{debug}", seeds
    )

    actions = {}

    for action, value in output.actions.items():
        if action == "embed":
            actions[action] = value.to_dict()
        else:
            actions[action] = value

    response = {
        "body": encode_tagscript(output.body),
        "actions": actions,
        "extras": output.extras,
        "uses": uses
    }
    return jsonify(response)


def run() -> None:
    """
    Run the server
    """
    app.run(host="0.0.0.0", port=8080)

run()