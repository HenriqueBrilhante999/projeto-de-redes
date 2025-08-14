import socket
import threading
import random
import json

class GameServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.players = []
        self.turn = 0  # 0 ou 1
        self.board = {}
        self.pontos = [0, 0]
        self.create_board()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        print(f"[SERVER] Aguardando jogadores em {host}:{port}")

    def create_board(self):
        bombas = random.sample(range(1, 65), 4)
        barcos = []
        while len(barcos) < 30:
            pos = random.randint(1, 64)
            if pos not in bombas and pos not in barcos:
                barcos.append(pos)
        mar = [i for i in range(1, 65) if i not in bombas and i not in barcos]
        for i in range(1, 65):
            if i in bombas:
                self.board[i] = "bomba"
            elif i in barcos:
                self.board[i] = "barco"
            else:
                self.board[i] = "mar"

    def broadcast(self, data):
        for conn in self.players:
            conn.sendall(json.dumps(data).encode())

    def handle_player(self, conn, player_id):
        conn.sendall(json.dumps({"type": "init", "player": player_id}).encode())
        while True:
            try:
                msg = conn.recv(1024)
                if not msg:
                    break
                data = json.loads(msg.decode())
                if data["type"] == "jogada":
                    numero = data["numero"]
                    if self.board.get(numero) == "bomba":
                        self.broadcast({
                            "type": "fim",
                            "causa": f"Player {player_id+1} encontrou uma bomba!",
                            "final_board": self.board
                        })
                        break
                    elif self.board.get(numero) == "barco":
                        self.pontos[player_id] += 1
                        self.board[numero] = "descoberto_barco"
                    elif self.board.get(numero) == "mar":
                        self.board[numero] = "descoberto_mar"
                    self.turn = 1 - self.turn
                    self.broadcast({
                        "type": "update",
                        "board": self.board,
                        "pontos": self.pontos,
                        "turno": self.turn
                    })
            except Exception as e:
                print(f"[ERRO] {e}")
                break
        conn.close()

    def start(self):
        while len(self.players) < 2:
            conn, addr = self.server.accept()
            self.players.append(conn)
            print(f"[SERVER] Jogador {len(self.players)} conectado de {addr}")
        for i in range(2):
            threading.Thread(target=self.handle_player, args=(self.players[i], i), daemon=True).start()
        self.broadcast({
            "type": "start",
            "board": self.board,
            "pontos": self.pontos,
            "turno": self.turn
        })

if __name__ == "__main__":
    GameServer().start()
