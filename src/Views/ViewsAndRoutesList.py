"""
Enumeration representing various views and routes.

This class is a specialized enumeration that defines a set of constants
representing the names of commonly used views and routes within an
application. This can help maintain consistency in navigation and
route management.
"""

import enum

class ViewsAndRoutesList(enum.Enum):
    """
    Enumeration representing various views and routes.

    This class is a specialized enumeration that defines a set of constants
    representing the names of commonly used views and routes within an
    application. This can help maintain consistency in navigation and
    route management.

    :ivar HOME: Represents the "Home" view or route.
    :type HOME: str
    :ivar SIGN_UP: Represents the "Sign Up" view or route.
    :type SIGN_UP: str
    :ivar LOG_IN: Represents the "Log In" view or route.
    :type LOG_IN: str
    """
    HOME = "Home"
    SIGN_UP = "Sign Up"
    LOG_IN = "Log In"
