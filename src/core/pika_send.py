import pika
import datetime

params = pika.ConnectionParameters(host='192.168.49.2', port=30762)
connection = pika.BlockingConnection(parameters=params)
channel = connection.channel()
channel.queue_declare(queue='results')
channel.basic_publish(exchange='', routing_key='results',
                      body=f'rtmp://192.168.49.2:30000/live/1;{datetime.datetime.now()};{str([[1,2,3,4], [1,2,3,4]])}')
connection.close()
