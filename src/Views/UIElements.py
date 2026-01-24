import logging

import flet as ft

from Dependencies.Constants import crypt_drive_blue_semilight, crypt_drive_purple, crypt_drive_blue_medium_light


class FileTile:
    def __init__(self, file_name, file_size):
        self.name = file_name
        self.size = file_size
        self.download = ft.IconButton(
            ft.Icons.FILE_DOWNLOAD_OUTLINED,
            tooltip="Download File"
        )
        self.rename = ft.IconButton(
            ft.Icons.EDIT,
            tooltip="Rename File"
        )
        self.move = ft.IconButton(
            ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
            tooltip="Move File"
        )
        self.delete = ft.IconButton(
            ft.Icons.DELETE,
            tooltip="Delete File"
        )
        self.tile = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INSERT_DRIVE_FILE),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls = [
                                    ft.Text(self.name, font_family="Aeonik Bold", size=20),
                                    ft.Text(f"Size: {self.size} bytes", font_family="Aeonik", size=16)
                                ],
                                height=40,
                                expand = False
                            )
                        ], expand = True
                    ),
                    self.download,
                    self.move,
                    self.rename,
                    self.delete,
                ],
                expand=False
            ),
            border_radius=10,
            bgcolor=crypt_drive_blue_semilight,
            padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
            expand=False
        )


class FolderTile:
    def __init__(self, path, item_count, compact_tile=False, regular_folder_icon=False, hide_path=False):
        self.name = path.split("/")[-1]

        if self.name == "":
            self.path = "/"
        else:
            self.path = path[:-len(self.name)]

        self.items = item_count
        self.parent_icon = ft.Icons.DRIVE_FOLDER_UPLOAD_ROUNDED
        self.tooltip = "Click to return to Parent Folder"
        self.is_root = False

        self.move = ft.IconButton(
            ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
            tooltip="Move File"
        )
        self.rename = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Rename Folder"
        )
        self.delete = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Delete Folder"
        )

        if self.path == "/" and self.name == "":
            self.is_root = True
            self.parent_icon = ft.Icons.HOME_ROUNDED
            self.tooltip = "Already at root folder"

        if regular_folder_icon: self.parent_icon = ft.Icons.FOLDER_ROUNDED


        if compact_tile:
            self.tile=ft.FloatingActionButton(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(self.parent_icon, color=crypt_drive_purple),
                            ft.Text(self.path if not hide_path else "", font_family="Aeonik Bold" if not self.is_root else "Aeonik Black", size=20),
                            ft.Text(self.name, font_family="Aeonik Black", size=20)
                        ],
                    ),
                    tooltip=self.tooltip,
                    border_radius=10,
                    bgcolor=crypt_drive_blue_semilight,
                    padding=ft.padding.all(10),
                    expand=True,
                ),
                bgcolor=crypt_drive_blue_semilight,
                elevation=0,
                expand=True,
                height=50,
            )
            if self.is_root:
                self.tile.disabled = True
        else:
            self.tile = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FOLDER),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(self.name, font_family="Aeonik Bold", size=20),
                                        ft.Text(f"{self._get_items_string(self.items)}", font_family="Aeonik", size=16)
                                    ],
                                    height=40,
                                    expand=False
                                )
                            ],
                            expand=True,
                        ),
                        self.move,
                        self.rename,
                        self.delete,
                    ],
                    expand=False
                ),
                border_radius=10,
                bgcolor=crypt_drive_blue_semilight,
                padding=ft.padding.only(left=10, right=10, top=10, bottom=12),
                tooltip="Click to open folder",
            )

    def _get_items_string(self, item_count: int):
        if item_count == 1:
            return "1 item"
        else:
            return f"{item_count} items"


def error_alert(error_message: str):
    return ft.SnackBar(
        duration=5000,
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.CLOSE_ROUNDED, color=ft.Colors.RED),
                      ft.Text(error_message, color=ft.Colors.RED)],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        behavior=ft.SnackBarBehavior.FLOATING,
        bgcolor=ft.Colors.RED_100,
        shape=ft.ContinuousRectangleBorder(radius=10),
        margin=ft.margin.all(10),
    )

def success_alert(success_message: str):
    return ft.SnackBar(
        duration=5000,
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.CHECK_ROUNDED, color=ft.Colors.GREEN),
                      ft.Text(success_message, color=ft.Colors.GREEN)],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        behavior=ft.SnackBarBehavior.FLOATING,
        bgcolor=ft.Colors.GREEN_100,
        shape=ft.ContinuousRectangleBorder(radius=10),
        margin=ft.margin.all(10),
    )


