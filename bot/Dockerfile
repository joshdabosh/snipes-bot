FROM python:3.8-slim

COPY ./ /snipes-bot
WORKDIR /snipes-bot

RUN pip3 install --upgrade -r requirements.txt

CMD ["python3", "bot.py"]