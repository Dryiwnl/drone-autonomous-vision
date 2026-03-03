from pymavlink import mavutil
import time

# 1. Conecta ao simulador
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("[JETSON] Conectado à Pixhawk!")

# 2. Muda para o modo GUIDED (O número 4 representa o GUIDED no ArduCopter)
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    4)
print("[JETSON] Ordem enviada: Modo GUIDED")
time.sleep(2) # Espera 2 segundos para a placa processar

# 3. Arma os motores (Destrava a segurança. O número 1 liga, o 0 desliga)
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0)
print("[JETSON] Ordem enviada: Armar motores")
time.sleep(2)

# 4. Comanda a decolagem (O último número '10' é a altitude desejada em metros)
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 10)
print("[JETSON] Ordem enviada: Decolar para 10 metros!")




# 5. Esperar o drone atingir os 10 metros de altura
time.sleep(10)

# 6. Mover 10 metros para frente (Norte) mantendo a altitude
print("[JETSON] Indo 10 metros para a frente...")

master.mav.send(
    mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
        10, # timestamp (ignorado pela placa)
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # Usa o sistema NED
        int(0b110111111000), # Máscara indicando que vamos enviar apenas posição (X,Y,Z)
        10, 0, -10, # Coordenadas: X (10m frente), Y (0m lado), Z (-10m altura, lembre-se do negativo)
        0, 0, 0, # Velocidade X, Y, Z (ignoradas pela máscara)
        0, 0, 0, # Aceleração X, Y, Z (ignoradas pela máscara)
        0, 0 # Ângulo (Yaw) (ignorado)
    )
)
print("[JETSON] Ordem de movimento enviada com sucesso!")
