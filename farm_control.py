import Adafruit_DHT
import RPi.GPIO as GPIO
import time
from datetime import datetime

# 센서 설정
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4           # 온습도 센서
RELAY_PIN = 18        # 릴레이 (워터펌프)
FLOATER_PIN = 17      # 플로트 스위치

# GPIO 초기화
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

GPIO.setup(FLOATER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

LOG_FILE = "/home/pi/farm_log.txt"

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        water_low = GPIO.input(FLOATER_PIN) == GPIO.HIGH

        if humidity is not None and temperature is not None:
            log(f"온도: {temperature:.1f}°C   습도: {humidity:.1f}%   수위: {'낮음' if water_low else '정상'}")

            if (temperature > 28 or humidity < 45):
                if water_low:
                    log("물이 부족합니다.")
                else:
                    log("워터펌프 작동 시작")
                    GPIO.output(RELAY_PIN, GPIO.LOW)
                    time.sleep(10)
                    GPIO.output(RELAY_PIN, GPIO.HIGH)
                    log("워터펌프 작동 종료")
        else:
            log("센서에서 값을 읽지 못했습니다.")

        time.sleep(120)

except KeyboardInterrupt:
    log("사용자 종료 요청")
    GPIO.cleanup()
    log("GPIO 정리 완료")
