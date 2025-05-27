import discord
from utils import (
    carregar_records,
    salvar_records,
    formatar_data_brasil,
    obter_agora_brasil,
    converter_para_brasil,
)

def register_record_commands(bot):
    @bot.command()
    async def records(ctx):
        """Display all records"""
        records = carregar_records()
        if not records:
            await ctx.send("❌ Nenhum record foi criado ainda.")
            return

        embed = discord.Embed(title="🏁 Lista de Records", color=discord.Color.orange())
        for i, record in enumerate(records, start=1):
            embed.add_field(
                name=f"{i}. {record['titulo']}",
                value=f"{record['descricao']}\n🎯 Tentativas: {len(record['tentativas'])}",
                inline=False
            )
        await ctx.send(embed=embed)

    @bot.command()
    async def tentativa(ctx, id: str = None, valor: str = None):
        """Submit an attempt for a record"""
        if id is None or valor is None:
            await ctx.send("❌ Você deve informar o número do record e a quantidade. Exemplo: `.tentativa 1 50`")
            return

        try:
            id_int = int(id)
        except ValueError:
            await ctx.send("❌ O número do record deve ser um número inteiro válido.")
            return

        try:
            valor_float = float(valor)
        except ValueError:
            await ctx.send("❌ A quantidade deve ser um número válido. Exemplo: 50 ou 3.14")
            return

        records = carregar_records()
        if id_int < 1 or id_int > len(records):
            await ctx.send("❌ Record não encontrado.")
            return

        record = records[id_int - 1]

        tentativa_antiga = None
        for t in record["tentativas"]:
            if t["user"] == ctx.author.name:
                tentativa_antiga = t
                break

        agora_brasil = obter_agora_brasil()
        nova_tentativa = {
            "user": ctx.author.name,
            "valor": valor_float,
            "data": formatar_data_brasil(agora_brasil)
        }

        if tentativa_antiga:
            record["tentativas"].remove(tentativa_antiga)
            record["tentativas"].append(nova_tentativa)
            await ctx.send(f"✅ Tentativa atualizada para o record **{record['titulo']}** com valor {valor_float}!")
        else:
            record["tentativas"].append(nova_tentativa)
            await ctx.send(f"✅ Tentativa adicionada ao record **{record['titulo']}** com valor {valor_float}!")

        salvar_records(records)

    @bot.command()
    async def ranking(ctx, id: int = None):
        """Display ranking for a specific record by its number"""
        records = carregar_records()
        if not records:
            await ctx.send("❌ Nenhum record foi criado ainda.")
            return

        if id is None:
            await ctx.send("❌ Você precisa informar o número do record. Exemplo: `.ranking 1`")
            return

        if id < 1 or id > len(records):
            await ctx.send("❌ Record não encontrado.")
            return

        record = records[id - 1]
        tentativas = record.get("tentativas", [])

        if not tentativas:
            await ctx.send(f"❌ Nenhuma tentativa registrada para o record **{record['titulo']}**.")
            return

        tentativas_ordenadas = sorted(
            tentativas,
            key=lambda t: (-t["valor"], converter_para_brasil(t["data"]))
        )

        ranking_str = ""
        medalhas = {1: "🥇 Ouro", 2: "🥈 Prata", 3: "🥉 Bronze"}

        for pos, t in enumerate(tentativas_ordenadas, start=1):
            medalha = medalhas.get(pos, f"**{pos}.**")
            ranking_str += f"{medalha} {t['user']} - `{t['valor']}` em {t['data']}\n"

        embed = discord.Embed(
            title=f"🏆 Ranking do Record: {record['titulo']}",
            description=f"📝 {record['descricao']}\n\n{ranking_str}",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Horários em fuso de Brasília")

        await ctx.send(embed=embed)

    @bot.command()
    async def deletar_record(ctx, id: int):
        """Delete a record (only creator can delete)"""
        records = carregar_records()
        if id < 1 or id > len(records):
            await ctx.send("❌ Record não encontrado.")
            return

        record = records[id - 1]
        if record["autor_id"] != ctx.author.id:
            await ctx.send("❌ Só o criador desse record pode deletar.")
            return

        titulo = record["titulo"]
        del records[id - 1]
        salvar_records(records)

        await ctx.send(f"🗑️ Record **{titulo}** foi deletado com sucesso.")
