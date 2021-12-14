FROM python:3.8-alpine

RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod a+x ./start.sh

CMD ["./start.sh"]
