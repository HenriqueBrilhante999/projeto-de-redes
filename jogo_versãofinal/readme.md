# 🚢 Batalha Naval Multiplayer

Um jogo de Batalha Naval multiplayer em Python com suporte a **TCP/UDP**, **IPv4/IPv6** e interface gráfica utilizando **Tkinter**.

Dois jogadores se conectam à mesma partida e tentam encontrar os barcos escondidos em um tabuleiro de 8x8. Cuidado com as bombas!

---

## 👨‍💻 Autores Do Projeto

- João Henrique Silva Brilhante
- Pedro Lucas Da Costa Manaia
- Antunes Fábio Ferreira De Oliveira

---

## 🎮 Funcionalidades

- Suporte a múltiplos protocolos: `TCP` e `UDP`
- Compatibilidade com `IPv4` e `IPv6`
- Interface gráfica amigável com `Tkinter`
- Geração aleatória de barcos e bombas
- Gerenciamento de turnos entre dois jogadores
- Game over automático ao encontrar bomba

---

## ⚙️ Como executar

### 🔧 Requisitos

- Python 3.10 ou superior
- Tkinter (geralmente já incluso com Python)
- VScode

---

### ▶️ Iniciar o Servidor

- 1 - use vscode para abrir o codigo e escreva em seu terminal:
python batalhanaval.py
- 2 - logo depois, irá aparecer para escolher seu modo, server ou client:
- 2.1 - caso seu pc seja o pc que irá ser o server:
server
- 2.2 - caso seja o segundo pc, digite:
client
- 3 - versão do ip e protocolo, a versão do ip vai de sua preferencia, o protocolo TCP é melhor para jogos de turno como este:
(apenas um exemplo):
IPv4
TCP
- 4 - aqui caso você seja o servidor, voce deve digitar o host e a porta, caso seja o cliente, deve por o ip e a porta definida pelo pc server:
(apenas um exemplo):
- 4.1 - server:
0.0.0.0
7000
- 4.2 - cliente:
10.65.XX.XX
7000
- 5 - aguardar a conexão
- 6 - jogar  

