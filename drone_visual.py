import cv2
import numpy as np
from pymavlink import mavutil
import time

# 1. CONEXÃO
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("Conectado!")

# Força o modo GUIDED e ARMA o drone via código
master.mav.command_long_send(master.target_system, master.target_component,
                             mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 1, 4, 0, 0, 0, 0, 0)
master.mav.command_long_send(master.target_system, master.target_component,
                             mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

def enviar_velocidade(vx, vy, vz):
    # Máscara que foca apenas nas velocidades lineares
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, 
        0b110111000111, 0, 0, 0, vx, vy, vz, 0, 0, 0, 0, 0
    )

camera = cv2.VideoCapture(0)

while True:
    sucesso, frame = camera.read()
    if not sucesso: break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mascara = cv2.inRange(hsv, lower_red, upper_red)
    
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contornos:
        maior = max(contornos, key=cv2.contourArea)
        area = cv2.contourArea(maior)
        
        if area > 800:
            M = cv2.moments(maior)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)
            
            vx, vy, vz = 0, 0, 0
            
            # Movimentos laterais (Y)
            if cx > 380: vy = 1.5
            elif cx < 260: vy = -1.5
            
            # Movimentos de altitude (Z)
            if cy < 150: vz = -0.8
            elif cy > 330: vz = 0.8
            
            # Movimentos de profundidade (X)
            if area < 6000: vx = 1.0
            elif area > 18000: vx = -1.0

            # Envia o comando múltiplas vezes para o buffer não ignorar
            for _ in range(2):
                enviar_velocidade(vx, vy, vz)
            
            print(f"ALVO OK | Vx:{vx} Vy:{vy} Vz:{vz} Area:{int(area)}")
    else:
        enviar_velocidade(0, 0, 0)
        print("Buscando...")

    cv2.imshow("Follower", frame)
    if cv2.waitKey(1) == 27: break

camera.release()
cv2.destroyAllWindows()
