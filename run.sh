uwsgi --http 192.168.1.175:9090 -w index -H /Users/tangyue/.pyvirtualenvs/genju/ -d uws.log
tail -F uws.log
