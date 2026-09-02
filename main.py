import os
import sys
import asyncio
import importlib
from datetime import datetime
import discord
from discord import app_commands
from source import add_message
from source import config

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_screen()

# 1. 인텐트 및 클라이언트 설정
intents = discord.Intents.all()

# 버튼 클릭 후 메시지 작성을 기다리는 유저 세션 {user_id: "카테고리명"}
pending_users = {}

# config.json에 등록된 관리 서버 ID (티켓 채널이 생성되는 서버)
TARGET_GUILD_ID = int(config.config("guild2"))
guild_obj = discord.Object(id=TARGET_GUILD_ID)

class RandyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(InquiryView())
        
        # 전역 명령어 정리 후 관리 서버에만 동기화
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        await self.tree.sync(guild=guild_obj)

client = RandyBot()

# 2. 첫 내용 입력 시 DM으로 전송될 "문의 시작" 임베드
def create_start_embed(user_name: str, category_name: str) -> discord.Embed:
    embed = discord.Embed(
        title="Randy's 채널 고객센터",
        description=(
            f"**{user_name}**님의 **[{category_name}]** 접수가 정상적으로 시작되었습니다.\n\n"
            "> 문의 내용이 관리팀으로 전달되었으며 확인 후 답변을 드릴 예정입니다.\n\n"
            "> 관리자가 문의를 확인하고 처리를 완료할 때까지 기다려 주세요."
        ),
        color=0x2da4d8,
        timestamp=discord.utils.utcnow()
    )
    if client.user.avatar:
        embed.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.avatar.url)
    else:
        embed.set_footer(text="Randy's 채널 고객센터")
    return embed

# 3. 4개 카테고리 버튼 UI (일반문의, 후원문의, 유저 신고, 기타문의)
class InquiryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def prepare_inquiry(self, interaction: discord.Interaction, category: str, guide_detail: str):
        pending_users[interaction.user.id] = category

        await interaction.response.send_message(
            f"✅ **{category}** 접수 단계입니다. 개인 DM을 확인하여 내용을 작성해 주세요!", 
            ephemeral=True
        )

        try:
            guide_msg = (
                f"📋 **[Randy's 고객센터 - {category}]**\n\n"
                f"{guide_detail}\n\n"
                "👉 **문의하실 내용을 이 DM에 적어서 보내주세요.**\n"
                "(메시지를 전송하시면 정식으로 접수되며 관리자 채널이 개설됩니다.)"
            )
            await interaction.user.send(guide_msg)
        except discord.Forbidden:
            if interaction.user.id in pending_users:
                del pending_users[interaction.user.id]
            await interaction.followup.send(
                "❌ DM을 보낼 수 없습니다. 디스코드 설정에서 '서버 멤버가 보내는 다이렉트 메시지 허용'을 켜주세요.", 
                ephemeral=True
            )

    @discord.ui.button(label="일반문의", style=discord.ButtonStyle.primary, custom_id="inquiry_general")
    async def general_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.prepare_inquiry(interaction, "일반문의", "궁금하신 사항이나 도움받으실 내용을 상세히 작성해 주세요.")

    @discord.ui.button(label="후원문의", style=discord.ButtonStyle.primary, custom_id="inquiry_donation")
    async def donation_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.prepare_inquiry(interaction, "후원문의", "후원과 관련된 문의 사항을 남겨주세요.")

    @discord.ui.button(label="유저 신고", style=discord.ButtonStyle.danger, custom_id="inquiry_report")
    async def report_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.prepare_inquiry(
            interaction, 
            "유저 신고", 
            "[유저 신고 양식]\n1. 신고 대상 유저 닉네임:\n2. 신고 사유:\n3. 발생 시각 및 증거 링크(스크린샷/영상):"
        )

    @discord.ui.button(label="기타문의", style=discord.ButtonStyle.secondary, custom_id="inquiry_etc")
    async def etc_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.prepare_inquiry(interaction, "기타문의", "기타 문의나 건의하실 내용을 자유롭게 작성해 주세요.")

