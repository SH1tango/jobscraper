FROM python:3.12-alpine

# system deps for lxml
RUN apk add --no-cache libxml2 libxslt && \
    apk add --no-cache --virtual .build-deps gcc musl-dev libxml2-dev libxslt-dev

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY api.py scraper.py run.sh /app/
RUN chmod +x /app/run.sh

# clean build deps
RUN apk del .build-deps

# HA add ons expect s6, but a simple long running process is fine here
EXPOSE 8001
ENV PYTHONUNBUFFERED=1
CMD ["/app/run.sh"]
