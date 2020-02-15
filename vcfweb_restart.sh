# 
# !!! redis need restart  !!!
# ./src/redis-server redis.conf
ps aux | grep [g]unicorn | awk '{print $2}' | xargs kill -9
fuser -k 8080/tcp
gunicorn -c gunicorn.conf manager:app
