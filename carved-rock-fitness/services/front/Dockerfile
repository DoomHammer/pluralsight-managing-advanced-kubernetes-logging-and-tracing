FROM node:10.17-alpine

ADD package.json yarn.lock .yarnrc /app/

WORKDIR /app

RUN yarn

ADD . /app/

EXPOSE 3000

CMD npx react-scripts start
