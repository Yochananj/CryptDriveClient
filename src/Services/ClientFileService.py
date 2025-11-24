import logging
import os
import platform
import subprocess



class ClientFileService:
    def __init__(self):
        pass

    def save_file_to_disk(self, path_to_save_to, file_name, file_contents):
        os.makedirs(path_to_save_to, exist_ok=True)
        file_bytes = b""
        if isinstance(file_contents, list):
            for chunk in file_contents:
                file_bytes += chunk
        else:
            file_bytes = file_contents
        with open(os.path.join(path_to_save_to, file_name), "wb") as file:
            logging.debug(f"Writing file {file_name} to {path_to_save_to} on the disk.")
            file.write(file_bytes)
        logging.debug(f"File {file_name} written to {path_to_save_to} on the disk.")


    def read_file_from_disk(self, full_file_path):
        with open(full_file_path, "rb") as file:
            file_contents = file.read(-1)
        return file_contents


    def file_picker_dialog(self):
        osv = platform.system()
        if osv == "Darwin":
            script = 'POSIX path of (choose file with prompt "Select a file")'
            path = subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()
            logging.debug(f"File path picked: {path}")
            logging.debug(f"Is path Empty? {path == ""}")
            return path
        elif osv == "Windows":
            ps_command = f"""
                [System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") | Out-Null
                $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog
                $OpenFileDialog.filter = "All Files (*.*)|*.*"
                $OpenFileDialog.ShowDialog() | Out-Null
                $OpenFileDialog.filename"""

            path = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
            ).stdout.strip()

            logging.debug(f"File path picked: {path if not path == "" else "Empty"}")
            return path
        else:
            raise Exception("Unsupported OS")

    def save_file_dialog(self, file_name):
        osv = platform.system()
        if osv == "Darwin":
            script = f'POSIX path of (choose file name with prompt "Choose where to save {file_name} to: default name {file_name}")'
            path = subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()
            logging.debug(f"File path picked: {path}")
            logging.debug(f"Is path Empty? {path == ""}")
            return path
        elif osv == "Windows":
            ps_command = f"""
                [System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") | Out-Null
                $SaveFileDialog = New-Object System.Windows.Forms.SaveFileDialog
                $SaveFileDialog.filter = "All Files (*.*)|*.*"
                $SaveFileDialog.AddExtension = $true
                $SaveFileDialog.FileName = "{file_name}" # Set the default file name here
                $SaveFileDialog.ShowDialog() | Out-Null
                $SaveFileDialog.filename"""

            path = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
            ).stdout.strip()

            logging.debug(f"File path picked: {path if not path == "" else 'Empty'}")
            return path
        else:
            raise Exception("Unsupported OS")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cfs = ClientFileService()
    cfs.save_file_dialog("jorkin depeanits")