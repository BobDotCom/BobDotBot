import aiosqlite

async def check(ctx):
    async with aiosqlite.connect("economy.db") as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT wallet FROM users WHERE userid = ?",(ctx.author.id,))
            rows = await cursor.fetchone()
            if not rows:
                if ctx.invoked_with == 'crime':
                    await ctx.send("Go to work and get some money before using this command please")
                elif ctx.invoked_with == 'help':
                    return True
                else:
                    await ctx.send('An error occurred, please notify my developer about this. Custom error code 600')
                return False
            else:
                if not rows[0] >= 5000:
                    if ctx.invoked_with == 'crime':
                        await ctx.send("You need to have at least 5000 to commit a crime, otherwise you might go bankrupt")
                    elif ctx.invoked_with == 'help':
                        return True
                    else:
                        await ctx.send('An error occurred, please notify my developer about this. Custom error code 600')
                    return False
                else:
                    return True