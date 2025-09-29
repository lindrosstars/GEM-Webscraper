FROM python:3.12-slim


USER root

# These libraries are crucial for a headless browser to run correctly
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libfontconfig1 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    # Clean up the package cache to reduce image size
    && rm -rf /var/lib/apt/lists/*



RUN GECKODRIVER_VERSION="0.34.0" && \
    wget https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -zxf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/


WORKDIR /usr/src/app


COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt


COPY gemscraperJSON.py ./


CMD [ "python3", "gemscraperJSON.py" ]