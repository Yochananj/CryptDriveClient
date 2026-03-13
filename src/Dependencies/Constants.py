"""
Module providing constants for the CryptDrive application.

This module defines various constants that are used throughout the
CryptDrive application for managing GUI elements, application metadata,
encryption flags, and network configurations.

Constants:
    app_name (str): The name of the application.
    app_author (str): The author of the application.

    title_size (int): Font size for the application title.

    crypt_drive_blue_light (str): Hex color code for light blue theme.
    crypt_drive_blue_semilight (str): Hex color code for semilight blue theme.
    crypt_drive_blue_medium_light (str): Hex color code for medium-light blue theme.
    crypt_drive_blue_medium (str): Hex color code for medium blue theme.
    crypt_drive_purple (str): Hex color code for purple theme.
    crypt_drive_blue (str): Hex color code for primary blue theme.
    crypt_drive_theme (ft.Theme): GUI theme configuration.

    crypt_drive_fonts (dict): Dictionary mapping font names to file paths.

    separator (str): Separator used in the application.
    byte_data_flag (bytes): Marker for byte data flag.
    string_data_flag (bytes): Marker for string data flag.
    end_flag (bytes): Marker for the end of data.

    init_flag (bytes): Marker for initializing encryption.
    resume_flag (bytes): Marker for resuming encryption.
    encryption_separator (bytes): Separator used in encryption operations.

    server_address (str): Host address for the server.
    server_port (int): Port number for the server.
    host_addr (tuple): Tuple containing the server's address and port.

    buffer_size (int): Size of the network buffer for data transfers.
"""

import flet as ft

# Constants:

# Project Constants
app_name = "CryptDrive"
app_author = "YochananJulian"

# GUI Constants
title_size = 69

crypt_drive_blue_light = "#E6E8FE"
crypt_drive_blue_semilight = "#CDD2FE"
crypt_drive_blue_medium_light = "#B4BBFC"
crypt_drive_blue_medium = "#9BA5FB"
crypt_drive_purple = "#4A5086"
crypt_drive_blue = "#3043FB"
crypt_drive_theme = ft.Theme(color_scheme_seed=crypt_drive_blue, font_family="Aeonik", floating_action_button_theme=ft.FloatingActionButtonTheme(foreground_color=crypt_drive_purple))

crypt_drive_fonts = {
    "Aeonik": f"Aeonik/AeonikExtendedLatinHebrew-Regular.otf",
    "Aeonik Bold": f"Aeonik/AeonikExtendedLatinHebrew-Bold.otf",
    "Aeonik Black": f"Aeonik/AeonikExtendedLatinHebrew-Black.otf",
    "Aeonik Thin": f"Aeonik/AeonikExtendedLatinHebrew-Thin.otf"
}

# Flags
separator = "|||"
byte_data_flag = b"||| BYTE DATA |||"
string_data_flag = b"||| STRING DATA |||"
end_flag = b"||| END |||"

# Encryption Flags
init_flag = b"(&) INIT (&)"
resume_flag = b"(&) RESUME (&)"
encryption_separator = b"(&) SEP (&)"

# Common Constants
server_address = "localhost"
server_port = 8081
host_addr = (server_address, server_port)

buffer_size = 1024

