import os  
import discord  
from discord.ext import commands  
import random  
from datetime import datetime  
import pytz  
from apscheduler.schedulers.asyncio import AsyncIOScheduler  
from apscheduler.triggers.cron import CronTrigger  
from dotenv import load_dotenv  

# Load environment variables  
load_dotenv()  

# Bot configuration with all intents  
intents = discord.Intents.all()  # This line changed  
bot = commands.Bot(command_prefix='!', intents=intents)  

# Global variables  
USER_NAME = "Joey"  
USER_ID = int(os.getenv('USER_ID'))  # Your ID  
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Your channel ID  
tasks = []  
task_reminders = {}  

# Good morning wishes  
morning_wishes = [  
    f"Rise and shine, {USER_NAME}! 🌅 Hope your day is filled with awesome moments!",  
    f"Good morning {USER_NAME}! 🌞 May today bring you joy and success!",  
    f"Hey {USER_NAME}! 🌄 Wishing you a fantastic day ahead!",  
    f"Morning {USER_NAME}! 🌅 Let's make today amazing!",  
    f"Rise and grind, {USER_NAME}! 🌞 Today is going to be great!",  
]  

@bot.event  
async def on_ready():  
    print(f'{bot.user} has connected to Discord!')  
    
    # Initialize scheduler  
    scheduler = AsyncIOScheduler()  
    
    # Schedule good morning message (10:00 AM GMT+7)  
    tz = pytz.timezone('Asia/Bangkok')  
    scheduler.add_job(  
        send_morning_message,  
        CronTrigger(hour=10, minute=0, timezone=tz)  
    )  
    
    # Schedule task reminders  
    scheduler.add_job(  
        check_tasks,  
        'interval',  
        hours=1  
    )  
    
    scheduler.start()  

async def send_morning_message():  
    channel = bot.get_channel(CHANNEL_ID)  
    wish = random.choice(morning_wishes)  
    await channel.send(f"<@{USER_ID}> {wish}\nWhat are your plans for today?")  

async def check_tasks():  
    if not tasks:  
        return  
        
    channel = bot.get_channel(CHANNEL_ID)  
    current_time = datetime.now(pytz.timezone('Asia/Bangkok'))  
    
    for task in tasks:  
        if task not in task_reminders:  
            continue  
        
        last_reminder = task_reminders[task]  
        if (current_time - last_reminder).total_seconds() >= 3600:  # 1 hour  
            await channel.send(f"<@{USER_ID}> Have you completed this task yet?\n- {task}")  
            task_reminders[task] = current_time  

@bot.event  
async def on_message(message):  
    if message.author == bot.user:  
        return  

    if message.author.id != USER_ID:  
        return  

    content = message.content.lower()  
    
    # Handle task completion  
    if content == "done":  
        tasks.clear()  
        task_reminders.clear()  
        await message.channel.send(f"<@{USER_ID}> Great job completing your tasks! 🎉")  
        return  

    # Handle play-related messages  
    if "play" in content:  
        await message.channel.send(f"<@{USER_ID}> Have fun! 🎮 Remember to take breaks!")  
        return  

    # Handle task listing  
    if content.strip().startswith("-"):  
        task = content.strip()[1:].strip()  # Remove the "-" and extra spaces  
        if task:  
            tasks.append(task)  
            task_reminders[task] = datetime.now(pytz.timezone('Asia/Bangkok'))  
            await message.channel.send(f"<@{USER_ID}> Task added: {task}")  
            return  

    await bot.process_commands(message)  

# Command to show current tasks  
@bot.command(name='tasks')  
async def show_tasks(ctx):  
    if not tasks:  
        await ctx.send(f"<@{USER_ID}> You have no active tasks!")  
        return  
    
    task_list = "\n".join([f"- {task}" for task in tasks])  
    await ctx.send(f"<@{USER_ID}> Here are your current tasks:\n{task_list}")  

# Run the bot  
bot.run(os.getenv('DISCORD_TOKEN')) 