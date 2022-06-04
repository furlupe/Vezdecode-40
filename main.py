import asyncio

import discord, csv, datetime
from discord.ext import commands

config = {
    "token": "OTgyNTg1MjUzMDg2NTI3NTY4.G8e8oK.uN22tgjS6AElyMVUV9YWNFt6gnFgpmTXGhn_SY",
    "prefix": "prefix"
}

days = {
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "воскресенье": 6,
}

days_reverted = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "оскресенье"
}

bot = commands.Bot(command_prefix=config['prefix'])

pupils, end_of_lessons = dict(), dict()
groups = list()

with open("students.csv", "r", encoding="utf-8") as r_file:
    reader = csv.reader(r_file, delimiter=",")

    file = [row for row in reader]
    presented = {key: [] for key in file[0]}

    for i, pupil in enumerate(file[3]):
        for p in pupil.split(","):
            if p not in pupils.keys():
                pupils[p] = {}

            pupils[p][file[0][i]] = {
                "dates": file[1][i].split(" - "),
                "time": file[2][i].split(" - ")
            }

            end_of_lessons[file[0][i]] = {"dates": [days[d] for d in file[1][i].split(" - ")],
                                          "time": file[2][i].split(" - ")[1]}


async def make_log():
    await bot.wait_until_ready()

    now = datetime.datetime.now()
    schedules = {}
    for group in end_of_lessons:
        t = end_of_lessons[group]["time"].split(":")
        schedules[group] = datetime.datetime(now.year, now.month, now.day, int(t[0]), int(t[1]))

    while True:
        now = datetime.datetime.now()
        for group in end_of_lessons:
            if now.weekday() in end_of_lessons[group]["dates"] and len(presented):

                hour = end_of_lessons[group]["time"].split(":")
                minute = int(hour[1])
                hour = int(hour[0])

                if now >= schedules[group]:
                    with open("log.txt", "a") as f:
                        log = "{0}, {1}, {2}:{3}\n".format(group,
                                                           days_reverted[now.weekday()],
                                                           hour,
                                                           minute)
                        for pupil in presented[group]:
                            log += "\t{0}\n".format(pupil)
                        f.write(log)
                        schedules[group] += datetime.timedelta(days=1)

        await asyncio.sleep(20)

bot.loop.create_task(make_log())
@bot.event
async def on_voice_state_update(member: discord.member, before, after):
    if after.channel is not None:
        name = "{0}#{1}".format(member.name, member.discriminator)
        group = after.channel.name

        if name not in pupils.keys() or group not in pupils[name].keys():
            return

        interval = pupils[name][group]["time"]
        days_of_lesson = [days[d] for d in pupils[name][group]["dates"]]

        left = list(map(int, interval[0].split(":")))
        right = list(map(int, interval[1].split(":")))

        now = datetime.datetime.now()
        left = datetime.datetime(now.year, now.month, now.day, left[0], left[1])
        right = datetime.datetime(now.year, now.month, now.day, right[0], right[1])

        if left <= now <= right:
            right_day = (now.weekday() in days_of_lesson)

            if not right_day:
                return

            if name not in presented[group]:
                presented[group].append(name)

bot.run(config['token'])
