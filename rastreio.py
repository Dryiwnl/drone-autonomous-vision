import cv2
import numpy as np

# 1. Abre a câmera padrão
camera = cv2.VideoCapture(0)

while True:
    # 2. Captura o frame atual
    sucesso, frame = camera.read()
    if not sucesso:
        break

    # 3. Converte para HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 4. Cria a máscara para a cor Vermelha
    limite_inferior = np.array([0, 120, 70])
    limite_superior = np.array([10, 255, 255])
    mascara = cv2.inRange(hsv, limite_inferior, limite_superior)

    # 5. Calcula o Centro de Massa
    momentos = cv2.moments(mascara)
    
    # Se a área (m00) for maior que 0, significa que achou algo vermelho
    if momentos["m00"] > 0:
        centro_x = int(momentos["m10"] / momentos["m00"])
        centro_y = int(momentos["m01"] / momentos["m00"])
        print(f"[ALVO] Eixo X (Coluna): {centro_x} | Eixo Y (Linha): {centro_y}")
    else:
        print("Procurando alvo...")

    # 6. Mostra as imagens na tela
    cv2.imshow("Camera Original", frame)
    cv2.imshow("Mascara (O que o PC ve)", mascara)

    # Aguarda 30ms e sai se a tecla 'ESC' (código 27) for pressionada
    if cv2.waitKey(30) == 27:
        break

# Limpa a memória ao fechar
camera.release()
cv2.destroyAllWindows()
