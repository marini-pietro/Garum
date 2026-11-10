:: Execute this script to populate the database with mock data for testing purposes.
:: There should already be a database created with the db.sql file before running this script.
:: The database can simply be created by running the application and closing it right after.

:: It's not necessary to add sqlite3 to the PATH, as this script uses Python's built-in sqlite3 
:: module to execute the SQL script.

@echo off
setlocal

set "DATA_DIR=%~dp0"
set "DATABASE=%DATA_DIR%garum.db"
set "MOCK_DATA=%DATA_DIR%mock_data.sql"

if not exist "%DATABASE%" (
    echo Database not found: "%DATABASE%"
    echo Start the application once to create it, then run this script again.
    exit /b 1
)

python -c "import sqlite3, sys; database, script = sys.argv[1:]; connection = sqlite3.connect(database); connection.execute('PRAGMA foreign_keys = ON'); connection.executescript(open(script, encoding='utf-8').read()); connection.close()" "%DATABASE%" "%MOCK_DATA%"
if errorlevel 1 (
    echo Failed to load mock data.
    exit /b 1
)

echo Mock data loaded into "%DATABASE%".
endlocal