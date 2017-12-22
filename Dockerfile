FROM python:3

WORKDIR /usr/src/crawler

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./crawler.py" ]