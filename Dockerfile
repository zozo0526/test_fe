FROM node:18.16.1 as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY ./ .
RUN npm run build

FROM nginx:stable-alpine3.17-slim as production-stage
RUN mkdir /app
COPY --from=build-stage /app/dist /app

#CMD gunicorn -c gun.conf -w 1 main:app
# Example build command:
# docker build --progress=plain -t gflai2/genlab_fe:1.0.0 -f Dockerfile .