#!/bin/sh
echo "Making migrations..."
python manage.py makemigrations --noinput


echo "Applying database migrations..."
python manage.py migrate --noinput


echo "Collecting static files..."
python manage.py collectstatic --noinput


echo "Starting Gunicorn..."
gunicorn Doctors_Appointment_Booking_System.wsgi:application --bind 0.0.0.0:8000
