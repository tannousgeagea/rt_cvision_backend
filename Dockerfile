FROM ubuntu:22.04

LABEL maintainer="tannous.geagea@wasteant.com"
LABEL com.wasteant.version="1.1b1"

ARG user
ARG userid
ARG group
ARG groupid

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -q -y --no-install-recommends \
    apt-utils \
    vim \
    git \
    iputils-ping \
    netcat \
    ssh \
    curl \
    lsb-release \
    wget \
    zip \
    sudo \
    cron \
    && rm -rf /var/lib/apt/lists/*

# install python dependancies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -q -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3 \
    python3-pip \
    python3-dev \
    python3-wstool \
    build-essential \
    python3-distutils \
    python3-psutil \
    python3-tk \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid $groupid $group \
    && adduser --uid $userid --gid $groupid --disabled-password --gecos '' --shell /bin/bash $user \
    && echo "$user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$user \
    && chmod 0440 /etc/sudoers.d/$user

RUN mkdir -p /home/$user/src

# set work directory
WORKDIR /home/$user/src

# Create directory for Supervisor logs
RUN mkdir -p /var/log/supervisor && \
    chmod -R 755 /var/log/supervisor

# install python packages
RUN pip3 install supervisor
RUN pip3 install fastapi[standard]
RUN pip3 install uvicorn[standard]
RUN pip3 install gunicorn
RUN pip3 install django==4.2
RUN pip3 install asgi_correlation_id
RUN pip3 install redis
RUN pip3 install python-redis-lock
RUN pip3 install celery
RUN pip3 install flower
RUN pip3 install requests
RUN pip3 install psycopg2-binary
RUN pip3 install django-unfold
RUN pip3 install whitenoise
RUN pip3 install python-jose

COPY . /home/$user/src/
COPY ./supervisord.conf /etc/supervisord.conf
COPY ./entrypoint.sh /home/
RUN /bin/bash -c "chown -R $user:$user /home/"
ENTRYPOINT /bin/bash -c ". /home/entrypoint.sh"


