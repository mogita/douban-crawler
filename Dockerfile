FROM python:3.8-bullseye

ENV LANG="en_US.UTF-8"

# Comment the following line if you don't need an alternative debian software source
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list && rm -Rf /var/lib/apt/lists/* && apt-get update
RUN apt-get update
RUN apt-get install -y make automake gcc g++ subversion python3-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
# Comment the following line if you don't need an alternative pypi source
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod a+x ./start.sh

CMD ["./start.sh"]
