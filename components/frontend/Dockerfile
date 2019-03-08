FROM node:alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Quality-time frontend"

ENV REACT_APP_SERVER_URL=http://localhost:8080

WORKDIR /work
ADD . /work
RUN npm install
RUN npm install -g serve
RUN npm run build

CMD ["serve", "-s", "build"]
