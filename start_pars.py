"""Process orchestrator for launching and managing the Ozon scraper pipeline."""

import sys
import time
import subprocess 


def main() -> None: 
    """Starts the queue consumer and scraper worker processes simultaneously.

    Launches ``src/consumer.py`` as a background process first so it can
    initialize the database and listen to Redis, then starts ``src/main.py``
    and waits for its completion. Ensures the background consumer process is
    gracefully terminated upon exit or interruption.
    """
    parser_proc = None
    bot_proc = None
    consumer_proc = None
    try:
        consumer_proc = subprocess.Popen([sys.executable, "src/consumer.py"])
        time.sleep(1)
        parser_proc = subprocess.Popen([sys.executable, "src/main.py"])
        bot_proc = subprocess.Popen([sys.executable, "tg_bot.py"])
        bot_proc.wait()
    except KeyboardInterrupt:
        return
    finally:
        for proc in [parser_proc, bot_proc, consumer_proc]:
            if proc and proc.poll() is None:
                proc.terminate()
                proc.wait()


if __name__ == "__main__":
    main()
