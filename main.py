"""
StudyDesk — Root Entry Point.
Directly invokes src.main:main for desktop and mobile builds.
"""
from src.main import main
import flet as ft

if __name__ == "__main__":
    ft.run(main)
