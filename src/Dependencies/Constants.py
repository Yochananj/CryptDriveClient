import flet as ft

# Constants:

# Project Constants
app_name = "CryptDrive"
app_author = "YochananJulian"

# GUI Constants
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
server_address = input("Enter Server Address: ")
server_port = 8081
host_addr = (server_address, server_port)

buffer_size = 1024

