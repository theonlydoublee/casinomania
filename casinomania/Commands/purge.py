import lightbulb,datetime


purgePL = lightbulb.Plugin('purge')


# region PURGE COMMAND - Remove specified number of messages
@purgePL.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('count', 'The amount of messages to purge.', type=int, max_value=100, min_value=1)
@lightbulb.command('purge', 'Purges a defined amount of messages from the channel.', pass_options=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def purge(ctx:lightbulb.context, count:int) -> None:
    messages = (
        await ctx.app.rest.fetch_messages(ctx.channel_id)
        .take_until(lambda m: datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14) > m.created_at)
        .limit(count)
    )

    if messages:
        await ctx.app.rest.delete_messages(ctx.channel_id, messages)
        await ctx.respond(f"Purged {len(messages)} messages.")
    else:
        await ctx.respond("Could not find any messages younger than 14 days.")
# endregion


def load(bot: lightbulb.BotApp):
    bot.add_plugin(purgePL)


def unload(bot: lightbulb.BotApp):
    # bot.remove_command(bot.get_slash_command("purge"))
    bot.remove_plugin(purgePL)