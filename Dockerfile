FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

#RUN pip install poetry && poetry install

CMD ["python", "bot.py"]

#CMD ["poetry", "run", "python", "main.py"]
