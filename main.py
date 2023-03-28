import os
import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text
from discord import Interaction
from discord.ext.commands import is_owner, Context

from events import pro_groups


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix="!")


# if slash command isn't in a cog
@client.tree.command(
    description="Shows the server rules"
)  # removed the name param because it will raise an error as it is the same that the async function
async def rules(interaction: discord.Interaction) -> None:
    rules = (
        "1. Don't say bad words",
        "2. Respect other people",
        "3. You mustn't speak loud in voice channels",
    )
    await interaction.response.send_message(f"{rules}")


@client.tree.command(
    description="Get the member counts for all basic and pro groups"
)  # removed the name param because it will raise an error as it is the same that the async function
async def rules(interaction: discord.Interaction) -> None:
    rules = (
        "1. Don't say bad words",
        "2. Respect other people",
        "3. You mustn't speak loud in voice channels",
    )
    await interaction.response.send_message(f"{rules}")


@client.command()
@is_owner()
async def sync(ctx: Context) -> None:
    synced = await client.tree.sync()
    await ctx.reply("{} commands synced".format(len(synced)))


@client.command()
@is_owner()
async def member_counts(ctx):
    basicgroups = [
        f"{r.name}: {len(r.members)}"
        for r in ctx.guild.roles
        if r.name.startswith("basic-group")
    ]
    progroups = [
        f"{r.name}: {len(r.members)}"
        for r in ctx.guild.roles
        if r.name.startswith("pro-group")
    ]
    privategroups = [
        f"{r.name}: {len(r.members)}"
        for r in ctx.guild.roles
        if r.name.startswith("private")
    ]
    await ctx.reply(
        "Basic Members:\n"
        + "\n-".join(basicgroups)
        + "\n------------------"
        + "Pro Members:\n"
        + "\n-".join(progroups)
        + "\n------------------"
        + "Private Members:\n"
        + "\n-".join(privategroups)
    )


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_member_update(before, after):
    await pro_groups.handle_pro_role_change(before, after)


client.run(os.environ["DISCORD_TOKEN"])


#### API ####

app = FastAPI()

# MySQL database configuration
user = os.getenv("MYSQLUSER")
password = os.getenv("MYSQLPASSWORD")
host = os.getenv("MYSQLHOST")
port = os.getenv("MYSQLPORT")
dbname = os.getenv("MYSQLDATABASE")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WebhookData(Base):
    __tablename__ = "whop_data"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Text)


Base.metadata.create_all(bind=engine)


# Define Pydantic model for webhook data
class Webhook(BaseModel):
    data: str


# Define FastAPI route to receive webhook requests
@app.post("/whopWebhook")
async def receive_webhook(webhook: Webhook):
    try:
        # Create new database session
        db = SessionLocal()

        # Create new webhook data object and store it in the database
        new_webhook = WebhookData(data=webhook.data)
        db.add(new_webhook)
        db.commit()
        db.refresh(new_webhook)

        # Close database session
        db.close()

        # Return success response
        return {"message": "Webhook data stored successfully!"}
    except Exception as e:
        # Rollback database changes and return error response
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sendEmbed")
async def sendEmbed(request: Request):
    body = await request.json()
    channel = client.get_channel(body["channel"])
    embed = discord.Embed(
        title=body["title"],
        description=body["description"],
        color=discord.Color.blue(),
    )
    embed.add_field(name="ASIN", value=body["asin"], inline=True)
    embed.add_field(name="ROI", value=body["roi"], inline=True)
    embed.add_field(name="category", value=body["category"], inline=True)
    embed.add_field(name="price", value=body["price"], inline=True)
    embed.add_field(name="discount codes", value=body["discount codes"], inline=True)
    embed.set_thumbnail(url="https://i.imgur.com/axLm3p6.jpeg")
    embed.set_footer(text="LeadBot by UpSource Labs")
    await channel.send(embed=embed)
    return {"status": "ok"}
