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

import discord, humanize, datetime

class VerifyMember:
    def __init__(self, bot, payload, data, **kwargs):
        self.bot = bot
        self.payload = payload
        self.data = data
        self.points = 0
        self.failed = None
        self.result = None
        self.moderator_approval = False
        self.needs_captcha = False
        self.join_time = datetime.datetime.utcnow() - payload.member.joined_at
        self.creation_time = datetime.datetime.utcnow() - payload.member.created_at
        self.embed = discord.Embed(title='Member Verification',timestamp=datetime.datetime.utcnow())
        self.embed.set_author(name=payload.member,icon_url=payload.member.avatar_url)
        self.required_time = datetime.timedelta(seconds=data[2])
        if self.join_time < self.required_time:
            self.failed = f'Member has not been in the server for long enough. \n**Required time:** {humanize.precisedelta(self.required_time)} \n**Current time:** {humanize.precisedelta(self.join_time)}'
            self.embed = None
            return
        if self.creation_time < datetime.timedelta(weeks=1):
            self.points += 1
            if self.creation_time < datetime.timedelta(days=1):
                self.points += 2
                if self.creation_time < datetime.timedelta(hours=1):
                    self.points += 6
                    self.embed.add_field(name='\U0000274c Account is newer than 1 hour (+8)', value=humanize.precisedelta(self.creation_time))
                else:
                    self.embed.add_field(name='\U0000274c Account is newer than 1 day (+3)', value=humanize.precisedelta(self.creation_time))
            else:
                self.embed.add_field(name='\U0000274c Account is newer than 1 week (+1)', value=humanize.precisedelta(self.creation_time))
        else:
            self.embed.add_field(name='\U00002705 Account is older than 1 week', value=humanize.precisedelta(self.creation_time))
        if not payload.member.avatar:
            self.points += 1
            self.embed.add_field(name='\U0000274c Account has no avatar (+1)', value='No avatar')
        else:
            self.embed.add_field(name='\U00002705 Account has an avatar', value=payload.member.avatar_url)
        guild = self.bot.get_guild(payload.guild_id)
        all_names = [member.name for member in guild.members]
        if all_names.count(payload.member.name) > 1:
            self.points += 3
            self.embed.add_field(name="\U0000274c Member's name may be impersonating (+3)", value=payload.member.name)
        else:
            self.embed.add_field(name='\U00002705 Member is not impersonating', value=payload.member.name)

        if self.points > 5:
            self.failed = f'Points above 5 ({self.points}), requires moderator approval'
        elif self.points > 2:
            if data[3] > 0:
                self.failed = f'Points above 2 ({self.points}), requires captcha'
                self.needs_captcha = True
            else:
                self.failed = f'Points above 2 ({self.points}), captcha disabled, requires manual approval'
                self.moderator_approval = True
        else:
            if data[3] == 2:
                self.failed = f'Passed checks with less than 2 points, captcha needed (points: {self.points})'
                self.needs_captcha = True
            else:
                self.result = f'Passed checks with less than 2 points (points: {self.points})'

        override = kwargs.get('override')
        if override or self.moderator_approval:
            self.override = f'~~{self.failed or self.result}~~ \n{override or "Pending Manual Approval"}'
            self.failed = kwargs.get('failed') if not kwargs.get('failed') is None else self.failed
            self.result = kwargs.get('result') if not kwargs.get('result') is None else self.result
        else:
            self.override = False

        if self.failed or self.moderator_approval:
            self.embed.color = discord.Color.red()
        else:
            self.embed.color = discord.Color.green()
        self.embed.add_field(name="Final result",value=self.override or self.failed or self.result)