@echo off
cd C:\Users\informaticos\Desktop\Django Tareas A.Mercado\Plataforma
call venv\Scripts\activate
python -c "from datetime import datetime; from CRUD_escritorio.cron import export_last_month_busquedas; export_last_month_busquedas()"