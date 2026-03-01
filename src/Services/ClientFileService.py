import logging
import os
import platform
import subprocess



class ClientFileService:
    """
    Provides functionalities for interacting with files, including saving to disk, reading from disk, and
    selecting file paths via platform-specific dialogs.

    This class allows seamless handling of file operations while abstracting platform-specific behaviors
    such as file picker or file save dialogs, enabling cross-platform compatibility.
    """
    def __init__(self):
        pass

    def save_file_to_disk(self, path_to_save_to, file_name, file_contents):
        """
        Saves a file to a specified directory on the disk. If the specified directory
        does not exist, it will be created. The file contents can either be provided
        as a single binary object or as a list of binary chunks which will be combined
        into a single binary stream before saving.

        :param path_to_save_to: The directory path where the file will be saved.
        :type path_to_save_to: str
        :param file_name: The name of the file to be saved.
        :type file_name: str
        :param file_contents: The contents of the file to be written. Can be a binary
            object or a list of binary chunks.
        :type file_contents: Union[bytes, List[bytes]]
        :return: None
        :rtype: None
        """
        if len(path_to_save_to) == 0: return
        os.makedirs(path_to_save_to, exist_ok=True)
        file_bytes = b""
        if isinstance(file_contents, list):
            for chunk in file_contents:
                file_bytes += chunk
        else:
            file_bytes = file_contents
        with open(os.path.join(path_to_save_to, file_name), "wb") as file:
            logging.info(f"Writing file {file_name} to {path_to_save_to} on the disk.")
            file.write(file_bytes)
        logging.info(f"File {file_name} written to {path_to_save_to} on the disk.")


    def read_file_from_disk(self, full_file_path):
        """
        Reads the content of a file from the disk in binary mode.

        This method opens the specified file, reads its entire content in binary mode,
        and returns the content as bytes.

        :param full_file_path: The full absolute or relative path to the file to be opened and read.
        :type full_file_path: str
        :return: The binary content of the file.
        :rtype: bytes
        """
        with open(full_file_path, "rb") as file:
            file_contents = file.read(-1)
        return file_contents


    def file_picker_dialog(self):
        """
        Prompts the user to select a file via a file picker dialog appropriate for the operating system
        and returns the selected file's path. The method handles macOS and Windows-specific logic for
        file selection and logs the selected path. For unsupported operating systems, an exception
        is raised.

        :raises Exception: If the operating system is not supported.

        :return: The full path of the file selected by the user. Returns an empty string if no file
            is selected.
        :rtype: str
        """
        osv = platform.system()
        if osv == "Darwin":
            script = 'POSIX path of (choose file with prompt "Select a file")'
            path = subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()
            logging.info(f"File path picked: {path}")
            logging.info(f"Is path Empty? {path == ""}")
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

            logging.info(f"File path picked: {path if not path == "" else "Empty"}")
            return path
        else:
            raise Exception("Unsupported OS")

    def save_file_dialog(self, file_name):
        """
        Prompts the user with a save file dialog box specific to their operating system and
        returns the file path selected by the user.

        Supported operating systems:
        - macOS: Utilizes the AppleScript 'choose file name' dialog.
        - Windows: Uses PowerShell to invoke a Save File dialog.

        On unsupported operating systems, the method raises an exception.

        :param file_name: The default file name to be suggested in the save file dialog. Should be a string.
        :type file_name: str
        :return: The file path selected by the user as a string. If no file is selected, the function
            returns an empty string. Raises an exception on unsupported operating systems.
        :rtype: str
        """
        osv = platform.system()

        logging.info(f"OS: {osv}")
        logging.info(f"File name: {file_name}")

        if osv == "Darwin":
            script = f'POSIX path of (choose file name with prompt "Choose where to save `{file_name}` to:" default name "{file_name}")'
            path = subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()
            logging.info(f"File path picked: {path if path != "" else 'Empty'}")
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

            logging.info(f"File path picked: {path if not path == "" else 'Empty'}")
            return path
        else:
            raise Exception("Unsupported OS")
