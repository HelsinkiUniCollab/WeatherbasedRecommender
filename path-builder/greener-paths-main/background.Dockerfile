FROM python:3.11
WORKDIR /
RUN apt update && apt -y install cron
RUN apt install -y osmctools gnupg curl
RUN pip install netCDF4==1.6.4 requests==2.31.0 pymongo==4.5.0
# Mongosh
RUN wget -qO- https://www.mongodb.org/static/pgp/server-7.0.asc | tee /etc/apt/trusted.gpg.d/server-7.0.asc
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
RUN apt update
RUN apt install -y mongodb-mongosh
RUN mongosh --version
#
COPY cronjobs /etc/cron.d/cronjobs
COPY update_aqi.sh /
COPY aqi_tools.py /
COPY utils /utils
COPY activity_definitions.py /
COPY build_mongodb.py /
COPY start_background_services.sh /
COPY graphhopper_server/graphhopper_data/config.yml /
RUN chmod +x update_aqi.sh
RUN chmod +x start_background_services.sh
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjobs
# Apply cron job
RUN crontab /etc/cron.d/cronjobs
CMD ./start_background_services.sh
#CMD ["cron", "-f"]