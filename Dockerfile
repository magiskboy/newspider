FROM python:3.8-alpine3.12 AS compile-image

LABEL maintainer="nguyenkhacthanh244@gmail.com" version="0.0.1"

WORKDIR /app

ADD ./requirements.txt .

RUN python -mvenv venv && \
    venv/bin/pip install -r requirements.txt

FROM python:3.8-alpine3.12

WORKDIR /app

COPY --from=compile-image /app/venv ./venv

ADD . .

EXPOSE 8000

ENTRYPOINT ./entry-point.sh

CMD /bin/sh
