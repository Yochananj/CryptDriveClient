import flet as ft

from Dependencies.Constants import crypt_drive_blue, crypt_drive_blue_light, crypt_drive_purple


class HomeView:
    def __init__(self, window_height, window_width):
        self.nav_rail = ft.NavigationRail(
            label_type=ft.NavigationRailLabelType.SELECTED,
            min_width=100,
            group_alignment=-1,
            selected_label_text_style=ft.TextStyle(font_family="Aeonik Bold", size=16, color=crypt_drive_blue),
            selected_index=0,

            leading = ft.Container(
                content=ft.Image(
                    src="icon.png",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.FIT_WIDTH,
                ),
                url="https://github.com/Yochananj/CyberFinalProject",
                tooltip="About CryptDrive (Click)"
            ),

            destinations=[
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
                    label="Settings",
                    selected_icon=ft.Icon(ft.Icons.SETTINGS, color=crypt_drive_purple),
                    icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=crypt_drive_purple)
                )
            ]
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
            duration=400,
            reverse_duration=400,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
        )


    def build(self):
        return ft.View(route="/home",
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

def test(page: ft.Page):
    page.views.append(
        HomeView(page.window.height, page.window.width).build()
    )
    page.update()

if __name__ == "__main__":
    ft.app(test)