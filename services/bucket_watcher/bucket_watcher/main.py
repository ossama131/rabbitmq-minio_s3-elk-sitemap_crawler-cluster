import os, sys
import time
from utils.helpers import start_consuming, close_all_rabbitmq_conn


def main():
    start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        print('Closing Connections to RabbitMQ')
        conn_closed, e = close_all_rabbitmq_conn()
        while not conn_closed:
            print(f'Failed: {e}')
            print('Trying Again to close all connections after 5 sec!')
            time.sleep(5)
            conn_closed = close_all_rabbitmq_conn()
        print('All connections closed succefully!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)