import sys
import socket
import threading
import json
import tkinter as tk
import random
import time

# ============================
# FUNÇÃO AUXILIAR DE SOCKET
# ============================
def make_socket(ip_version="IPv4", protocol="TCP"):
    if ip_version == "IPv4":
        af = socket.AF_INET
    else:
        af = socket.AF_INET6

    if protocol == "TCP":
        sock_type = socket.SOCK_STREAM
    else:
        sock_type = socket.SOCK_DGRAM

    s = socket.socket(af, sock_type)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s

# ============================
# SERVIDOR
# ============================
class BarcosServer:
    def __init__(self, host, port, ip_version="IPv4", protocol="TCP"):
        self.protocol = protocol
        self.ip_version = ip_version
        self.server = make_socket(ip_version, protocol)
        if protocol == "TCP":
            self.server.bind((host, port))
            self.server.listen()
        self.clients = {}
        self.lock = threading.Lock()

        # Configuração inicial do jogo
        self.bombas = random.sample(range(1, 65), 4)
        self.barcos = []
        while len(self.barcos) < 30:
            pos = random.randint(1, 64)
            if pos not in self.bombas and pos not in self.barcos:
                self.barcos.append(pos)
        self.mar = [i for i in range(1, 65) if i not in self.bombas and i not in self.barcos]
        self.pontos = {"Player 1": 0, "Player 2": 0}
        self.turno = 0
        self.jogadores = ["Player 1", "Player 2"]
        self.game_over = False

    def start(self):
        if self.protocol == "TCP":
            threading.Thread(target=self.accept_clients, daemon=True).start()
        else:
            threading.Thread(target=self.udp_loop, daemon=True).start()

    def accept_clients(self):
        print(f"[SERVIDOR] Aguardando conexões em {self.server.getsockname()} (TCP)...")
        while len(self.clients) < 2:
            conn, addr = self.server.accept()
            player_id = len(self.clients)
            self.clients[player_id] = conn
            print(f"[SERVIDOR] Cliente {player_id} conectado: {addr}")
            conn.sendall(json.dumps({"type": "init", "player": player_id, "jogador": self.jogadores[player_id]}).encode())
            threading.Thread(target=self.handle_client, args=(conn, player_id), daemon=True).start()
        self.broadcast_state()

    def handle_client(self, conn, player_id):
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get("type") == "jogada" and not self.game_over:
                    self.processar_jogada(player_id, msg["numero"])
        except:
            pass
        finally:
            conn.close()
            with self.lock:
                if player_id in self.clients:
                    del self.clients[player_id]
            print(f"[SERVIDOR] Cliente {player_id} desconectado")

    def udp_loop(self):
        self.server.bind(self.server.getsockname())
        print(f"[SERVIDOR] Aguardando pacotes em {self.server.getsockname()} (UDP)...")
        while True:
            data, addr = self.server.recvfrom(4096)
            msg = json.loads(data.decode())
            player_id = None
            for pid, a in self.clients.items():
                if a == addr:
                    player_id = pid
            if player_id is None:
                if len(self.clients) < 2:
                    player_id = len(self.clients)
                    self.clients[player_id] = addr
                    init_msg = {"type": "init", "player": player_id, "jogador": self.jogadores[player_id]}
                    self.server.sendto(json.dumps(init_msg).encode(), addr)
                else:
                    continue
            if msg.get("type") == "jogada" and not self.game_over:
                self.processar_jogada(player_id, msg["numero"])

    def processar_jogada(self, player_id, numero):
        if self.jogadores[self.turno] != self.jogadores[player_id]:
            return
        jogador_atual = self.jogadores[player_id]
        if numero in self.bombas:
            self.game_over = True
            resultado = "bomba"
        elif numero in self.barcos:
            self.pontos[jogador_atual] += 1
            self.barcos.remove(numero)
            resultado = "barco"
            self.turno = 1 - self.turno
        elif numero in self.mar:
            self.mar.remove(numero)
            resultado = "agua"
            self.turno = 1 - self.turno
        else:
            return
        self.broadcast_state(resultado, numero)

    def broadcast_state(self, ultimo_resultado=None, ultima_pos=None):
        estado = {
            "type": "update",
            "pontos": self.pontos,
            "turno": self.jogadores[self.turno],
            "ultimo_resultado": ultimo_resultado,
            "ultima_pos": ultima_pos,
            "game_over": self.game_over,
            "bombas": self.bombas if self.game_over else None
        }
        for player_id, conn in list(self.clients.items()):
            try:
                if self.protocol == "TCP":
                    conn.sendall(json.dumps(estado).encode())
                else:
                    self.server.sendto(json.dumps(estado).encode(), conn)
            except:
                pass

