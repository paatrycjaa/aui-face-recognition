FROM ubuntu:latest
 
#
# Identify the maintainer of an image
LABEL maintainer="pawelzakieta97@gmail.com"
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y install build-essential libpcre3 libpcre3-dev libssl-dev 
# RUN apt-get update && \
#     apt-get -y install gcc mono-mcs && \
#     rm -rf /var/lib/apt/lists/*
#
# Update the image to the latest packages
# RUN apt-get update && apt-get upgrade -y
 
#
# Install NGINX to test.
# RUN apt-get install nginx -y


COPY nginx-1.19.10 ./nginx-1.19.10
COPY nginx-rtmp-module-dev ./nginx-rtmp-module-dev
COPY nginx.conf ./nginx.conf
WORKDIR ./nginx-1.19.10
RUN ./configure --with-http_ssl_module --without-http_gzip_module --add-module=../nginx-rtmp-module-dev
RUN make
RUN make install

COPY nginx.conf /usr/local/nginx/conf/nginx.conf
 
#
# Expose port 80
EXPOSE 80
EXPOSE 1935
 
#
# Last is the actual command to start up NGINX within our Container
CMD ["/usr/local/nginx/sbin/nginx","-g", "daemon off;"]
# CMD ["nginx", "-g", "daemon off;"]