# 4. 슬래시 커맨드: /고객센터 (서버 전용 등록)
@client.tree.command(name="고객센터", description="Randy's 채널 고객센터 안내 패널과 문의 버튼을 생성합니다.", guild=guild_obj)
@app_commands.default_permissions(administrator=True)
async def setup_center_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Randy's 채널 고객센터",
        description=(
            "• 본 고객센터는 채널의 여러 문의를 접수하기 위한 공간이며 이를 악용하는 유저는 이용제한 조치 대상입니다.\n\n"
            "아래의 항목 중 해당되는 카테고리를 선택하여 고객센터 문의를 시작하세요.\n"
            "• 봇 고객센터에 먼저 DM이 아닌 아래 버튼을 누르면 개인 DM으로 전환됩니다."
        ),
        color=discord.Color.dark_theme()
    )
    await interaction.response.send_message(embed=embed, view=InquiryView())

# 5. 슬래시 커맨드: /문의종료 (서버 전용 등록)
@client.tree.command(name="문의종료", description="문의 채널을 정리하고 로그를 저장한 뒤 종료합니다.", guild=guild_obj)
@app_commands.default_permissions(administrator=True)
async def close_inquiry_slash(interaction: discord.Interaction):
    target_user_id = config.check_user_m2(interaction.channel_id, "")
    
    if not target_user_id:
        await interaction.response.send_message(
            embed=discord.Embed(title="ERROR", description="😅 이곳은 문의 티켓 채널이 아닙니다.", color=0xff0000),
            ephemeral=True
        )
        return

    add_message.close_user_m[target_user_id] = 1
    await interaction.response.send_message("🔒 3초 뒤 해당 유저의 문의가 종료되고 채널이 삭제됩니다.")
    await asyncio.sleep(3)

    current_channel = interaction.channel
    config.delete_user(current_channel.id)
    await current_channel.delete()

    user = client.get_user(int(target_user_id))
    if user:
        dm_embed = discord.Embed(
            title="Randy's 채널 고객센터",
            description=(
                f"{user.name}님 문의가 종료되었습니다\n\n"
                "> 다시 문의하고 싶으신 경우에만 메시지를 다시 보내주세요\n\n"
                "> 앞으로 더욱 나아가는 Randy's 채널이 되겠습니다 :)"
            ),
            color=0x2da4d8,
            timestamp=discord.utils.utcnow()
        )
        if client.user.avatar:
            dm_embed.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.avatar.url)
        else:
            dm_embed.set_footer(text="Randy's 채널 고객센터")
        try:
            await user.send(embed=dm_embed)
        except Exception:
            pass

    log_channel_id = config.config("log_channel")
    log_channel = client.get_channel(int(log_channel_id))
    log_file_path = f"log/{target_user_id}.txt"

    if log_channel and os.path.exists(log_file_path):
        now = datetime.now()
        log_embed = discord.Embed(
            title=f"{now.strftime('%Y - %m - %d')}",
            color=0x2da4d8,
            timestamp=discord.utils.utcnow()
        )
        log_embed.add_field(
            name="문의 종료 로그",
            value=f"문의한 유저 : <@{target_user_id}>\n\n문의 종료 담당자 : <@{interaction.user.id}>",
            inline=True
        )
        if client.user.avatar:
            log_embed.set_footer(text="Randy's 채널 고객센터", icon_url=client.user.avatar.url)
        
        await log_channel.send(embed=log_embed)
        
        file = discord.File(log_file_path)
        await log_channel.send(file=file)
        
        os.remove(log_file_path)

    config.check_count(target_user_id)
    add_message.close_user_m[target_user_id] = 0

# 6. 이벤트 핸들러
@client.event
async def on_ready():
    clear_screen()
    print(f"Logged in as {client.user} - 봇이 준비되었습니다")

@client.event
async def on_message(message):
    if message.author.bot:
        return None

    if message.content.startswith("##리로드"):
        importlib.reload(add_message)
        importlib.reload(config)
        await message.reply(embed=discord.Embed(title="Module Reload", description="✅ 모든 모듈을 다시 시작했습니다"))
        return
    elif message.content.startswith("##정리"):
        clear_screen()
        return

# 유저의 개인 DM 메시지 처리
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id in pending_users:
            category = pending_users.pop(message.author.id)
            
            # 1) 시작 확인 임베드 전송
            start_embed = create_start_embed(message.author.name, category)
            await message.channel.send(embed=start_embed)

            # 2) 첫 문의 접수 상태임을 명시하여 전달
            message.content = f"[{category}] {message.content}"
            await add_message.go_message(client, message, category=category, is_pending=True)
            return

    # 기존 실시간 대화 중계
    await add_message.go_message(client, message, is_pending=False)

client.run(config.config("token"))
