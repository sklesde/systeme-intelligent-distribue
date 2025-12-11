import subprocess
import time
import os

# Dossier où se trouvent server.py et agent.py
PROJECT_DIR = r"C:\Users\Seb\Desktop\Seb\Cours IPSA\A5\Systemes intelligents distribues\systeme-intelligent-distribue\In512_Project_Student-main"

def run_in_cmd(command):
    """
    Ouvre une nouvelle fenêtre cmd dans le bon dossier et lance la commande.
    /k = laisse la fenêtre ouverte après exécution.
    """
    subprocess.Popen(
        [
            "cmd.exe",
            "/k",
            f"cd /d {PROJECT_DIR} && {command}"
        ],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

# --- Lancement des programmes ---

# Serveur
run_in_cmd("python scripts/server.py -nb 2")

# Pause légère pour éviter collision de ressources
time.sleep(1)

# Agent 1
run_in_cmd("python scripts/agent.py")

# Agent 2
run_in_cmd("python scripts/agent.py")
