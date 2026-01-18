@echo off
echo ==========================================
echo   Database Status (Supabase)
echo ==========================================
echo.

:: Change to project root directory
cd /d "%~dp0\.."

:: Test connection and show stats
python -c "from database import test_connection, get_db_session, Company, Contact, Search; test_connection(); s=get_db_session(); db=s.__enter__(); print(); print(f'Companies: {db.query(Company).count()}'); print(f'Contacts:  {db.query(Contact).count()}'); print(f'Searches:  {db.query(Search).count()}'); s.__exit__(None,None,None)"

echo.
echo ==========================================
echo   Additional Commands
echo ==========================================
echo To see detailed company list:
echo   python scripts\list_companies.py
echo.
echo To verify migration:
echo   python -c "from database.migrate_json_to_db import verify_migration; verify_migration()"
echo.
echo To access Supabase Dashboard:
echo   https://supabase.com/dashboard
echo.
pause