class TextFieldAlertDialog:
    def __init__(
            self,
            page: ft.Page,
            title: str,
            title_icon: ft.Icons,
            subtitle: str,
            text_fields: list[str],
            modal: bool = False,
            password_fields: bool = False
            ):

        self.text_fields = ft.Column(
            controls=[],
        )

        for i in range(len(text_fields)):
            self.text_fields.controls.append(ft.TextField(label=text_fields[i], password=password_fields))

        self.content = ft.Container(
            content=
            ft.Column(
                controls=[
                    ft.Text(subtitle, font_family="Aeonik"),
                    self.text_fields
                ],
            ),
            alignment=ft.Alignment(0,0),
            width=400,
            height = 90 + 50 * (len(text_fields) - 1),
        )
        self.alert = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(title_icon, color=crypt_drive_purple),
                ft.Text(title, font_family="Aeonik Bold")
                ],
            ),
            modal=modal,
            content=self.content,
            bgcolor=crypt_drive_blue_semilight,

        )
        self.cancel = ft.TextButton(text="Cancel", on_click=lambda e: page.close(self.alert))
        self.confirm = ft.TextButton(text="Confirm", disabled=True)
        self.alert.actions=[self.cancel, self.confirm]

        for text_field in self.text_fields.controls:
            text_field.on_change = lambda e: self._update_confirm_button_status()

    def set_on_confirm_method(self, method):
        self.confirm.on_click = method

    def get_text_field_values(self) -> list[str]:
        return [text_field.value for text_field in self.text_fields.controls]

    def _update_confirm_button_status(self):
        self.confirm.disabled = not self._do_all_text_fields_have_a_value()
        self.alert.update()

    def _do_all_text_fields_have_a_value(self):
        for text_field in self.text_fields.controls:
            if text_field.value == "":
                return False
        else:
            return True


class CancelConfirmAlertDialog:
    def __init__(
            self,
            page: ft.Page,
            title: str,
            title_icon: ft.Icons,
            subtitle: str,
            modal=False):

        self.alert = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(title_icon, color=crypt_drive_purple),
                ft.Text(title, font_family="Aeonik Bold")
            ]),
            modal=modal,
            content=ft.Container(ft.Text(subtitle, font_family="Aeonik"), width=500, expand=False),
            bgcolor=crypt_drive_blue_semilight,

        )
        self.cancel = ft.TextButton(text="Cancel", on_click=lambda e: page.close(self.alert))
        self.confirm = ft.TextButton(text="Confirm")
        self.alert.actions = [self.cancel, self.confirm]


    def set_on_confirm_method(self, method):
        self.confirm.on_click = method

class FolderPickerAlertDialog:
    def __init__(self, page: ft.Page, title: str, subdirectories, current_dialog_dir, selected_dir_on_click_method, on_confirm_method):

        self.current_dir = FolderTile(current_dialog_dir, 0, True, False)
        self.current_dir.tile.disabled = False
        self.dir_list: list[FolderTile] = [self.current_dir]

        for directory in subdirectories:
            self.dir_list.append(FolderTile(directory, 0, True, True, hide_path=True))

        rows_list = []
        for directory in self.dir_list:
            rows_list.append(ft.Row(controls=[directory.tile]))

        self.subtitle=ft.Text(f"Selected folder: {self.current_dir.path + self.current_dir.name}", font_family="Aeonik")
        self.alert = ft.AlertDialog(
            title=ft.Column(
                [ft.Row([ft.Icon(ft.Icons.DRIVE_FILE_MOVE_ROUNDED, color=crypt_drive_purple), ft.Text(title, font_family="Aeonik Bold")]), self.subtitle]
            ),
            modal=False,
            content=ft.Container(
                content=ft.Column(
                    controls=rows_list,
                    scroll=True,
                ),
                width=600,
                padding=ft.padding.all(10),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            bgcolor=crypt_drive_blue_semilight,
        )
        self.cancel = ft.TextButton(text="Cancel", on_click=lambda e: page.close(self.alert))
        self.confirm = ft.TextButton(text="Confirm", on_click=on_confirm_method)
        self.alert.actions = [self.cancel, self.confirm]

        self.selected_dir: FolderTile = self.current_dir
        self.selected_dir_on_click_method = selected_dir_on_click_method
        self._update_selected_dir(self.current_dir)

    def _update_selected_dir(self, directory: FolderTile):
        logging.debug(f"Selected dir: {directory.__dict__}")
        self.selected_dir = directory
        for folder_tile in self.dir_list:
            if folder_tile == self.selected_dir:
                folder_tile.tile.content.bgcolor = crypt_drive_blue_medium_light
                folder_tile.tile.on_click = self.selected_dir_on_click_method
                self.subtitle.value = f"Selected folder: {self.selected_dir.path + self.selected_dir.name}"
            else:
                folder_tile.tile.content.bgcolor = crypt_drive_blue_semilight
                folder_tile.tile.on_click = lambda e, folder_tile_instance=folder_tile: self._update_selected_dir(folder_tile_instance)
        if self.alert.page:
            self.alert.update()

    def get_selected_directory_path_for_dialogs(self):
        logging.debug(f"RETURNING SELECTED DIR: {self.selected_dir.__dict__}")
        if self.selected_dir == self.current_dir:
            trt = self.selected_dir.path if self.selected_dir.path == "/" else self.selected_dir.path[:-1] if self.selected_dir.path[-1] == "/" else self.selected_dir.path
        else:
            trt = self.selected_dir.path + self.selected_dir.name
        logging.debug(f"TO RETURN STRING: {trt}")
        return trt

    def get_selected_directory_path_for_comms(self):
        logging.debug(f"RETURNING SELECTED DIR: {self.selected_dir.__dict__}")
        trt = self.selected_dir.path + self.selected_dir.name
        logging.debug(f"TO RETURN STRING: {trt}")
        return trt

