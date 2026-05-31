# IMAGE INSTALL
FROM odoo:18.0
# USER TO INSTALL
USER root
# COPY FILE REQUERIMENTS IN SERVICE
COPY /addons/requirements.txt /mnt/extra-addons
# EXECUTE REQUERIMENTS.TXT
# RUN pip3 install -r /mnt/extra-addons/requirements.txt

