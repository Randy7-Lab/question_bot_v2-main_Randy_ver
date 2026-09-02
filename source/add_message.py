import discord 
import asyncio 
import os
import re
from datetime import datetime, timedelta
from source import config

user_command_time = {}
close_user_m = {}

def clean_channel_name(category: str, user_nick: str) -> str:
    name = f"{category}-{user_nick}" if category else user_nick
    name = re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "-").lower()
    return name[:95]

async def go_message(client, message, category=None, is_pending=False):
    ######################################## 문의봇 명령어 확인 부분 ########################################
    if message.content.startswith("#문의봇명령어"):
        embed = discord.Embed(title='문의봇 명령어 안내', color=0x50bcdf, timestamp=message.created_at)
        embed.add_field(name="문의종료 방법", value='```!문의종료``` 또는 ```/문의종료```', inline=False)
        embed.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.display_avatar.url)
        await message.channel.send(embed=embed)
    ############################################ 문의 종료 부분 ############################################
    elif message.content.startswith("!문의종료"):
        channel = config.check_user_m2(message.channel.id, "")
        if not channel:
            await message.channel.purge(limit=1)
            a = await message.channel.send(embed=discord.Embed(title="ERROR", description="😅 이곳은 문의하는 채널이 아닙니다\n\n해당 메시지는 5초 뒤 삭제됩니다", color=0xff0000))
            await asyncio.sleep(5)
            await a.delete()
        else:
            close_user_m[channel] = 1
            await message.channel.send("3초 뒤 해당 유저의 문의가 종료됩니다")
            await asyncio.sleep(3)
            await message.channel.delete()
            config.delete_user(message.channel.id)
            file = discord.File(f"log/{channel}.txt")
            user = client.get_user(int(channel))
            log_channel = client.get_channel(int(config.config("log_channel")))
            embed = discord.Embed(
                title="Randy's 채널 고객센터", 
                description=f"{user.name}님 문의가 종료되었습니다 \n\n> 다시 문의하고 싶으신 경우에만 문의 버튼을 눌러 다시 문의 바랍니다.\n\n > 앞으로 더욱 나아가는 Randy's 채널이 되겠습니다 :)", 
                color=0x2da4d8, 
                timestamp=message.created_at
            )
            embed.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.display_avatar.url)
            await user.send(embed=embed)
            now = datetime.now()
            embed = discord.Embed(title='{}'.format(now.strftime("%Y - %m - %d")), color=0x2da4d8, timestamp=message.created_at)
            embed.add_field(name="문의 종료 로그", value=f"문의한 유저 : <@{channel}>\n\n문의 종료 담당자 : <@{message.author.id}>", inline=True)
            embed.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.display_avatar.url)
            await log_channel.send(embed=embed)
            log = await log_channel.send(file=file)
            os.remove(f"log/{channel}.txt")
            config.check_count(channel)
            close_user_m[channel] = 0
    ############################################ 문의 답변 부분 ############################################
    else:
        user_id = config.check_user_m2(message.channel.id, "")
        if user_id:
            try:
                user = client.get_user(int(user_id))
                if user is None:
                    return await message.channel.send(embed=discord.Embed(title="ERROR", description="문의를 답변하던 중 알 수 없는 에러가 발생했습니다\n\n> ERROR CODE : 0002(NONE TYPE USER)", color=0xff0000))
            except Exception as e:
                return await message.channel.send(embed=discord.Embed(title="ERROR", description=f"문의를 답변하던 중 알 수 없는 에러가 발생했습니다\n\n> ERROR CODE : 0003({e})", color=0xff0000))
            if message.attachments:
                await message.add_reaction('❄️')
                await user.send(embed=discord.Embed(title="문의 답변", description=f"Randy's 채널 고객센터 : {message.content}", color=0x2da4d8))
                await user.send(message.attachments[0].url)
                open(f"log/{user.id}.txt", 'a', encoding='utf-8 sig').write(f"Randy's 채널 고객센터({message.author.name}) : {message.content} , {message.attachments[0].url}\n")
            else:
                await message.add_reaction('❄️')
                await user.send(embed=discord.Embed(title="문의 답변", description=f"Randy's 채널 고객센터 : {message.content}", color=0x2da4d8))
                open(f"log/{user.id}.txt", 'a', encoding='utf-8 sig').write(f"Randy's 채널 고객센터({message.author.name}) : {message.content}\n")

    ######################################## 문의 or 첫 문의 부분 #########################################
    if message.guild is None:
        # 1. 이미 개설된 티켓 채널이 있는 경우 실시간 대화 전달
        existing_channel_id = config.check_user_m2(message.author.id, "channel")
        if existing_channel_id:
            channel = client.get_channel(existing_channel_id)
            if channel:
                user_nick = message.author.name
                guild = client.get_guild(int(config.config("guild")))
                if guild:
                    member = guild.get_member(message.author.id)
                    if member and member.nick:
                        user_nick = member.nick
                
                if message.attachments:
                    await message.add_reaction('❄️')
                    await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x2da4d8))
                    await channel.send(message.attachments[0].url)
                    open(f"log/{message.author.id}.txt", 'a', encoding='utf-8 sig').write(f"{user_nick} : {message.content} , {message.attachments[0].url}\n")
                else:
                    await message.add_reaction('❄️')
                    await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x2da4d8))
                    open(f"log/{message.author.id}.txt", 'a', encoding='utf-8 sig').write(f"{user_nick} : {message.content}\n")
            return

        # 2. 버튼을 누르지 않은 상태로 DM을 보낸 경우 차단
        if not is_pending:
            await message.channel.send(
                embed=discord.Embed(
                    title="Randy's 채널 고객센터", 
                    description="❌ 고객센터 패널의 **문의 버튼을 먼저 누른 후** 내용을 입력해 주세요!", 
                    color=0xff0000
                )
            )
            return

        # 3. 버튼을 누르고 첫 내용을 입력한 경우 티켓 채널 생성
        black, reason = config.check_black(message.author.id)
        if black == True:
            await message.channel.send(embed=discord.Embed(title="Randy's 문의 담당", description=f"안녕하세요 {message.author.name}님 당신은 '{reason}'의 사유로 블랙리스트에 등록되어 문의가 불가능합니다", color=0xff0000))
            return

        user_id = config.check_user_m(message.author.id)
        try:
            close_user_m[message.author.id]
        except:
            close_user_m[message.author.id] = 0

        if close_user_m[message.author.id] == 1:
            return await message.channel.send(embed=discord.Embed(title="Randy's 채널 고객센터", description=f"안녕하세요 {message.author.name}님 현재 전에 문의한 내용이 정리되고있습니다 잠시 후 다시 시도해주세요", color=0xff0000))

        if user_id == True:
            now = datetime.now()
            try:
                user_command_time[message.author.id]
            except:
                user_command_time[message.author.id] = now - timedelta(seconds=5)

            if user_command_time[message.author.id] <= now:
                guild = client.get_guild(int(config.config("guild")))
                guild2 = client.get_guild(int(config.config("guild2")))
                user = guild.get_member(message.author.id) if guild else None
                user_nick = user.nick if (user and user.nick) else message.author.name

                valid_channel_name = clean_channel_name(category, user_nick)

                try:
                    category_channel = client.get_channel(int(config.config("category")))
                    channel = await guild2.create_text_channel(valid_channel_name, category=category_channel)
                except Exception as err:
                    print(f"❌ 채널 생성 실패: {err}")
                    return await message.channel.send(
                        embed=discord.Embed(title="ERROR", description=f"채널 생성 중 오류가 발생했습니다: {err}", color=0xff0000)
                    )

                count, bool_val = config.check_url2(message.author.id)
                history_text = f"**{count}**건" if bool_val else "```해당 유저는 0건의 문의 내역이 있습니다```"

                embeda = discord.Embed(title="Randy's 채널 고객센터", description="유저에게 문의가 도착했어요!", color=0x2da4d8, timestamp=message.created_at)
                embeda.add_field(name="문의 카테고리", value=f"**{category}**" if category else "일반", inline=False)
                embeda.add_field(name="문의한 유저", value=f"{user_nick} (<@{message.author.id}>)", inline=False)
                embeda.add_field(name="문의 내역 건수", value=history_text, inline=False)
                embeda.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.display_avatar.url)

                await channel.send(content="@everyone", embed=embeda)
                config.insert_user(message.author.id, channel.id)

                if not os.path.exists("log"):
                    os.makedirs("log")

                if message.attachments:
                    user_command_time[message.author.id] = now + timedelta(seconds=5)
                    await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x2da4d8))
                    await channel.send(message.attachments[0].url)
                    open(f"log/{message.author.id}.txt", 'w', encoding='utf-8 sig').write(f"{user_nick} : {message.content} , {message.attachments[0].url}\n")
                else:
                    user_command_time[message.author.id] = now + timedelta(seconds=5)
                    await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x2da4d8))
                    open(f"log/{message.author.id}.txt", 'w', encoding='utf-8 sig').write(f"{user_nick} : {message.content}\n")
            else:
                check_time2 = user_command_time[message.author.id] - now
                seconds = check_time2.seconds - (check_time2.seconds // 3600) * 3600 - ((check_time2.seconds // 60) - (check_time2.seconds // 3600) * 60) * 60
                error_message = await message.reply(embed=discord.Embed(title="채팅 속도가 너무 빨라요!", description=f"첫 문의 후 다음 메시지는 {round(seconds, 1)}초 뒤에 다시 보낼 수 있어요!\n\n > 해당 메시지는 3초 뒤 삭제됩니다", color=0x2da4d8))
                await asyncio.sleep(3)
                return await error_message.delete()
