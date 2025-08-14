import tkinter as tk
import random
bombas = random.sample(range(1, 65), 4)
barcos = []
while len(barcos) < 30:
    pos = random.randint(1, 64)
    if pos not in bombas and pos not in barcos:
        barcos.append(pos)

mar = [i for i in range(1, 65) if i not in bombas and i not in barcos]
pontos = {"Player 1": 0, "Player 2": 0}
turno = [0] 
jogadores = ["Player 1", "Player 2"]
def escolher(numero, botao):
    jogador_atual = jogadores[turno[0]]
    
    if numero in bombas:
        botao.config(text="💣", bg="red", state="disabled")
        status.config(text=f"{jogador_atual} encontrou uma bomba! Fim de jogo!")
        desativar_todos()
    elif numero in barcos:
        botao.config(text="🚢", bg="green", state="disabled")
        pontos[jogador_atual] += 1
        placar.config(text=f"Player 1: {pontos['Player 1']} | Player 2: {pontos['Player 2']}")
        turno[0] = 1 - turno[0]
        status.config(text=f"Vez de {jogadores[turno[0]]}")
    elif numero in mar:
        botao.config(text="🌊", bg="lightblue", state="disabled")
        turno[0] = 1 - turno[0]
        status.config(text=f"Vez de {jogadores[turno[0]]}")
def desativar_todos():
    for botao in botoes:
        botao.config(state="disabled")
janela = tk.Tk()
janela.title("Jogo dos Barcos - 2 Jogadores")

placar = tk.Label(janela, text="Player 1: 0 | Player 2: 0", font=("Arial", 14))
placar.grid(row=0, column=0, columnspan=8)

status = tk.Label(janela, text="Vez de Player 1", font=("Arial", 12))
status.grid(row=1, column=0, columnspan=8)

botoes = []
for i in range(64):
    numero = i + 1
    botao = tk.Button(janela, text=str(numero), width=6, height=2,
                      command=lambda num=numero, b=None: escolher(num, botoes[num-1]))
    botoes.append(botao)
    botao.grid(row=2 + i // 8, column=i % 8, padx=2, pady=2)

janela.mainloop()
