"""
Flet launcher used by flet run from the project root.
Shouldn't contain any code nor ran directly, its purpose is to be discovered by the flet run command.
"""

# Import the main entry point from garum.gui.app
from garum.gui.app import main

if __name__ == "__main__":
    main()
