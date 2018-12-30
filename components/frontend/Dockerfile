FROM node:alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Quality-time frontend"

RUN npm install -g serve

WORKDIR /work
ADD . /work
RUN npm run build

CMD ["serve", "-s", "build"]
