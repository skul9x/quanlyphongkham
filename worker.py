import sys
import traceback
from PySide6.QtCore import QRunnable, QObject, Signal, Slot

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    """
    Worker thread
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        # print(f"[WORKER] Thread started for: {self.fn.__name__ if hasattr(self.fn, '__name__') else str(self.fn)}")
        try:
            result = self.fn(*self.args, **self.kwargs)
            # print("[WORKER] Function executed successfully")
        except:
            traceback.print_exc() # Print to console/debug tab
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
            print(f"[WORKER] Error emitted: {value}")
        else:
            # Safe emit: Catch errors in slots connected to result
            try:
                self.signals.result.emit(result)
                # print("[WORKER] Result emitted")
            except:
                print("CRITICAL ERROR: Failed to emit result signal from Worker.")
                traceback.print_exc()
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()
            # print("[WORKER] Thread finished")