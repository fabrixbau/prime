from datetime import timedelta, datetime

# Function to generate dates with greater memory efficiency
def date_range(start_date, end_date):
    """Generar un rango de fechas entre start_date y end_date."""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)
