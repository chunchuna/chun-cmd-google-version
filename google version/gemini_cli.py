import os
import configparser
from colorama import Fore, Back, init
import subprocess
import sys
import pkg_resources
import time
import random
import google.generativeai as genai

# Initialize colorama
init(autoreset=True)

CONFIG_FILE = "config.ini"
MODELS_FILE = "available_models.txt"
HCK_DIR = "hck"
HCK_COMMAND_FILE = os.path.join(HCK_DIR, "command.txt")
RGB_FILE = "rgb.ini"
REQUIRED_LIBRARIES = ["google.generativeai", "colorama"]
INSTALLED_MARKER = ".installed"

def get_rgb_color_code(rgb_string):
    """Converts a comma-separated RGB string to a color code."""
    try:
        r, g, b = map(int, rgb_string.split(','))
        return f"\033[38;2;{r};{g};{b}m"
    except ValueError:
        return None


def get_rgb_bg_color_code(rgb_string):
    """Converts a comma-separated RGB string to a background color code."""
    try:
        r, g, b = map(int, rgb_string.split(','))
        return f"\033[48;2;{r};{g};{b}m"
    except ValueError:
        return None


def create_default_rgb_config():
    """Creates default RGB config file."""
    rgb_config = configparser.ConfigParser()
    rgb_config["colors"] = {
        "blue_fg": "0,0,255",  # Default Blue foreground
        "green_fg": "0,255,0",  # Default Green foreground
        "yellow_fg": "255,255,0",  # Default Yellow foreground
        "cyan_fg": "0,255,255",  # Default Cyan foreground
        "magenta_fg": "255,0,255",  # Default Magenta foreground
        "blue_bg": "0,0,0",  # Default blue background
    }
    with open(RGB_FILE, "w") as f:
        rgb_config.write(f)
    print(f"Default RGB configuration file created: {RGB_FILE}")
    return rgb_config


def load_rgb_config():
    """Loads RGB configuration file, creates if not exists."""
    rgb_config = configparser.ConfigParser()
    if not os.path.exists(RGB_FILE):
        print(f"RGB configuration file not found: {RGB_FILE}, creating default...")
        rgb_config = create_default_rgb_config()
    else:
        rgb_config.read(RGB_FILE)
    return rgb_config


def blue_print(text, rgb_config=None):
    """Prints text in a specified color (or blue if no color is specified)."""
    if rgb_config:
        blue_fg = rgb_config.get("colors", "blue_fg", fallback="0,0,255")
        blue_bg = rgb_config.get("colors", "blue_bg", fallback="0,0,0")
        color_code = get_rgb_color_code(blue_fg)
        bg_color_code = get_rgb_bg_color_code(blue_bg)
        print(f"{bg_color_code}{color_code}{text}\033[0m")  # Added background color and reset
    else:
        print(Fore.BLUE + text)


