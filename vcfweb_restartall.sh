ps aux | grep [g]unicorn | awk '{print $2}' | xargs kill -9
fuser -k 8080/tcp
fuser -k 8081/tcp
fuser -k 8082/tcp
gunicorn -c gunicorn1.conf manager:app
gunicorn -c gunicorn2.conf manager:app
gunicorn -c gunicorn3.conf manager:app
