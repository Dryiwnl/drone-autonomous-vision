import sys
import os

# Tenta encontrar e adicionar o caminho do Gazebo automaticamente
gz_path = "/usr/lib/python3/dist-packages"
if gz_path not in sys.path:
    sys.path.append(gz_path)

try:
    from gz.transport13 import Node
    print("Sucesso: Biblioteca 'gz' encontrada!")
except ImportError:
    print("ERRO: Ainda não encontrei a biblioteca 'gz'.")
    print("Tente rodar no terminal: sudo apt install python3-gz-transport13")
    sys.exit()

import cv2
import numpy as np
from pymavlink import mavutil
from gz.transport13 import Node

# --- CONFIGURAÇÃO ---
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

frame_gz = None

def image_callback(msg):
    global frame_gz
    # Converte os bytes do Gazebo diretamente para imagem OpenCV
    img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)
    frame_gz = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

node = Node()
# O tópico no Gazebo Harmonic para o Iris é /camera
node.subscribe('/camera', image_callback)

def enviar_velocidade(vx, vy, vz):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, 
        0b110111000111, 0, 0, 0, vx, vy, vz, 0, 0, 0, 0, 0
    )

print("Sistema iniciado. Aguardando conexão com Gazebo...")

# --- LOOP PRINCIPAL ---
try:
    while True:
        if frame_gz is not None:
            frame = frame_gz.copy()
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Filtro Verde
            mask = cv2.inRange(hsv, np.array([35, 100, 100]), np.array([85, 255, 255]))
            contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contornos:
                maior = max(contornos, key=cv2.contourArea)
                if cv2.contourArea(maior) > 500:
                    M = cv2.moments(maior)
                    cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                    
                    # LOGICA SUAVE
                    vy = (cx - 320) * 0.005
                    vz = (cy - 240) * 0.005
                    vx = (10000 - cv2.contourArea(maior)) * 0.0001
                    
                    enviar_velocidade(np.clip(vx, -1, 1), np.clip(vy, -1, 1), np.clip(vz, -1, 1))
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)
            else:
                enviar_velocidade(0, 0, 0)

            cv2.imshow("Drone View", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cv2.destroyAllWindows()