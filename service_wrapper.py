import win32serviceutil
import win32service
import win32event
import subprocess
import os
import logging

class AppService(win32serviceutil.ServiceFramework):
    _svc_name_ = "OpenShares"
    _svc_display_name_ = "Open Server Shares Service"
    _svc_description_ = "Runs the Open Server Shares FastAPI web application."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        # Set up logging
        logging.basicConfig(
            filename=r"C:\CNS4U\service_log.txt",
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger()
        self.logger.info("Service initialized.")

    def SvcStop(self):
        self.logger.info("Service stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        if self.process:
            self.process.terminate()
            self.logger.info("Service stopped successfully.")

    def SvcDoRun(self):
        # Set the working directory to where your FastAPI app is located
        os.chdir(r"C:\CNS4U")
        self.logger.info("Changed directory to C:\\CNS4U.")

        try:
            # Run your Uvicorn server using the full command with 'python -m uvicorn'
            self.process = subprocess.Popen(
                ["python", "-m", "uvicorn", "prodOpenFiles:app", "--host", "0.0.0.0", "--port", "9001"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.logger.info("Started uvicorn server.")

            # Continuously check for output and errors
            while True:
                output = self.process.stdout.readline()
                if output:
                    self.logger.info(output.strip().decode("utf-8"))
                error = self.process.stderr.readline()
                if error:
                    self.logger.error(error.strip().decode("utf-8"))

                if win32event.WaitForSingleObject(self.hWaitStop, 100) == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            self.logger.error(f"Exception occurred: {str(e)}")

        self.logger.info("Service is stopping due to external signal.")
        self.process.terminate()

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(AppService)
