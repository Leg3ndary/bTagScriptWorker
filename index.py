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
import sys
import urllib
from random import randint
from threading import Thread
from urllib.parse import unquote

import bTagScript as tse
from flask import Flask, jsonify
from flask_cors import CORS

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


@app.route("/")
def main() -> None:
    """
    Main function to return "Status"
    """
    return {"Status": "Alive"}


@app.route("/v1/process/<string:tagscript>")
def v1_process(tagscript: str) -> None:
    """
    Main function to return "Status"
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

@app.route("/v2/process/<string:tagscript>")
def v2_process(tagscript: str) -> None:
    """
    Main function to return "Status"
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
        with urllib.request.urlopen("https://"):
            pass


Thread(target=run).start()

if sys.platform.lower() == "linux":
    Thread(target=asyncio.run(keep_alive())).start()
