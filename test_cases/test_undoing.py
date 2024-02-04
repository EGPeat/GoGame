from unittest.mock import patch, MagicMock
import unittest
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import uifunctions as ui
import PySimpleGUI as sg
import goclasses as go
import undoing as undo
import pygame
from player import Player


class TestClassPyTestUndoing:

    @pytest.fixture
    def mock_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value