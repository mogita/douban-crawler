FROM python:3.8-alpine

# Uncomment the following line if you need to use an alternative alpine software source
# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
# Uncomment the following line if you need to use an alternative pypi source
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod a+x ./start.sh

CMD ["./start.sh"]
