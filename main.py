import nextcord, json, requests, re, certifi, httpx
from nextcord.ext import commands

bot, config = commands.Bot(command_prefix='flexzy!',help_command=None,intents=nextcord.Intents.all()), json.load(open('./config.json', 'r', encoding='utf-8'))

class BuyModal(nextcord.ui.Modal) :

   def __init__(self):
        super().__init__('กรอกลิ้งค์อั่งเปาของท่าน')
        self.a = nextcord.ui.TextInput(
            label = 'Truemoney Wallet Angpao',
            placeholder = 'https://gift.truemoney.com/campaign/?v=xxxxxxxxxxxxxxx',
            style = nextcord.TextInputStyle.short,
            required = True
        )
        self.add_item(self.a)

   async def callback(self, interaction: nextcord.Interaction):
        link = str(self.a.value).replace(' ', '')
        if re.match(r'https:\/\/gift\.truemoney\.com\/campaign\/\?v=+[a-zA-Z0-9]{18}', link):
            print(f'URL {link} DISCORD-ID {interaction.user.id}')
            voucher_hash = link.split('?v=')[1]
            response = httpx.post(
                url = f'https://gift.truemoney.com/campaign/vouchers/{voucher_hash}/redeem',
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Yourmom) Chrome/8a0.0.3987.149 Safari/537.36'
                },
                json = {
                    'mobile': config['phone'],
                    'voucher_hash': f'{voucher_hash}'
                },
                verify=certifi.where(),
            )
            if (response.status_code == 200 and response.json()['status']['code'] == 'SUCCESS'):
                data = response.json()
                embed = None
                amount = int(float(data['data']['my_ticket']['amount_baht']))
                for roleData in config['roleSettings']:
                    if (amount == roleData['price']):
                        role = nextcord.utils.get(interaction.user.guild.roles, id = int(roleData['roleId']))
                        if (role in interaction.user.roles):
                            embed = nextcord.Embed(
                                description=f'ไม่สามารถซื้อได้คุณมียศอยู่แล้ว',
                                color=nextcord.Color.from_rgb(255, 0, 0)
                            )
                        else:
                            await interaction.user.add_roles(role)
                            embed = nextcord.Embed(
                                description=f'เติมเงินสำเร็จ',
                                color=nextcord.Color.from_rgb(0, 255, 0)
                            )
                        await bot.get_channel(int(config['channelLog'])).send(embed=nextcord.Embed(
                            description=f'เติมเงินสำเร็จ {amount} โดย <@{interaction.user.id}>',
                            color=nextcord.Color.from_rgb(0, 255, 0)
                        ).add_field(
                            name='คุณได้รับยศ',
                            value=f'𓆩⟡𓆪 <@&{roleData["roleId"]}>'
                        ))
                        break
                if (embed == None):
                    embed = nextcord.Embed(description=f'จำนวนเงินผิดพลาด', color=nextcord.Color.from_rgb(255, 0, 0))
            else:
                print(response.text)
                embed = nextcord.Embed(description=f'ต้องมีอะไรผิดพลาดตรงไหนนนนนนนนนนนนน', color=nextcord.Color.from_rgb(255, 0, 0))
        else:
            embed = nextcord.Embed(description='เติมเงินไม่สำเร็จ : ลิ้งค์รับเงินแล้ว/ลิ้งค์ผิด', color=nextcord.Color.from_rgb(255, 0, 0))
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BuyView(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.link_button = nextcord.ui.Button(style=nextcord.ButtonStyle.link, label="จ้างทำบอท", url='https://discord.gg/flexzy') 
        self.add_item(self.link_button)

    @nextcord.ui.button(label='[🧧] เติมเงิน', custom_id='buyRole', style=nextcord.ButtonStyle.blurple)
    async def buyRole(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(BuyModal())

    @nextcord.ui.button(label='[🛒] ราคายศทั้งหมด', custom_id='priceRole', style=nextcord.ButtonStyle.blurple)
    async def priceRole(self, button: nextcord.Button, interaction: nextcord.Interaction):
        description = ''
        for roleData in config['roleSettings']:
            description += f'เติมเงิน {roleData["price"]} บาท จะได้รับยศ\n𓆩⟡𓆪  <@&{roleData["roleId"]}>\n₊✧──────✧₊∘\n'
        embed = nextcord.Embed(
            title='ราคายศทั้งหมด',
            color=nextcord.Color.from_rgb(93, 176, 242),
            description=description
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(BuyView())
    print(f"""          LOGIN AS: {bot.user}
    Successfully reloaded application [/] commands.""")

@bot.slash_command(name='setup',description='setup')
async def setup(interaction: nextcord.Interaction):
    if (int(interaction.user.id) == int(config['ownerId'])):
        await interaction.channel.send(embed=nextcord.Embed(
            title='**【⭐】Flexzy Store Topup**',
            description='ซื้อยศอัตโนมัติ 24ชั่วโมง\n・กดปุ่ม "เติมเงิน" เพื่อซื้อยศ\n・กดปุ่ม "ราคายศ" เพื่อดูราคายศ',
            color=nextcord.Color.from_rgb(100, 220, 255),
        ).set_thumbnail(url='https://cdn.discordapp.com/attachments/1105860649294237846/1171859094999662693/flexzyz.png?ex=65a809d4&is=659594d4&hm=463b298fab99c869af55ddc8c6379830c00a145e161c1bcd181ac4ba975e3912&')
        .set_image(url='https://images-ext-1.discordapp.net/external/JDnpFIEpRqs3lXwgtc6zk023mQP0KD5GDkXbRbWkAUM/https/www.checkraka.com/uploaded/img/content/130026/aungpao_truewallet_01.jpg?format=webp&width=810&height=540'), view=BuyView())
        await interaction.response.send_message((
        'Successfully reloaded application [/] commands.'
        ), ephemeral=True)
    else:
        await interaction.response.send_message((
           'มึงไม่ได้เป็น Owner ไอควาย ใช้ไม่ได้'
        ), ephemeral=True)

bot.run(config['token'])