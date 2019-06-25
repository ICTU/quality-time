FROM node:alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /work
ADD . /work
RUN npm install
RUN npm install -g serve
RUN npm run build

CMD ["serve", "-s", "build"]
