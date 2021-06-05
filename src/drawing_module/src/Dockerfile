FROM python:3.8-slim-buster

COPY src /app/src
COPY requirements.txt /app/requirements.txt
WORKDIR /app/src
RUN apt-get update
RUN apt-get -y install gcc && apt-get install -y librtmp-dev
# RUN apt-get update && apt-get -y install gcc && apt-get -y install g++ 
RUN pip install -r ../requirements.txt

CMD ["python", "manager_api.py"]