import subprocess


class SystemService:

    def open_application(self, application: str) -> bool:

        try:

            subprocess.Popen(application)

            return True

        except Exception as e:

            print(e)

            return False