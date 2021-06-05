import datetime

import pika

params = pika.ConnectionParameters(host='192.168.49.2', port=30762)
connection = pika.BlockingConnection(parameters=params)
channel = connection.channel()

channel.queue_declare(queue='results')

def callback(ch, method, properties, body):
    body = body.decode('utf-8').split(';')
    print(datetime.datetime.fromisoformat(body[1]))
    print(body[0])
    print(eval(body[2]))

channel.basic_consume(queue='rtmp://192.168.49.2:30000/live/1',
                      auto_ack=True,
                      on_message_callback=callback)
channel.start_consuming()
