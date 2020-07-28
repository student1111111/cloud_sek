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
docker run -p 8888:5000  akstldr/gen_random_app
```
* To register a user, run from other terminal hit end point '/register' witjh user_name and password
```
curl --header "Content-Type: application/json" --request POST --data '{"user_name":"user1","password":"pasword1"}'   http://127.0.0.1:8888/register
```
