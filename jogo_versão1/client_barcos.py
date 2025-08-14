import socket
import threading
import tkinter as tk
import json

class GameClient:
    def __init__(self, host="localhost", port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.jogador_id = None
        self.board = {}
        self.pontos = [0, 0]
        self.turno = 0
        self.botoes = {}
        self.janela = tk.Tk()
        self.janela.title("Jogo dos Barcos - Multiplayer")

        self.placar = tk.Label(self.janela, text="", font=("Arial", 14))
        self.placar.grid(row=0, column=0, columnspan=8)

        self.status = tk.Label(self.janela, text="", font=("Arial", 12))
        self.status.grid(row=1, column=0, columnspan=8)

        for i in range(64):
            numero = i + 1
            botao = tk.Button(self.janela, text=str(numero), width=6, height=2,
                              command=lambda num=numero: self.enviar_jogada(num))
            botao.grid(row=2 + i // 8, column=i % 8, padx=2, pady=2)
            self.botoes[numero] = botao

        threading.Thread(target=self.ouvir_servidor, daemon=True).start()
        self.janela.mainloop()

    def enviar_jogada(self, numero):
        if self.jogador_id != self.turno:
            return
        if self.board.get(numero, "").startswith("descoberto"):
            return
        self.sock.sendall(json.dumps({"type": "jogada", "numero": numero}).encode())

    def ouvir_servidor(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg["type"] == "init":
                    self.jogador_id = msg["player"]
                elif msg["type"] == "start" or msg["type"] == "update":
                    self.board = msg["board"]
                    self.pontos = msg["pontos"]
                    self.turno = msg["turno"]
                    self.atualizar_ui()
                elif msg["type"] == "fim":
                    self.board = msg["final_board"]
                    self.atualizar_ui(fim=True, causa=msg["causa"])
                    break
            except Exception as e:
                print("[ERRO CLIENTE]", e)
                break
        self.sock.close()

    def atualizar_ui(self, fim=False, causa=""):
        self.placar.config(
            text=f"Player 1: {self.pontos[0]} | Player 2: {self.pontos[1]}"
        )
        if fim:
            self.status.config(text=f"{causa}")
        else:
            vez = "sua vez" if self.jogador_id == self.turno else "vez do oponente"
            self.status.config(text=f"É {vez}")

        for i in range(1, 65):
            estado = self.board.get(i, "")
            botao = self.botoes[i]
            if estado == "descoberto_barco":
                botao.config(text="🚢", bg="green", state="disabled")
            elif estado == "descoberto_mar":
                botao.config(text="🌊", bg="lightblue", state="disabled")
            elif fim and estado == "bomba":
                botao.config(text="💣", bg="red", state="disabled")
            else:
                if estado.startswith("descoberto"):
                    botao.config(state="disabled")
                else:
                    botao.config(text=str(i), bg="SystemButtonFace", state="normal")

if __name__ == "__main__":
    host = input("Digite o IP do servidor (ex: localhost ou 192.168.x.x): ").strip()
    GameClient(host)
