#!/bin/bash
set -e

# /bin/bash -c "python3 /home/$user/src/rt_cvision_backend/manage.py makemigrations"
# /bin/bash -c "python3 /home/$user/src/rt_cvision_backend/manage.py migrate"
# /bin/bash -c "python3 /home/$user/src/rt_cvision_backend/manage.py create_superuser"

sudo -E supervisord -n -c /etc/supervisord.conf