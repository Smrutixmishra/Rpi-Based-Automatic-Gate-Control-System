import time
import RPi.GPIO as GPIO
from hx711 import HX711
# Pin setup
DT = 5
SCK = 6
SERVO_PIN = 18
LED_PIN = 26
BUZZER_PIN = 21
# Threshold for weight (grams)
WEIGHT_THRESHOLD = 1  # adjust based on sensitivity
SAMPLES = 15
DEADZONE = 5
# Servo angles
OPEN_ANGLE = 90
CLOSE_ANGLE = 0
# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Setup PWM for servo
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

def alert():
    GPIO.output(LED_PIN, GPIO.HIGH)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)

# Initialize HX711
hx = HX711(DT, SCK)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(-5052.77)  # Your calibrated value
hx.reset()
hx.tare()
print("Tare complete. System ready...")

# Track gate state
gate_open = False

try:
    while True:
        # Average weight
        weight = sum([hx.get_weight(1) for _ in range(SAMPLES)]) / SAMPLES
        print(f"Weight: {weight:.2f} grams")

        # Apply deadzone
        if abs(weight) < DEADZONE:
            weight = 0

        if abs(weight) >= WEIGHT_THRESHOLD and not gate_open:
            print("Weight detected. Opening gate.")
            alert()
            set_angle(OPEN_ANGLE)
            gate_open = True

        elif abs(weight) < WEIGHT_THRESHOLD and gate_open:
            print("Weight removed. Closing gate.")
            alert()
            set_angle(CLOSE_ANGLE)
            gate_open = False

        hx.power_down()
        hx.power_up()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")
    servo.stop()
    GPIO.cleanup()

 
