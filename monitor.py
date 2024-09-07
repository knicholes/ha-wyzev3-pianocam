import threading
import logging
import queue

class Monitor:
    def __init__(self, result_queue):
        self.result_queue = result_queue
        self.stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self._monitor_results, daemon=True).start()

    def _monitor_results(self):
        logging.info("Monitoring detection results.")
        results = {'audio': None, 'video': None}
        while not self.stop_event.is_set():
            try:
                result = self.result_queue.get(timeout=1)
                results[result['type']] = result['status']
                logging.info(f"Detection Results - Audio: {results['audio']}, Video: {results['video']}")
                # Implement logic to send updates to external systems here
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Monitor error: {e}")

    def stop(self):
        self.stop_event.set()
        logging.info("Monitor stopped.")
