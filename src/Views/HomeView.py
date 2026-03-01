import flet as ft

from Dependencies.Constants import crypt_drive_blue, crypt_drive_blue_light, crypt_drive_purple


class HomeView:
    """
    Represents the home view of the application.

    This class is responsible for rendering the home screen's user interface, including
    navigation rail, main content area, and transitions within the home view. It organizes
    and manages the layout and visual elements specific to the home view of the application.

    :ivar destinations: Contains the navigation destinations for the navigation rail.
        Each destination has a label, selected icon, and unselected icon.
    :type destinations: list[ft.NavigationRailDestination]
    :ivar icon_container: A container for displaying the application's icon image.
    :type icon_container: ft.Container
    :ivar nav_rail: The navigation rail component, which includes navigation destinations,
        styling, and alignment.
    :type nav_rail: ft.NavigationRail
    :ivar body: The main content area container for the home view.
        This container encompasses the central UI elements.
    :type body: ft.Container
    :ivar loading: An empty container serving as a placeholder during transitions or loading states.
    :type loading: ft.Container
    :ivar home_view_animator: An animated switcher responsible for managing content transitions
        within the home view.
    :type home_view_animator: ft.AnimatedSwitcher
    """
    def __init__(self, window_height, window_width):
        """
        Initializes and configures the user interface components for the application.

        This class sets up the main navigation rail with multiple destinations, a customizable
        icon container at the top, and a content body. It also includes an animated switcher
        for seamless transitions between views. The configuration supports flexible window
        dimensions, ensuring adaptability across different screen sizes, while maintaining
        aesthetic alignment and spacing.

        :param window_height: Integer value representing the height of the application window.
        :param window_width: Integer value representing the width of the application window.
        """
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
        """
        Builds and returns the primary layout view of the application.

        This method constructs and organizes the main user interface elements, including
        a navigation rail and an animated home view, into a flexible and responsive
        layout. The elements are arranged within a `Row` control to ensure that they
        expand properly to fill the allocated space.

        :returns: The top-level view of the application's primary layout.
        :rtype: View
        """
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
