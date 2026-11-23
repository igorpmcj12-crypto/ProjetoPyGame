from setuptools import setup

# Para gerar a build/executavel conforme o ambiente da disciplina:
# python setup.py build

try:
    from cx_Freeze import setup, Executable
    setup(
        name="OmnitrixRun",
        version="1.0",
        description="Jogo Pygame - Pensamento Computacional",
        options={
            "build_exe": {
                "packages": ["pygame", "pyttsx3", "Recursos"],
                "include_files": ["bases", "Recursos", "main.py"]
            }
        },
        executables=[Executable("main.py")]
    )
except ImportError:
    setup(
        name="OmnitrixRun",
        version="1.0",
        py_modules=["main"],
        description="Jogo Pygame - Pensamento Computacional"
    )
