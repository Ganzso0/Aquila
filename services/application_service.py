from pathlib import Path
import json
import win32com.client

CATALOG_PATH = Path("cache") / "applications.json"


class ApplicationService:

    def __init__(self):

        self.applications = {}

        if self.catalog_exists():
            print("Cargando catálogo...")
            self.load_catalog()
        else:
            print("Escaneando aplicaciones...")
            self.scan()
            self.save_catalog()

    # =====================================================
    # Catálogo
    # =====================================================

    def catalog_exists(self) -> bool:
        return CATALOG_PATH.exists()

    def load_catalog(self):

        with open(CATALOG_PATH, "r", encoding="utf-8") as file:
            self.applications = json.load(file)

    def save_catalog(self):

        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(CATALOG_PATH, "w", encoding="utf-8") as file:
            json.dump(self.applications, file, indent=4)

    def refresh_catalog(self):

        self.applications.clear()

        self.scan()

        self.save_catalog()

    # =====================================================
    # Escaneo
    # =====================================================

    def scan(self):

        self.applications.clear()

        self.scan_start_menu()

    def scan_start_menu(self):

        shell = win32com.client.Dispatch("WScript.Shell")

        start_menus = [

            Path.home()
            / "AppData"
            / "Roaming"
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs",

            Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs")

        ]

        for folder in start_menus:

            if not folder.exists():
                continue

            for shortcut in folder.rglob("*.lnk"):

                try:

                    target = shell.CreateShortcut(str(shortcut)).TargetPath

                    if not target:
                        continue

                    name = shortcut.stem.lower()

                    self.applications[name] = {
                    "name": shortcut.stem,
                    "path": target,
        }

                except Exception:
                    pass

    # =====================================================
    # Consultas
    # =====================================================

    def find_application(self, request: str):

        request = self.normalize_name(request)

        for key, application in self.applications.items():

            normalized_key = self.normalize_name(key)

            if normalized_key == request:
                return application

        return None

    def normalize_name(self, name: str) -> str:
        return (
            name
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )