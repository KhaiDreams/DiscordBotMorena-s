import discord
from discord.ui import Modal, TextInput
from utils import (
    formatar_data_brasil,
    converter_para_brasil,
    obter_agora_brasil,
    carregar_sorteios,
    salvar_sorteios,
    carregar_records,
    salvar_records,
)
from config import OWNER_ID, msg_com_botao

class SorteioModal(Modal, title="🎁 Criar Novo Sorteio"):
    def __init__(self, canal_id: int):
        super().__init__(timeout=300)
        self.canal_id = canal_id

        self.titulo = TextInput(
            label="Título do sorteio", 
            placeholder="Ex: Sorteio de gift card", 
            max_length=100
        )
        self.participantes = TextInput(
            label="Participantes (1 por linha)", 
            style=discord.TextStyle.paragraph, 
            placeholder="Ex:\nMaria\nJoão\nCarlos"
        )
        self.data = TextInput(
            label="Data (DD/MM/AAAA HH:MM)", 
            placeholder="Ex: 28/05/2025 18:00"
        )

        self.add_item(self.titulo)
        self.add_item(self.participantes)
        self.add_item(self.data)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data_formatada = converter_para_brasil(self.data.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Data inválida! Use o formato DD/MM/AAAA HH:MM", ephemeral=True)
            return

        agora_brasil = obter_agora_brasil()
        if data_formatada <= agora_brasil:
            await interaction.response.send_message("❌ A data do sorteio deve ser no futuro!", ephemeral=True)
            return

        lista_participantes = [p.strip() for p in self.participantes.value.strip().split("\n") if p.strip()]
        if not lista_participantes:
            await interaction.response.send_message("❌ Adicione pelo menos um participante.", ephemeral=True)
            return

        sorteios = carregar_sorteios()
        sorteios.append({
            "titulo": self.titulo.value.strip(),
            "participantes": lista_participantes,
            "data": formatar_data_brasil(data_formatada),
            "feito": False,
            "canal_id": self.canal_id
        })
        salvar_sorteios(sorteios)

        embed = discord.Embed(
            title="📢 Sorteio Criado!",
            description=f"**Título:** {self.titulo.value.strip()}\n📅 Data: {formatar_data_brasil(data_formatada)} (horário de Brasília)\n👥 Participantes: {len(lista_participantes)}",
            color=discord.Color.green()
        )
        embed.set_footer(text="O resultado será postado aqui automaticamente. Boa sorte! 🍀")

        global msg_com_botao
        if msg_com_botao:
            try:
                await msg_com_botao.delete()
            except:
                pass
            msg_com_botao = None

        await interaction.response.send_message(embed=embed)

class RecordModal(Modal, title="🏁 Criar Record"):
    def __init__(self, autor_id: int):
        super().__init__(timeout=300)
        self.autor_id = autor_id

        self.titulo = TextInput(
            label="Título do Record", 
            placeholder="Ex: Maior número de kills em 1 partida", 
            max_length=100
        )
        self.descricao = TextInput(
            label="Quantidade do seu record", 
            style=discord.TextStyle.paragraph, 
            placeholder="Detalhes do record...", 
            max_length=500
        )

        self.add_item(self.titulo)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        records = carregar_records()
        records.append({
            "titulo": self.titulo.value.strip(),
            "descricao": self.descricao.value.strip(),
            "autor_id": self.autor_id,
            "tentativas": [],
        })
        salvar_records(records)

        embed = discord.Embed(
            title="✅ Record criado!",
            description=f"🏁 **{self.titulo.value.strip()}**\n📝 {self.descricao.value.strip()}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

class SugestaoModal(discord.ui.Modal, title="Enviar sugestão"):
    sugestao = discord.ui.TextInput(
        label="Qual é sua sugestão?",
        style=discord.TextStyle.paragraph,
        placeholder="Escreve aqui sua ideia pro bot!",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        dono = await interaction.client.fetch_user(OWNER_ID)
        embed = discord.Embed(
            title="📬 Nova sugestão recebida!",
            description=self.sugestao.value,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Enviado por: {interaction.user} (ID: {interaction.user.id})")

        try:
            await dono.send(embed=embed)
            await interaction.response.send_message("Valeu! Sua sugestão foi enviada!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Não consegui mandar pro dono, tenta avisar ele direto!", ephemeral=True)
