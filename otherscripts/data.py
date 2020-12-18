"""
MIT License

Copyright (c) 2020 BobDotCom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import asyncio


class Data:
    filename = "data.json"
    with open(filename, "r") as data_file:
        server_data = json.load(data_file)

    @staticmethod
    async def auto_update_data():
        while True:
            # erase file and dump data
            with open(Data.filename, "w") as data_file:
                json.dump(Data.server_data, data_file)

            await asyncio.sleep(30)

    @staticmethod
    def create_new_data():
        data_entry = {
            "active": False,
            "users": [],
            "urls": [],
            "channels": [],
            "welcome_msg": "",
            "join_role": None,
            "pay_respects": False,
            "leave_msg": ""
        }
        return data_entry
