import asyncio
import os
import discord
import pandas as pd
import math
import winsound
from discord import app_commands
from dotenv import load_dotenv
path = "G:/GitHub-Repos/Stockbot_PY/src/"
base_balance = 1000
base_Oil = 0
message = "DEFAULT"

load_dotenv()

guild_id = os.environ.get("DISCORD_GUILD_ID")


# Always handle UserID's as strings


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False  # we use this so the bot doesn't sync commands more than once

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            # guild specific: leave blank if global (global registration can take 1-24 hours)
            await tree.sync(guild=discord.Object(id=guild_id))
            self.synced = True
        winsound.Beep(750, 150)
        print(f"I am {self.user}.")
        await production()


client = aclient()
tree = app_commands.CommandTree(client)

# * Command Functions


def checkIfUserIsAdmin(uid):
    df = pd.read_csv(path + "data/admins.csv")
    uid = int(uid)
    for v, i in enumerate(df["uid"]):
        print(i, uid)
        if i == uid:
            return {1: df["auth_level"][v], 2: df["name"][v]}


def recalculatePrice(resource):
    price = pd.read_csv(path + "data/prices.csv")
    max_price = price[resource][3]
    price[resource][0] = math.floor(
        max_price*(price[resource][2]+1) ** (-0.245))
    price.to_csv(path + "data/prices.csv", index=False)
    return price[resource][0]


async def production():
    while True:
        price = pd.read_csv(path + "data/prices.csv")
        for i in price.columns:
            # TODO: If available resources are greater than 80% of max, then stop production
            production = price[i][0]*price[i][0]/500
            price[i][2] = int(int(price[i][2]) + production)
            recalculatePrice(i)
            print(
                f"+{math.floor(production)} {i} produced, price is now at {price[i][0]}₭")
        price.to_csv(path + "data/prices.csv", index=False)
        await asyncio.sleep(3600)

# * Slash commands
# TODO: /daily


@tree.command(guild=discord.Object(id=guild_id), name='joe', description='mama')
async def slash2(interaction: discord.Interaction):
    await interaction.response.send_message("Joe Mama!")


@tree.command(guild=discord.Object(id=guild_id), name='promote', description='OWNER ONLY')
async def promote(interaction: discord.Interaction, user: discord.User, authorization_level: str):
    authorization_level = authorization_level.lower()
    if authorization_level == "owner" or authorization_level == "admin":
        if int(interaction.user.id) == int(os.environ.get("OWNER_ID")):
            df = pd.read_csv(path + "data/admins.csv")
            for v, i in enumerate(df["uid"]):
                if i == user.id:
                    if df["auth_level"][v] == "owner":
                        message = f"<@{user.id}> is already {authorization_level}!"
                        break
                    elif df["auth_level"][v] != "admin":
                        df["auth_level"][v] = authorization_level
                        df.to_csv(path + "data/admins.csv", index=False)
                        message = f"<@{user.id}> has been promoted to {authorization_level}!"
                        break
            else:
                df = pd.concat([df, pd.DataFrame(
                    {"name": [user.name], "uid": [user.id], "auth_level": [authorization_level]})])
                df.to_csv(path + "data/admins.csv", index=False)
                message = f"<@{user.id}> has been promoted to {authorization_level}!"
        else:
            message = "You do not have permission to use this command."
    else:
        message = "Invalid authorization level. Use `owner` or `admin`."

    print(f"{interaction.user.name} tried to promote {user.name} to {authorization_level}\nAnswer: {message}")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name='demote', description='OWNER ONLY')
async def demote(interaction: discord.Interaction, user: discord.User):
    if int(interaction.user.id) == int(os.environ.get("OWNER_ID")):
        df = pd.read_csv(path + "data/admins.csv")
        for v, i in enumerate(df["uid"]):
            if i == user.id:
                df = df.drop(v)
                df.to_csv(path + "data/admins.csv", index=False)
                message = f"<@{user.id}> has been demoted!"
                break
        else:
            message = f"<@{user.id}> does not have elevated priviliges!"
    else:
        message = "You do not have permission to use this command."

    print(f"{interaction.user.name} tried to demote {user.name}\nAnswer: {message}")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name='isadmin', description="Check if a user is an admin")
