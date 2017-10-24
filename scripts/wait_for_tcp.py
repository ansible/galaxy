import argparse
import socket
import time


def try_connect(host, port, timeout=5.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except socket.error:
        return False
    finally:
        s.close()


def wait_for_connection(host, port, attempts=10):
    while attempts > 0:
        if try_connect(host, port):
            return True
        time.sleep(1)
        attempts -= 1
    return False


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('port', type=int)

    args = parser.parse_args(argv)
    if not wait_for_connection(args.host, args.port):
        return 1


if __name__ == '__main__':
    exit(main())
