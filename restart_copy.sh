ps aux | grep [s]upervisord | awk '{print $2}' | xargs kill -9
ps aux | grep [c]elery | awk '{print $2}' | xargs kill -9
ps aux | grep [g]unicorn | awk '{print $2}' | xargs kill -9
supervisord -c supervisord.conf
#fuser -k 8080/tcp
#gunicorn -c gunicorn.conf manager:app