async def isadmin(interaction: discord.Interaction, user: discord.User):
    df = pd.read_csv(path + "data/admins.csv")
    for v, i in enumerate(df["uid"]):
        if i == user.id:
            message = f"<@{user.id}> is an {df['auth_level'][v]}!"
            break
    else:
        message = f"<@{user.id}> is not an admin!"

    print(f"{interaction.user.name} checked if {user.name} is an admin\nAnswer: {message}")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="init", description="init your account")
async def init(interaction: discord.Interaction):
    username = interaction.user.name
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    user_id = interaction.user.id
    df = pd.read_csv(path+"data/accounts.csv")
    for v, i in enumerate(df["UserID"]):
        if i == user_id:
            message = f'<@{user_id}> You already have an account!'
            if df["Username"][v] != username:
                old_username = df["Username"][v]
                df["Username"][v] = username
                df.to_csv(path+"data/accounts.csv", index=None, header=True)
                message = 'Your username has been updated!'
                print(old_username, "'s username has been updated to", username + ".")
            break
    else:
        df = pd.concat(
            [df, pd.DataFrame({"Username": [username], "UserID": [user_id], "Balance": [base_balance]})])
        df.fillna(0, inplace=True, downcast="infer")
        df.to_csv(path+"data/accounts.csv", encoding='utf-8', index=False)
        df = pd.read_csv(path+"data/inventories.csv")
        df = pd.concat(
            [df, pd.DataFrame({"username": [username], "uid": [user_id]})])
        df = df.fillna(0, downcast='infer', inplace=False)
        df.to_csv(path+"data/inventories.csv", index=False)

        message = f'**<@{user_id}>**, You\'ve successfully created an account! \n You have **{base_balance}₭**'
        print("User", username, "created an account.")
    print(f"@{console_username} Tried to create an account.\nAnswer: {message}\n")
    await interaction.response.send_message(message, ephemeral=True)


@tree.command(guild=discord.Object(id=guild_id), name="bal", description="Displays your balance.")
async def bal(interaction: discord.Interaction, user: discord.User = None):
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    if user is None:
        user = interaction.user
    user_cu = user.name + "#" + user.discriminator
    df = pd.read_csv(path+"data/accounts.csv")
    for v, i in enumerate(df["UserID"]):
        if i == user.id:
            message = f'<@{user.id}> has **{df["Balance"][v]:,}₭**!'
            break
    else:
        message = f'<@{user.id}> Does not have an account! Use `/init` to create one.'

    print(f"{console_username} tried to check the balance of {user_cu}\nAnswer: {message}")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="baltop", description="Displays the top 10 richest users.")
async def baltop(interaction: discord.Interaction):
    df = pd.read_csv(path+"data/accounts.csv")
    df = df.sort_values(by="Balance", ascending=False)
    df = df.reset_index(drop=True)
    message = "```"
    for i in range(10):
        if i < len(df):
            message += f"{i+1}. {df['Username'][i]}: {df['Balance'][i]:,}₭\n"
    message += "```"
    print(f"{interaction.user.name} checked the baltop.\nAnswer: \n{message}")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="price", description="Displays the price of a stock.")
