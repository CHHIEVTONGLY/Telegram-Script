from cx_Freeze import setup, Executable

# Define the executable, including target_name for custom naming
executable = Executable(
    script="main.py",  # Your Python script
    base=None,  # For GUI apps, you might use "Win32GUI"
    icon=r"C:\\Users\\Admin\\Downloads\\tg.ico",  # Path to your icon file
    target_name="Telegram Script by LCT.exe"  # The desired output executable name
)

# Setup configuration
setup(
    name="Telegram Script by LCT",
    version="2.9",
    description="Telegram Script by LCT",
    executables=[executable]  # Use the executable object here
)
