import traceback, time

while True:
    try:
        b = 0
        a = 10 / b
    except Exception as e:
        traceback.print_exc()
        print("sleeping...")
        time.sleep(3)