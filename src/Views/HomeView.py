import flet as ft

from Dependencies.Constants import crypt_drive_blue, crypt_drive_blue_light, crypt_drive_purple


class HomeView:
    def __init__(self, window_height, window_width):
        self.destinations = [
            ft.NavigationRailDestination(
                label="Files",
                selected_icon=ft.Icon(ft.Icons.FOLDER, color=crypt_drive_purple),
                icon=ft.Icon(ft.Icons.FOLDER_OUTLINED, color=crypt_drive_purple)
            ),
            ft.NavigationRailDestination(
                label="Account",
                selected_icon=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=crypt_drive_purple),
                icon=ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=crypt_drive_purple)
            ),
            ft.NavigationRailDestination(
                label="About",
                selected_icon=ft.Icon(ft.Icons.INFO, color=crypt_drive_purple),
                icon=ft.Icon(ft.Icons.INFO_OUTLINE, color=crypt_drive_purple)
            )
        ]

        self.icon_container = ft.Container(
            content=ft.Image(
                src="icon.png",
                width=100,
                height=100,
                fit=ft.ImageFit.FIT_WIDTH,
            ),
        )

        self.nav_rail = ft.NavigationRail(
            label_type=ft.NavigationRailLabelType.SELECTED,
            min_width=100,
            group_alignment=-1,
            selected_label_text_style=ft.TextStyle(font_family="Aeonik Bold", size=16, color=crypt_drive_blue),
            selected_index=0,
            leading = self.icon_container,
            destinations=self.destinations
        )

        self.body = ft.Container(
            height=window_height,
            width=window_width - 130,
            content=[],
            expand=True,
            bgcolor=crypt_drive_blue_light,
            border_radius=10,
            padding=(ft.padding.only(left=30, right=30, top=0, bottom=0)),
            alignment=ft.Alignment(0,-1),
        )

        self.loading = ft.Container()

        self.home_view_animator = ft.AnimatedSwitcher(
            content=self.loading,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
        )


    def build(self):
        return ft.View(
                       route="/home",
                       controls=[
                           ft.Row(
                               controls=[
                                   self.nav_rail,
                                   self.home_view_animator
                               ],
                               expand=True
                           )
                       ],
                )
