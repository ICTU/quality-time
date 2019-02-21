FROM node:alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Quality-time frontend"

WORKDIR /work
ADD . /work
RUN npm install
RUN npm run build

CMD ["serve", "-s", "build"]