# ============================
# CLIENTE
# ============================
class BarcosClient:
    def __init__(self, host, port, ip_version="IPv4", protocol="TCP"):
        self.protocol = protocol
        self.sock = make_socket(ip_version, protocol)
        self.jogador = None
        self.turno = None
        self.pontos = {}
        self.game_over = False
        self.bombas = []

        if protocol == "TCP":
            self.sock.connect((host, port))
        else:
            self.server_addr = (host, port)

        self.root = tk.Tk()
        self.root.title("Jogo dos Barcos Multiplayer")
        self.placar = tk.Label(self.root, text="", font=("Arial", 14))
        self.placar.grid(row=0, column=0, columnspan=8)
        self.status = tk.Label(self.root, text="", font=("Arial", 12))
        self.status.grid(row=1, column=0, columnspan=8)

        self.botoes = []
        for i in range(64):
            numero = i + 1
            botao = tk.Button(self.root, text=str(numero), width=6, height=2,
                              command=lambda num=numero: self.enviar_jogada(num))
            self.botoes.append(botao)
            botao.grid(row=2 + i // 8, column=i % 8, padx=2, pady=2)

        threading.Thread(target=self.receber_dados, daemon=True).start()
        self.root.mainloop()

    def enviar_jogada(self, numero):
        if self.turno != self.jogador or self.game_over:
            return
        msg = json.dumps({"type": "jogada", "numero": numero}).encode()
        if self.protocol == "TCP":
            self.sock.sendall(msg)
        else:
            self.sock.sendto(msg, self.server_addr)

    def receber_dados(self):
        def atualizar_interface(msg):
            if msg.get("type") == "init":
                self.jogador = msg["jogador"]
                self.root.title(f"Jogo dos Barcos - {self.jogador}")
            elif msg.get("type") == "update":
                self.pontos = msg["pontos"]
                self.turno = msg["turno"]
                self.game_over = msg["game_over"]
                self.placar.config(text=f"Player 1: {self.pontos['Player 1']} | Player 2: {self.pontos['Player 2']}")
                if self.game_over:
                    self.status.config(text="Fim de jogo!")
                    self.revelar_bombas(msg["bombas"])
                else:
                    self.status.config(text=f"Vez de {self.turno}")
                if msg["ultimo_resultado"] and msg["ultima_pos"]:
                    self.atualizar_botao(msg["ultima_pos"], msg["ultimo_resultado"])

        while True:
            try:
                data = self.sock.recv(4096) if self.protocol == "TCP" else self.sock.recvfrom(4096)[0]
                if not data:
                    break
                msgs = data.decode().split('}{')
                msgs = [m if m.startswith('{') else '{'+m for m in msgs]
                msgs = [m if m.endswith('}') else m+'}' for m in msgs]
                for m in msgs:
                    msg = json.loads(m)
                    self.root.after(0, atualizar_interface, msg)
            except:
                break

    def atualizar_botao(self, pos, resultado):
        botao = self.botoes[pos - 1]
        if resultado == "bomba":
            botao.config(text="💣", bg="red", state="disabled")
        elif resultado == "barco":
            botao.config(text="🚢", bg="green", state="disabled")
        elif resultado == "agua":
            botao.config(text="🌊", bg="lightblue", state="disabled")

    def revelar_bombas(self, bombas):
        for b in bombas:
            botao = self.botoes[b - 1]
            botao.config(text="💣", bg="red", state="disabled")

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("=== Batalha Naval Multiplayer ===")
    modo = input("Modo (server/client): ").strip().lower()
    while modo not in ["server", "client"]:
        modo = input("Digite 'server' ou 'client': ").strip().lower()

    # Normaliza o formato do IP version
    ip_version_input = input("IP version (IPv4/IPv6) [IPv4]: ").strip().upper() or "IPV4"
    while ip_version_input not in ["IPV4", "IPV6"]:
        ip_version_input = input("Digite 'IPv4' ou 'IPv6': ").strip().upper()
    ip_version_fmt = "IPv4" if ip_version_input == "IPV4" else "IPv6"

    protocol = input("Protocolo (TCP/UDP) [TCP]: ").strip().upper() or "TCP"
    while protocol not in ["TCP", "UDP"]:
        protocol = input("Digite 'TCP' ou 'UDP': ").strip().upper()

    if modo == "server":
        host = input("Host do servidor (deixe vazio para padrão): ").strip()
        if not host:
            host = "0.0.0.0" if ip_version_fmt == "IPv4" else "::"
        port_input = input("Porta do servidor [5000]: ").strip()
        port = int(port_input) if port_input else 5000

        print(f"[INFO] Servidor iniciando em {host}:{port} ({ip_version_fmt}/{protocol})...")
        srv = BarcosServer(host, port, ip_version_fmt, protocol)
        srv.start()
        time.sleep(1)
        local_ip = "127.0.0.1" if ip_version_fmt == "IPv4" else "::1"
        BarcosClient(local_ip, port, ip_version_fmt, protocol)

    elif modo == "client":
        host = input("Digite o IP do servidor: ").strip()
        port_input = input("Porta do servidor [5000]: ").strip()
        port = int(port_input) if port_input else 5000

        print(f"[INFO] Conectando ao servidor {host}:{port} ({ip_version_fmt}/{protocol})...")
        BarcosClient(host, port, ip_version_fmt, protocol)