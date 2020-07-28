## How to run
* Cretae Docker hub account https://hub.docker.com/
* git clone https://github.com/student1111111/cloud_sek.git
* cd cloud_sek
* Build Docker image
```
docker build -t <docker_hub_account>/gen_random_app .
```
* Docker Run
```
docker run -p 8888:5000  <docker_hub_account>/gen_random_app
```
* To register a user, run from other terminal hit end point '/register' witjh username and password
```
curl --header "Content-Type: application/json" --request POST --data '{"username":"user1","password":"pasword1"}'   http://127.0.0.1:8888/register
```
* `/login` API to authencate user and get security token
```
curl -X POST -F 'username=user1' -F 'password=password1' http://127.0.0.1:8888/login 
```
 *  This will return with access_token, for eg.
```
[ec2-user@ip-172-31-39-59 ~]$ curl -X POST -F 'username=user1' -F 'password=password1' http://127.0.0.1:8888/login

{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYwMTEzODU1M30.V9yqKlKPHDM2p5Js1amcySpI-vNG2apAK5CVvCfTE2I","token_type":"bearer"}
```
 * use this `access_token` for other GET APIs

* `/call_api` to get random rumber
```
curl -X GET -H "Authorization: Bearer $token" -F "password=password1" http://127.0.0.1:8888/call_api
9
```

* `/see_remaining_limit` API to get remainin API calls in the minute
```
curl -X GET -H "Authorization: Bearer $token" -F "password=password1" http://127.0.0.1:8888/see_remaining_limit
5
```

* run Automated Test for test all functionality
```
./test.sh
```
 * outut like
```
./test.sh

"Successfully registered aks1"
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJha3MxIiwiZXhwIjoxNjAxMTM4MTc3fQ.3K7HW4Lk5sXnNvBikpaSzNiAXSg5sqFMGt6pq1KP4fw
call 1 th random value
93
call 2 th random value
40
call 3 th random value
90
call 4 th random value
92
call 5 th random value
37
called API 5 times now, next calls should fail for rate limit
{"detail":"API rate limit excceded"}
{"detail":"API rate limit excceded"}
Remaining limit should be 0
0
Sleeping for a minute to replish tockens
Now remainin limit should 5
5
API call should succed
4
Done

```

* Kill the service by `docker kill`

```
[ec2-user@ip-172-31-39-59 ~]$ docker ps
CONTAINER ID        IMAGE                    COMMAND             CREATED             STATUS              PORTS                    NAMES
842fba59f3a7        akstldr/gen_random_app   "./start_app.sh"    6 minutes ago       Up 6 minutes        0.0.0.0:8888->5000/tcp   pensive_vaughan

[ec2-user@ip-172-31-39-59 ~]$ docker kill 842fba59f3a7
842fba59f3a7
```
