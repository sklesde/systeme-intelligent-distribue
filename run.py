import subprocess
import time
import os

# Dossier où se trouvent server.py et agent.py
PROJECT_DIR = r"C:\Users\Seb\Desktop\Seb\Cours IPSA\A5\Systemes intelligents distribues\systeme-intelligent-distribue\In512_Project_Student-main"
PROJECT_DIR=r"C:\Users\Blandine1\Documents\Travail_IPSA\A5\SII\In512_Project_Student\systeme-intelligent-distribue-Version_fonctionnelle_2_3_et_4_robots\In512_Project_Student-main"


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
n=2
run_in_cmd("py -3 scripts/server.py -nb "+str(n))

# Pause légère pour éviter collision de ressources
time.sleep(3)

for i in range(n):
    # Agent 1
    run_in_cmd("py -3 scripts/agent.py")



