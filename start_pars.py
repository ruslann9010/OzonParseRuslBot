import sys
import time
import subprocess 


def main(): 
    consumer_proc = None
    try:
        consumer_proc = subprocess.Popen([sys.executable, "src/consumer.py"])
        time.sleep(1)
        parser_proc = subprocess.Popen([sys.executable, "src/main.py"])
        parser_proc.wait()
        time.sleep(2)
    finally:
        if consumer_proc and consumer_proc.poll() is None:
            consumer_proc.terminate()
            consumer_proc.wait()


if __name__ == "__main__":
    main()
