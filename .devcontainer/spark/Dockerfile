FROM bitnami/spark:latest

USER root

RUN apt-get update && \
    apt-get install -y wget python3 python3-pip git && \
    mkdir -p /usr/lib/jvm && \
    wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.14%2B9/OpenJDK11U-jdk_x64_linux_hotspot_11.0.14_9.tar.gz && \
    tar xzf OpenJDK11U-jdk_x64_linux_hotspot_11.0.14_9.tar.gz -C /usr/lib/jvm/ && \
    rm OpenJDK11U-jdk_x64_linux_hotspot_11.0.14_9.tar.gz && \
    ln -s /usr/lib/jvm/jdk-11.0.14+9 /usr/lib/jvm/java-11-openjdk-amd64

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

RUN mkdir -p /root/.ivy2

COPY requirements-spark.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-spark.txt

CMD ["tail", "-f", "/dev/null"]
