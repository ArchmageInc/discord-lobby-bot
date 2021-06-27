FROM python:3.9-slim
EXPOSE 8888

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update \
  && apt-get install -y gcc make ffmpeg --no-install-recommends \
  && apt-get clean \
  && pip install --user -r requirements.txt \
  && apt-get purge -y --auto-remove gcc make

COPY ./src ./

CMD [ "python", "-u", "bot.py" ]