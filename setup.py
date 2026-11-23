from cx_Freeze import setup, Executable

# O comando solicitado na atividade e: python setup.py build
opcoes = {
    "build_exe": {
        "packages": ["pygame", "pyttsx3", "Recursos"],
        "include_files": [
            ("bases", "bases"),
            ("log.dat", "log.dat"),
        ],
    }
}

setup(
    name="OmnitrixRun",
    version="7.0",
    description="Jogo Pygame - Omnitrix Run V7",
    options=opcoes,
    executables=[Executable("main.py", target_name="OmnitrixRun.exe")],
)
