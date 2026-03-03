import cv2
import numpy as np
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

master.mav.command_long_send(master.target_system, master.target_component,
                             mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 1, 4, 0, 0, 0, 0, 0)
master.mav.command_long_send(master.target_system, master.target_component,
                             mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

def enviar_velocidade(vx, vy, vz):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, 
        0b110111000111, 0, 0, 0, vx, vy, vz, 0, 0, 0, 0, 0
    )

def comandar_pouso():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        1, 9, 0, 0, 0, 0, 0)

camera = cv2.VideoCapture(0)
pousando = False

while True:
    sucesso, frame = camera.read()
    if not sucesso: break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    mascara = cv2.inRange(hsv, lower_green, upper_green)

    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contornos and not pousando:
        maior = max(contornos, key=cv2.contourArea)
        area = cv2.contourArea(maior)
        
        if area > 800:
            M = cv2.moments(maior)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1)
            
            vx, vy, vz = 0, 0, 0

            if area > 5000:
                comandar_pouso()
                print("Acionando pouso")
                pousando = True
            else:
                enviar_velocidade(vx, vy, vz)
                print(f"Buscando... área:{area}")
        else:
            enviar_velocidade(0, 0, 0)
            
    elif not pousando:
        enviar_velocidade(0, 0, 0)

    cv2.imshow("Pouso de emergencia", frame)
    if cv2.waitKey(1) == 27: break

camera.release()
cv2.destroyAllWindows()