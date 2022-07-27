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

import asyncio
from datetime import datetime
import sys
import urllib
from random import randint
from threading import Thread
from urllib.parse import unquote

import bTagScript as tse
from flask import Flask, jsonify, request
from flask_cors import CORS

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
        self.created_at = user.get("user")
        self.id = user.get("id", "") # pylint: disable=C0103
        self.timestamp = datetime.now()
        self.color = user.get("color", "")
        self.display_name = user.get("name", "")
        self.display_avatar = FakeAvatar()
        self.display_avatar.url = user.get("avatar", "")
        self.discriminator = user.get("discriminator", "0001")
        self.joined_at = datetime.fromtimestamp(user.get("joined_at", "0"))
        self.mention = user.get("mention", "")
        self.bot = False

        '''
        {
            "bot": self.object.bot,
            "top_role": getattr(self.object, "top_role", ""),
            "boost": getattr(self.object, "premium_since", ""),
            "timed_out": getattr(self.object, "timed_out_until", ""),
            "banner": self.object.banner.url if self.object.banner else "",
        }'''


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
]
tsei = tse.interpreter.Interpreter(blocks=tse_blocks)

app = Flask("bTagScriptWorker")
CORS(app)

def clean_tagscript(tagscript: str) -> str:
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
        "user": tse.MemberAdapter(FakeMember(seeds.get("user"))),
        "target": tse.MemberAdapter(FakeMember(seeds.get("target"))),
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
    output = tsei.process(clean_tagscript(unquote(tagscript)) + r"{debug}")

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

@app.route("/v2/process/", methods=["GET"])
def v2_process() -> None:
    """
    v2 Processor

    Uses get as post requires you to encode params and decode them, which is a pain.
    """
    headers = request.headers
    #seeds = clean_seeds(clean_tagscript(headers.get("seeds", "")))
    seeds = {}
    output = tsei.process(headers.get("tagscript", "") + r"{debug}", seeds)

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
    }
    return jsonify(response)


def run() -> None:
    """
    Run the server
    """
    app.run(host="0.0.0.0", port=8080)


async def keep_alive() -> None:
    """
    Keep the server alive
    """
    while True:
        await asyncio.sleep(randint(50, 100))
        with urllib.request.urlopen("https://btp.leg3ndary.repl.co"):
            pass


Thread(target=run).start()

if sys.platform.lower() == "linux":
    Thread(target=asyncio.run(keep_alive())).start()
