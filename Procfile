# Railway / Heroku: set root directory to this repo, or use a start command that cds into `slate`.
web: cd slate && python manage.py migrate --noinput && gunicorn slate.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout 120
