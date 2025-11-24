import logging
import os
import platform
import subprocess

if platform.system() == "Windows":
    import win32ui
    from win32com.shell import shell, shellcon


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


    def file_picker(self):
        osv = platform.system()
        if osv == "Darwin":
            script = 'POSIX path of (choose file with prompt "Select a file")'
            path = subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()
            logging.debug(f"File path picked: {path}")
            logging.debug(f"Is path Empty? {path == ""}")
            return path
        elif osv == "Windows":
            dlg = win32ui.CreateFileDialog(1)  # 1 = open, 0 = save
            dlg.DoModal()
            path = dlg.GetPathName()
            logging.debug(f"File path picked: {path}")

            return path
        else:
            raise Exception("Unsupported OS")

    def dir_picker(self):
        osv = platform.system()
        if osv == "Darwin":
            script = 'POSIX path of (choose folder with prompt "Select a folder")'
            path = subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()
            logging.debug(f"File path picked: {path}")
            logging.debug(f"Is path Empty? {path == ""}")
            return path
        elif osv == "Windows":
            raise Exception("Not Implemented")
        else:
            raise Exception("Unsupported OS")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cfs = ClientFileService()
    cfs.dir_picker()