import base64
import time
from ultralytics import YOLO
import obsws_python as obs
from PIL import Image
import io
import cv2
import numpy as np

# ---------------- YOLO ----------------
model = YOLO("best.pt")  # Verifique se o caminho está correto

# ---------------- Conexão OBS ----------------
try:
    ws = obs.ReqClient(host="localhost", port=4455, password="pedro123")
    print("Conectado ao OBS!")
except Exception as e:
    print(f"Erro ao conectar ao OBS: {e}")
    exit()

SOURCE_NAME = "Tela"  # Nome exato da fonte do OBS

# ---------------- Loop principal ----------------
prev_time = time.time()
try:
    while True:
        try:
            # Captura screenshot
            resp = ws.get_source_screenshot(
                name=SOURCE_NAME,
                img_format="png",
                width=640,   # menor que 1920
                height=360,  # menor que 1200
                quality=60
            )

            # Decodifica base64 com proteção
            try:
                img_data_b64 = resp.image_data.strip().replace("\n", "")
                # Adiciona padding
                img_data_b64 += "=" * ((4 - len(img_data_b64) % 4) % 4)
                img_data = base64.b64decode(img_data_b64)
                img = Image.open(io.BytesIO(img_data))
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"Erro ao decodificar Base64, pulando frame: {e}")
                continue  # pula esse frame e tenta o próximo

            # Rodar YOLO
            results = model(frame, verbose=False)[0]

            # Desenhar caixas
            for box in results.boxes:
                xyxy = box.xyxy.cpu().numpy().astype(int).flatten()
                x1, y1, x2, y2 = xyxy
                conf = float(box.conf.cpu().numpy())
                cls = int(box.cls.cpu().numpy())
                label = f"{model.names[cls]} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Calcular FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Mostrar frame
            cv2.imshow("OBS YOLO Detection", frame)

            # Sair se apertar 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        except Exception as e:
            print(f"Erro no loop principal: {e}")
            time.sleep(0.5)
            continue

finally:
    try:
        ws.disconnect()
    except:
        pass
    cv2.destroyAllWindows()
