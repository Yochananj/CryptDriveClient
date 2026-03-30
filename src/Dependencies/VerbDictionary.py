"""
An enumeration representing various user actions as verbs.

This module defines the `Verbs` enumeration, which serves as a list of constants representing actions
that users can perform in an application. These actions primarily involve user authentication, file and
directory management, and updating user settings. Each enumeration value represents a specific action
or verb and is associated with the relevant context or parameters where applicable.
"""


import enum

class Verbs(enum.Enum):
    """
    A class representing different types of user actions that can be performed as enumerated values.

    This class is designed as an enumeration for actions such as signing up, logging in, file management
    (create, delete, rename, move), directory management, and user information updates. Each enumeration
    value corresponds to a specific action or verb and includes associated parameters as comments for
    reference, describing the inputs associated with each action.

    :ivar SIGN_UP: Represents the action of signing up a user with credentials and an encrypted file master key.
    :type SIGN_UP: str
    :ivar LOG_IN: Represents the action of logging in a user with a username and password hash.
    :type LOG_IN: str
    :ivar CREATE_FILE: Represents the action of creating a file, specifying its path, name, and optional contents.
    :type CREATE_FILE: str
    :ivar CREATE_DIR: Represents the action of creating a directory at a specified location.
    :type CREATE_DIR: str
    :ivar DOWNLOAD_FILE: Represents the action of downloading a file using its file path and name.
    :type DOWNLOAD_FILE: str
    :ivar DELETE_FILE: Represents the action of deleting a file, given its path and name.
    :type DELETE_FILE: str
    :ivar DELETE_DIR: Represents the action of deleting a directory at a specified path and name.
    :type DELETE_DIR: str
    :ivar GET_ITEMS_LIST: Represents the action of retrieving a list of items (files and directories) at a specific path.
    :type GET_ITEMS_LIST: str
    :ivar RENAME_FILE: Represents the action of renaming a file at a specific path, specifying the old and new names.
    :type RENAME_FILE: str
    :ivar RENAME_DIR: Represents the action of renaming a directory at a specific path, specifying the old and new names.
    :type RENAME_DIR: str
    :ivar MOVE_FILE: Represents the action of moving a file from an old to a new path, specifying the file name.
    :type MOVE_FILE: str
    :ivar MOVE_DIR: Represents the action of moving a directory from an old to a new path, specifying the directory name.
    :type MOVE_DIR: str
    :ivar CHANGE_USERNAME: Represents the action of changing the username for a user.
    :type CHANGE_USERNAME: str
    :ivar CHANGE_PASSWORD: Represents the action of changing the password and related security fields for a user.
    :type CHANGE_PASSWORD: str
    """
    SIGN_UP = "SIGN_UP" # [username, password, salt, encrypted_file_master_key, nonce]
    LOG_IN = "LOG_IN" # [username, password]
    CREATE_FILE = "CREATE_FILE" # [file_path, file_name, nonce] [file_contents]
    CREATE_DIR = "CREATE_DIR" # [path, dir_name]
    DOWNLOAD_FILE = "DOWNLOAD_FILE" # [file_path, file_name]
    DELETE_FILE = "DELETE_FILE" # [file_path, file_name]
    DELETE_DIR = "DELETE_DIR" # [path, dir_name]
    GET_ITEMS_LIST = "GET_ITEMS_LIST" # [path]
    RENAME_FILE = "RENAME_FILE" # [file_path, old_file_name, new_file_name]
    RENAME_DIR = "RENAME_DIR" # [path, old_dir_name, new_dir_name]
    MOVE_FILE = "MOVE_FILE" # [old_file_path, new_file_path, file_name]
    MOVE_DIR = "MOVE_DIR" # [old_dir_path, new_dir_path, dir_name]
    CHANGE_USERNAME = "CHANGE_USERNAME" # [new_username, password]
    CHANGE_PASSWORD = "CHANGE_PASSWORD" # [old_password, new_password, new_salt, new_encrypted_file_master_key, new_nonce]
    REFRESH_ACCESS_TOKEN = "REFRESH_ACCESS_TOKEN"