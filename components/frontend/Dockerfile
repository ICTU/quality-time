FROM node:alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time frontend"

ARG REACT_APP_SERVER_URL
ENV REACT_APP_SERVER_URL ${REACT_APP_SERVER_URL:-http://localhost:8080}

WORKDIR /work
ADD . /work
RUN npm install
RUN npm install -g serve
RUN npm run build

CMD ["serve", "-s", "build"]
