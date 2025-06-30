# Image de base officielle avec Python 3.11
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Passer en root pour installer Java
USER root

# Installer Java
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean

# Définir JAVA_HOME et mettre à jour PATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"


# Revenir à l’utilisateur vscode
USER vscode

# # Installer les dépendances Python
# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

