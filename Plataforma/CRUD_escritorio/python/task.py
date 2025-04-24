from celery import shared_task
from .export_busquedas import export_busquedas_for_month
from datetime import datetime

@shared_task
def export_last_month_busquedas():
    now = datetime.now()
    last_month = now.month - 1 if now.month > 1 else 12
    year = now.year if now.month > 1 else now.year - 1
    export_busquedas_for_month(year, last_month)