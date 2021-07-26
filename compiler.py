import shutil
import PyInstaller.__main__ as pyinstaller
import os
from datetime import datetime

AppDataPath = os.path.join(str(os.getenv('APPDATA')), "ArktPVC", "Matriisit Compiler")
BuildsPath = os.path.join(AppDataPath, "Builds")
os.makedirs(BuildsPath, exist_ok=True)
WorkPath = os.path.join(AppDataPath, "cache", "work")
CachePath = os.path.join(AppDataPath, "cache")
if os.path.isdir(CachePath):
    shutil.rmtree(CachePath)

parentDir = os.path.dirname(os.path.abspath(__file__))

BuildPath = os.path.join(BuildsPath, "build_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

def clearCache():
    if os.path.isdir(CachePath):
        print("Clearing cache...")
        shutil.rmtree(CachePath)


clearCache()

filename = "matriisit.py"
iconpath = "./assets/icon.ico"

pyinstaller.run([
    "--noconfirm",
    "--distpath",
    BuildPath,
    "--workpath",
    WorkPath,
    "--specpath",
    CachePath,
    "--windowed",
    "--icon",
    f"{parentDir}/{iconpath}",
    "--add-data",
    f"{parentDir}/assets;assets/",
    "--paths",
    f"{parentDir}/modules",
    f"{parentDir}/{filename}"
])

clearCache()

cutName = os.path.splitext(filename)[0]
print(f"Built {filename} at: \"" + os.path.join(BuildPath, cutName, f"{cutName}.exe") + "\"")
