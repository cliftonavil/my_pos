#!/usr/bin/env bash
kill -9 $(lsof -t -i:8000)
python manage.py runserver 8000



