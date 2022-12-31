import os
import math
import re
import json
import time
import asyncio
from humanfriendly import format_timespan
from helper_fns.helper import TimeFormatter
from pyrogram.errors.exceptions.flood_420 import FloodWait
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE, STDOUT
from helper_fns.helper import hrb, getbotuptime, Timer, timex, create_backgroud_task
from asyncio import sleep as assleep
from helper_fns.pbar import get_progress_bar_string

all_data = []
msg_data = ['Getting Logs']

async def update_message(working_dir, COMPRESSION_START_TIME, total_time, mode,message, position, pid, datam):
    txt = ''
    name = datam[0]
    opt = datam[1]
    remnx = datam[2]
    ptype = datam[3]
    while True:
            await assleep(5)
            with open(working_dir, 'r+') as file:
                                    text = file.read()
                                    frame = re.findall("frame=(\d+)", text)
                                    time_in_us=re.findall("out_time_ms=(\d+)", text)
                                    progress=re.findall("progress=(\w+)", text)
                                    speed=re.findall("speed=(\d+\.?\d*)", text)
                                    if len(frame):
                                        frame = int(frame[-1])
                                    else:
                                        frame = 1;
                                    if len(speed):
                                        speed = speed[-1]
                                    else:
                                        speed = 1;
                                    if len(time_in_us):
                                        time_in_us = time_in_us[-1]
                                    else:
                                        time_in_us = 1;
                                    if len(progress):
                                        if progress[-1] == "end":
                                            break
                                    execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME)*1000)
                                    elapsed_time = int(time_in_us)/1000000
                                    difference = math.floor( (total_time - elapsed_time) / float(speed) )
                                    ETA = "-"
                                    if difference > 0:
                                        ETA = TimeFormatter(difference*1000)
                                    perc = f"{elapsed_time * 100 / total_time:.1f}%"
                                    progress = get_progress_bar_string(elapsed_time, total_time)
                                    botupt = getbotuptime()
                                    pro_bar = f"{str(ptype)} ({opt})\n🎟️File: {name}\n🧶Remaining: {str(remnx)}\n🖼Position: {str(position)}\n♒Preset: `{mode}`\n🧭Duration: `{format_timespan(total_time)}`\n\n\n{progress}\n\n\n ┌ 𝙿𝚛𝚘𝚐𝚛𝚎𝚜𝚜:【 {perc} 】\n ├ 𝚂𝚙𝚎𝚎𝚍:【 {speed} 】\n └ 𝙿𝚛𝚘𝚌𝚎𝚜𝚜𝚎𝚍:【 {str(TimeFormatter(time_in_us))} 】\n\n⚙{str(msg_data[-1])}\n\n\n⏰️ ETA: `{ETA}`\n♥️Bot Uptime: {str(botupt)}"
                                    if txt!=pro_bar:
                                            txt=pro_bar
                                            try:
                                                await message.edit(text=pro_bar)
                                            except FloodWait as e:
                                                await asyncio.sleep(e.value)
                                            except Exception as e:
                                                print(e)
    return


async def vidmark(the_media, message, working_dir, watermark_path, output_vid, total_time, mode, position, size, datam):
    global all_data
    global msg_data
    all_data = []
    msg_data = ['Getting Logs']
    COMPRESSION_START_TIME = time.time()
    cmd = f"""ffmpeg -hide_banner -progress {working_dir} -i {the_media} -i {watermark_path} -filter_complex "[1][0]scale2ref=w='iw*{size}/100':h='ow/mdar'[wm][vid];[vid][wm]overlay={position}" -preset {mode} -codec:a copy {output_vid}"""
    print(cmd)
    process = await create_subprocess_shell(cmd, limit = 1024 * 128, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    pid = process.pid
    await assleep(2)
    task = await create_backgroud_task(update_message(working_dir, COMPRESSION_START_TIME, total_time, mode, message, position, pid, datam))
    while True:
            try:
                    async for line in process.stdout:
                                line = line.decode('utf-8').strip()
                                print(line)
                                all_data.append(line)
                                if len(line)<3800:
                                    msg_data[-1] = line
            except ValueError:
                    continue
            else:
                    break
    await process.communicate()
    try:
        task.cancel()
    except Exception as e:
        print(e)
    if os.path.lexists(output_vid):
        return [True, output_vid]
    else:
        return [False, all_data]


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    # width = "90"
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
