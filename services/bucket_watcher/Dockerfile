FROM python:3

#Change workdir
WORKDIR /usr/src/app

COPY requirements.txt ./

#Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bucket_watcher/main.py"]