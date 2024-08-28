import os
import shutil

def create_config_file():
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, 'BitaxeBot')
    config_file_path = os.path.join(config_dir, 'config.ini')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Path to the default config template in the package
    default_config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    if not os.path.isfile(config_file_path):
        if os.path.isfile(default_config_path):
            shutil.copy(default_config_path, config_file_path)
            print(f"Config file created at {config_file_path}")
        else:
            print(f"Warning: Default config file template not found at {default_config_path}.")
    else:
        print(f"Config file already exists at {config_file_path}.")
        new_config_copy_path = os.path.join(config_dir, 'config.ini.new')
        if os.path.isfile(default_config_path):
            shutil.copy(default_config_path, new_config_copy_path)
            print(f"A copy of the shipped config.ini has been saved as {new_config_copy_path}")
        else:
            print(f"Warning: Default config file template not found at {default_config_path}.")

if __name__ == "__main__":
    create_config_file()