def check_and_install_libraries():
    """Checks and installs required libraries if not present using pkg_resources."""
    if os.path.exists(INSTALLED_MARKER):
        blue_print("Libraries are already installed, skipping installation check.")
        return
    missing_libraries = []
    for lib in REQUIRED_LIBRARIES:
        try:
            pkg_resources.get_distribution(lib)
        except pkg_resources.DistributionNotFound:
            missing_libraries.append(lib)

    if missing_libraries:
        blue_print("The following required libraries are missing:")
        for lib in missing_libraries:
            blue_print(f"- {lib}")
        blue_print("Installing missing libraries...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_libraries])
            blue_print("Libraries installed successfully.")
            # Create a marker file to indicate that the libraries are installed
            open(INSTALLED_MARKER, "w").close()
            blue_print("Please restart the program to ensure changes take effect.")
            sys.exit(0)  # Exit after installation, user needs to restart
        except subprocess.CalledProcessError as e:
            blue_print(f"Error installing libraries: {e}")
            sys.exit(1)  # Exit if installation fails
    else:
        blue_print("All required libraries are installed.")

def create_default_config():
    """Creates default configuration file."""
    config = configparser.ConfigParser()
    config["gemini"] = {
        "model": "gemini-pro",
        "api_key": "",  # API key needs to be entered
        "temperature": "0.9",
        "top_k": "40",
        "top_p": "0.9",
        "hack": "true",  # New hack option
    }
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
    blue_print(f"Default configuration file created: {CONFIG_FILE}")


def load_config():
    """Loads configuration file, creates if not exists."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        blue_print(f"Configuration file not found: {CONFIG_FILE}, creating default...")
        create_default_config()
    config.read(CONFIG_FILE)
    return config


def save_config(config):
    """Saves configuration file."""
    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def get_api_key(config):
    """Retrieves API key from config."""
    api_key = config.get("gemini", "api_key").strip()
    if not api_key:
        blue_print("Error: API key is empty! Please configure using 'setting' command.")
    return api_key


def list_and_save_models(api_key, rgb_config):
    """Lists available models and saves to file."""
    if not api_key:
        return
    genai.configure(api_key=api_key)

    try:
        with open(MODELS_FILE, "w", encoding="utf-8") as f:
            f.write("Available Models:\n")
            f.write("------------------\n")
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    f.write(f"Model Name: {m.name}\n")
                    if m.name == "gemini-1.5-flash":
                        f.write("  Limitations: 1500 RPM (requests per minute)\n")
                        f.write("  Pricing: Input and output are free\n")
                    elif m.name == "gemini-1.5-pro":
                        f.write("  Limitations: 2 RPM (requests per minute)\n")
                        f.write("        32,000 TPM (tokens per minute)\n")
                        f.write("        50 RPD (requests per day)\n")
                    else:
                        f.write("  Limitations: Please refer to official documentation\n")
                    f.write("------------------\n")
            blue_print(f"Model list saved to: {MODELS_FILE}", rgb_config)
    except Exception as e:
        blue_print(f"Error listing models: {e}", rgb_config)


def simulate_downloading(duration=3, rgb_config=None):
    """Simulates downloading with a progress bar."""
    cyan_fg = rgb_config.get("colors", "cyan_fg", fallback="0,255,255")
    color_code = get_rgb_color_code(cyan_fg)
    
    animation_chars = ['[=     ]', '[ =    ]', '[  =   ]', '[   =  ]', '[    = ]', '[     =]']
    for i in range(101):
        time.sleep(duration / 100)
        progress_bar = animation_chars[i%len(animation_chars)]
        print(f"\r{color_code}Downloading... {progress_bar} {i}%{Fore.RESET}", end="")
    print()  # Add a newline after the progress bar finishes
    blue_print("Download complete.", rgb_config)


def simulate_loading(duration=3, rgb_config=None):
    """Simulates loading with a simple animation."""
    magenta_fg = rgb_config.get("colors", "magenta_fg", fallback="255,0,255")
    color_code = get_rgb_color_code(magenta_fg)
    
    loading_patterns = [
        "  [-----]   ",
        "  [-====]   ",
        "  [==--=]   ",
        "  [===--]   ",
        "  [====-]   ",
        "  [-----]   ",
        "   [--=--]   ",
        "   [---=--]   ",
        "   [----=-]   ",
        "   [-----=]   ",
    ]
    start_time = time.time()
    current_pattern_index = 0
    while (time.time() - start_time) < duration:
        print(f"\r{color_code}Loading... {loading_patterns[current_pattern_index % len(loading_patterns)]}  {Fore.RESET}", end="",
              flush=True)
        time.sleep(0.1)
        current_pattern_index += 1
    print("\rLoading complete.          ")


def read_prep_command():
    """Reads the preparation command from the file."""
    if not os.path.exists(HCK_COMMAND_FILE):
        blue_print("Error: hck command file not found.")
        return None
    try:
        with open(HCK_COMMAND_FILE, "r", encoding="utf-8") as f:
            command = f.read().strip()
        return command
    except Exception as e:
        blue_print(f"Error reading hck command file: {e}")
        return None


def start_gemini_interaction(config, rgb_config, prep_command=None):
    """Starts AI interaction, now with dialog history"""
    api_key = get_api_key(config)
    if not api_key:
        return

    genai.configure(api_key=api_key)
    model_name = config.get("gemini", "model", fallback="gemini-pro")
    temperature = config.getfloat("gemini", "temperature", fallback=0.9)
    top_k = config.getint("gemini", "top_k", fallback=40)
    top_p = config.getfloat("gemini", "top_p", fallback=0.9)

    model = genai.GenerativeModel(model_name)
    blue_print("Successfully connected to the model!", rgb_config)
    green_fg = rgb_config.get("colors", "green_fg", fallback="0,255,0")
    yellow_fg = rgb_config.get("colors", "yellow_fg", fallback="255,255,0")

    user_color_code = get_rgb_color_code(green_fg)
    gemini_color_code = get_rgb_color_code(yellow_fg)
    
    # Initialize dialog history
    dialog_history = []
    
    if prep_command:
         dialog_history.append({"role": "user", "parts": [prep_command]})
    
    while True:
        user_input = input(f"{user_color_code}user&//: \033[0m")
        if user_input.lower() == "exit":
            blue_print("Program exited.", rgb_config)
            break
            
        dialog_history.append({"role": "user", "parts": [user_input]})

        try:
            response = model.generate_content(
                dialog_history,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature, top_k=top_k, top_p=top_p
                ),
            )
            dialog_history.append({"role": "model", "parts": [response.text]})
            print(f"\n{gemini_color_code}//chun.com&: \033[0m{response.text}")
        except Exception as e:
            blue_print(f"Error: {e}", rgb_config)
            

def setting_mode(config, rgb_config):
    """Configuration mode, allows users to view and modify settings."""
    while True:
        blue_print("\n=== Setting Mode ===", rgb_config)
        blue_print("1. View Current Settings", rgb_config)
        blue_print("2. Modify Setting", rgb_config)
        blue_print("3. Save and Exit", rgb_config)
        blue_print("4. Exit Without Saving", rgb_config)
        choice = input("Select operation: ")

        if choice == "1":
            blue_print("\nCurrent Settings:", rgb_config)
            for key, value in config.items("gemini"):
                print(f"  {key}: {value}")

            blue_print("\nRGB Settings:", rgb_config)
            for key, value in rgb_config.items("colors"):
                print(f"  {key}: {value}")

        elif choice == "2":
            setting_type = input(
                "Enter 'gemini' to modify gemini settings or 'rgb' to modify rgb settings: "
            ).strip().lower()
            if setting_type == "gemini":
                key = input(
                    "Enter setting to modify (e.g., model, api_key, temperature, top_k, top_p, hack): "
                ).strip()
                if key in config["gemini"]:
                    new_value = input(f"Enter new value for {key}: ").strip()
                    config["gemini"][key] = new_value
                    blue_print("Setting modified.", rgb_config)
                else:
                    blue_print("Invalid setting.", rgb_config)

            elif setting_type == "rgb":
                key = input(
                    "Enter rgb setting to modify (e.g., blue_fg, green_fg, yellow_fg, cyan_fg, magenta_fg, blue_bg): "
                ).strip()
                if key in rgb_config["colors"]:
                    new_value = input(f"Enter new value for {key} (e.g., 255,255,255): ").strip()
                    rgb_config["colors"][key] = new_value
                    blue_print("RGB setting modified.", rgb_config)
                else:
                    blue_print("Invalid setting.", rgb_config)
            else:
                blue_print("Invalid setting type.", rgb_config)

        elif choice == "3":
            save_config(config)
            with open(RGB_FILE, "w") as f:
                rgb_config.write(f)
            blue_print("Settings saved, exiting setting mode.", rgb_config)
            break
        elif choice == "4":
            blue_print("Exiting setting mode, changes not saved.", rgb_config)
            break
        else:
            blue_print("Invalid choice, please try again.", rgb_config)


def main():
    check_and_install_libraries()
    config = load_config()
    rgb_config = load_rgb_config()

    api_key = get_api_key(config)
    list_and_save_models(api_key, rgb_config)

    hack_enabled = config.getboolean("gemini", "hack", fallback=True)

    prep_command = None
    if hack_enabled:
        simulate_downloading(random.uniform(1.5, 3.5), rgb_config)
        simulate_loading(random.uniform(1, 3), rgb_config)
        prep_command = read_prep_command()
    if api_key:
         start_gemini_interaction(config, rgb_config, prep_command)

    while True:
        command = input(
            "Enter command ('setting' for settings, 'exit' to quit): "
        ).strip().lower()
        if command == "setting":
            setting_mode(config, rgb_config)
        elif command == "exit":
            blue_print("Program exited.", rgb_config)
            break
        else:
            blue_print("Invalid command, please try again.", rgb_config)


if __name__ == "__main__":
    main()