async def price(interaction: discord.Interaction, stockname: str):
    stockname = stockname.lower()
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    df = pd.read_csv(path+"data/prices.csv", header=None)
    found = False
    for v, i in enumerate(df):
        if stockname == df[v][0]:
            price = df[v][1]
            found = True
            message = f'The price of `{stockname}` is **{price}₭**!'
            break
    if found == False:
        message = f'<@{interaction.user.id}>, Can\'t find this stock.'

    print(
        f"@{console_username} requested the price of {stockname}.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="buy", description="Buy some shares")
async def buy(interaction: discord.Interaction, name: str, amount: int):
    name = name.lower()
    amount = int(amount)
    stocks = pd.read_csv(path+"data/prices.csv")
    accounts = pd.read_csv(path+"data/accounts.csv")
    inventories = pd.read_csv(path+"data/inventories.csv")
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    user_id = interaction.user.id
    for v, i in enumerate(stocks):
        if name == i:
            price = stocks[i][0]
            for w, i in enumerate(accounts["UserID"]):
                if user_id == i:
                    balance = accounts["Balance"][w]
                    if balance < price * amount:
                        message = f'<@{user_id}>, You don\'t have enough money to buy this stock!'
                    else:
                        for v, i in enumerate(inventories["uid"]):
                            if user_id == i:
                                if stocks[name][2] <= amount:
                                    message = f'<@{user_id}>, There is not enough {name}!'
                                else:
                                    stocks[name][2] -= amount
                                    stocks.to_csv(
                                        path+"data/prices.csv", index=False)
                                    recalculatePrice(name)
                                    inventories[name][v] += amount
                                    inventories.to_csv(
                                        path+"data/inventories.csv", index=False)
                                    accounts["Balance"][w] -= price * amount
                                    accounts.to_csv(
                                        path+"data/accounts.csv", index=False)
                                    message = f'<@{user_id}>, You have successfully bought **{amount:,}** **{name}** for **{price * amount:,}₭**!'
                                    break
                    break
            else:
                message = f'<@{user_id}>, You don\'t have an account!\nCreate an account by typing `/init`!'
            break
    else:
        message = f'<@{user_id}>, Can\'t find this stock.'
    print(f"@{console_username} tried to buy {amount} {name}.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="sell", description="Sell some shares")
async def sell(interaction: discord.Interaction, name: str, amount: int):
    name = name.lower()
    stocks = pd.read_csv(path+"data/prices.csv")
    accounts = pd.read_csv(path+"data/accounts.csv")
    inventories = pd.read_csv(path+"data/inventories.csv")
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    user_id = interaction.user.id
    for v, i in enumerate(stocks):
        if name == i:
            for v2, i2 in enumerate(accounts["UserID"]):
                if user_id == i2:
                    for v3, i3 in enumerate(inventories["uid"]):
                        if user_id == i3:
                            if inventories[name][v3] < amount:
                                message = f'<@{user_id}>, You don\'t have enough {name} you can sell!'
                            else:
                                price = stocks[name][0]
                                inventories[name][v3] -= amount
                                inventories.to_csv(
                                    path+"data/inventories.csv", index=False)
                                stocks[name][2] += amount
                                stocks.to_csv(
                                    path+"data/prices.csv", index=False)
                                recalculatePrice(name)
                                accounts["Balance"][v2] += int(
                                    price * amount * 0.99)
                                accounts.to_csv(
                                    path+"data/accounts.csv", index=False)
                                message = f'<@{user_id}>, You have successfully sold **{amount:,}** **{name}** for **{price * amount:,}₭**!'
                                break
                    break
            else:
                message = f'<@{user_id}>, You don\'t have an account!\nCreate an account by typing `/init`!'
            break

    else:
        message = f'<@{user_id}>, Can\'t find {name}.'

    print(f"@{console_username} tried to sell some shares.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="inv", description="Displays your inventory.")
async def inv(interaction: discord.Interaction):
    accounts = pd.read_csv(path+"data/accounts.csv")
    username = interaction.user.name
    user_id = interaction.user.id
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    found = False

    for v, i in enumerate(accounts["UserID"]):
        if i == user_id:
            bal = accounts["Balance"][v]
            oil = accounts["oil"][v]
            iron = accounts["iron"][v]
            copper = accounts["copper"][v]
            message = f'**{bal} ₭**\n**{oil} Oil**\n**{iron} Iron**\n**{copper} Copper**'
            break
    else:
        message = f'<@{user_id}> Use `/init` first to create an account!'

    print(f"@{console_username} requested his inventory.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="pay", description="Pay someone some money.")
async def pay(interaction: discord.Interaction, user: discord.User, amount: int):
    accounts = pd.read_csv(path+"data/accounts.csv")
    user_id = interaction.user.id
    console_username = interaction.user.name + "#" + interaction.user.discriminator
    user_cu = user.name + "#" + user.discriminator

    for v, i in enumerate(accounts["UserID"]):
        if i == user_id:
            for w, j in enumerate(accounts["UserID"]):
                if j == user.id:
                    if accounts["Balance"][v] < amount:
                        message = f'<@{user_id}>, You don\'t have enough money to pay this amount!'
                        break
                    else:
                        accounts["Balance"][v] -= amount
                        accounts["Balance"][w] += amount
                        accounts.to_csv(path+"data/accounts.csv", index=False)
                        message = f'<@{user_id}>, You have successfully paid **{amount:,}₭** to <@{user.id}>!'
                        break
            break
    else:
        message = f'<@{user_id}> Use `/init` first to create an account!'
    print(f"{console_username} tried to pay {user_cu}.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="company", description="Create a company. or manage it.")
async def company(interaction: discord.Interaction, action: str = "info", name: str = ""):
    companies = pd.read_csv(path+"data/companies.csv")
    # TODO: decode/encode production
    # TODO: Calculate networth
    if action == "info":   # Get info about a company
        if name == "":
            for v, i in enumerate(companies["ownerid"]):
                if str(i) == str(interaction.user.id):
                    name = companies["name"][v]
                    break
            else:
                message = f'<@{interaction.user.id}>, You don\'t have a company!\nCreate one by typing `/company create <name>`'

        for v, i in enumerate(companies["name"]):
            if i == name:
                employees = companies["employees"][v].split(";")
                for v2, i2 in enumerate(employees):
                    employees[v2] = f"<@{i2}>"
                employees = ", ".join(employees)
                message = f'**{name}**\nCEO: **{companies["owner"][v]}**\nNetworth: **₭**\nProduction: **CUMING SOON**\nEmployees: **{employees}**'
                break
        else:
            message = f'<@{interaction.user.id}>, Can\'t find this company.'

    elif action == "create":   # Create a company
        for v, i in enumerate(companies["name"]):
            if i == name:
                message = f'<@{interaction.user.id}>, This company already exists!'
                break
        else:
            companies = pd.concat([companies, pd.DataFrame({"name": [name], "owner": [
                                  interaction.user.name], "ownerid": [interaction.user.id]})])
            companies.fillna("None", inplace=True, downcast="infer")
            companies.to_csv(path+"data/companies.csv", index=False)
            message = f'<@{interaction.user.id}>, You have successfully created a company called **{name}**!'

    elif action == "hire":   # Hire an employee from the applicant list of the company
        name = name.replace("<", "").replace(">", "").replace("@", "")
        for v, i in enumerate(companies["name"]):
            if i == name:
                if companies["ownerid"][v] == interaction.user.id:
                    applicants = companies["applicants"][v].split(";")
                    for v2, i2 in enumerate(applicants):
                        if i2 == str(name):
                            applicants.pop(v2)
                            employees = companies["employees"][v].split(";")
                            employees.append(str(interaction.user.id))
                            companies["employees"][v] = ";".join(employees)
                            companies["applicants"][v] = ";".join(applicants)
                            companies.to_csv(
                                path+"data/companies.csv", index=False)
                            message = f'<@{interaction.user.id}>, You have successfully been hired by **{name}**!'
                            break
                    else:
                        message = f'<@{interaction.user.id}>, This user is not an applicant!'
                        break
                    break
                else:
                    message = f'<@{interaction.user.id}>, You are not the owner of this company!'
                    break
        else:
            message = f'<@{interaction.user.id}>, Can\'t find this company.'

    elif action == "fire":   # Fire an employee
        name = name.replace("@", "").replace("<", "").replace(">", "")
        for v, i in enumerate(companies["ownerid"]):
            if i == interaction.user.id:
                employees = str(companies["employees"][v]).split(";")
                for w, j in enumerate(employees):
                    if str(j) == name:
                        employees.pop(w)
                        companies["employees"][v] = ";".join(employees)
                        companies.to_csv(
                            path+"data/companies.csv", index=False)
                        message = f'<@{interaction.user.id}>, You have successfully fired <@{name}>!'
                        break
                else:
                    message = f'<@{interaction.user.id}>, This user is not an employee!'
                break
            else:
                message = f'<@{interaction.user.id}>, You don\'t own a company!'

    elif action == "apply":   # Apply for a job
        for v, i in enumerate(companies["name"]):
            if i == name:
                # add the userid to the applicants list of the company
                applicants = str(companies["applicants"][v]).split(";")
                for w, j in enumerate(applicants):
                    if str(j) == str(interaction.user.id):
                        message = f'<@{interaction.user.id}>, You already applied for this job!'
                        break
                else:
                    if companies["applicants"][v] == "None":
                        companies["applicants"][v] = str(interaction.user.id)
                    else:
                        companies["applicants"][v] = str(companies["applicants"][v]) + \
                            ";" + str(interaction.user.id)
                    companies.to_csv(
                        path+"data/companies.csv", index=False)
                    message = f'<@{interaction.user.id}>, You have successfully applied for a job at **{name}**!\nPlease wait for the CEO to accept you, via the /company hire @{interaction.user.name} command.'

    else:
        message = f'<@{interaction.user.id}>, Invalid action!'

    print(f"@{interaction.user.name}#{interaction.user.discriminator} tried to manage a company.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="addresource", description="ADMIN_ONLY - Add a resource.")
async def addresource(interaction: discord.Interaction, resource: str, starting_price: int, amount: int, max_price: int):
    if checkIfUserIsAdmin(interaction.user.id)[1] == "owner" or checkIfUserIsAdmin(interaction.user.id)[1] == "admin":
        console_username = interaction.user.name + "#" + interaction.user.discriminator
        resource = resource.lower()
        stocks = pd.read_csv(path+"data/prices.csv")
        inventories = pd.read_csv(path+"data/inventories.csv")
        for v, i in enumerate(stocks):
            if resource == i:
                message = f'<@{interaction.user.id}>, This resource already exists!'
                break
        else:
            stocks[resource] = [starting_price, amount, amount, max_price]
            stocks.to_csv(path+"data/prices.csv", index=False)
            inventories[resource] = 0
            inventories.fillna(0, inplace=True, downcast="infer")
            inventories.to_csv(path+"data/inventories.csv", index=False)
            recalculatePrice(resource)
            message = f'<@{interaction.user.id}>, You have successfully added **{resource}** to the market!'
    else:
        message = "You are not allowed to use this command."
    print(f"{console_username} tried to add a resource.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="removeresource", description="ADMIN_ONLY - Remove a resource.")
async def removeresource(interaction: discord.Interaction, resource: str):
    if checkIfUserIsAdmin(interaction.user.id)[1] == "owner" or checkIfUserIsAdmin(interaction.user.id)[1] == "admin":
        inventories = pd.read_csv(path+"data/inventories.csv")
        prices = pd.read_csv(path+"data/prices.csv")
        accounts = pd.read_csv(path+"data/accounts.csv")
        resource = resource.lower()
        user_id = interaction.user.id
        console_username = interaction.user.name + "#" + interaction.user.discriminator
        payouts = {}
        for v, i in enumerate(prices):
            if resource == i:
                for w, j in enumerate(inventories["uid"]):
                    if inventories[resource][w] > 0:
                        for x, k in enumerate(accounts["UserID"]):
                            if k == j:
                                accounts["Balance"][x] += int(prices[resource][0] *
                                                              inventories[resource][w] * 0.9)
                                payouts[j] = int(prices[resource][0] *
                                                 inventories[resource][w] * 0.9)
                                accounts.to_csv(
                                    path+"data/accounts.csv", index=False)
                                break
                del prices[resource]
                del inventories[resource]
                prices.to_csv(path+"data/prices.csv", index=False)
                inventories.to_csv(path+"data/inventories.csv", index=False)
                message = f'<@{user_id}>, You have successfully removed `{resource}`!\n\n'
                for key, value in payouts.items():
                    message += f'<@{key}> has been paid **{value}₭**!\n'
                break
        else:
            message = f'<@{user_id}>, This resource doesn\'t exist!'
    else:
        message = "You are not allowed to use this command."
    print(f"{console_username} tried to remove a resource.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


@tree.command(guild=discord.Object(id=guild_id), name="editaccount", description="ADMIN_ONLY - Edit an account.")
async def editaccount(interaction: discord.Interaction, user: discord.User, subject: str, amount: int) -> None:
    if checkIfUserIsAdmin(interaction.user.id)[1] == "owner" or checkIfUserIsAdmin(interaction.user.id)[1] == "admin":
        accounts = pd.read_csv(path+"data/accounts.csv")
        console_username = interaction.user.name + "#" + interaction.user.discriminator
        if subject != "Balance":
            subject = subject.lower()
        # check if the subject exists
        for v, i in enumerate(accounts):
            if subject == i:
                for w, j in enumerate(accounts["UserID"]):
                    if j == user.id:
                        accounts[subject][w] = amount
                        accounts.to_csv(path+"data/accounts.csv", index=False)
                        message = f'<@{interaction.user.id}>, You have successfully edited the account of <@{user.id}>!'
                        break
                else:
                    message = f'<@{interaction.user.id}>, This user doesn\'t have an account!'
                break
        else:
            message = f'<@{interaction.user.id}>, This subject doesn\'t exist!'

    print(f"{console_username} tried to edit an account.\nAnswer: {message}\n")
    await interaction.response.send_message(message)


client.run(os.environ.get("DISCORD_TOKEN"))
