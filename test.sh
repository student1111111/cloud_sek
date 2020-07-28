#!/bin/bash
register()
{
curl --header "Content-Type: application/json" --request POST --data '{"username":"aks1","password":"aks111"}'   http://127.0.0.1:8888/register 2>/dev/null
}

login()
{
auth_token=$(curl -X POST -F 'username=aks1' -F 'password=aks111' http://127.0.0.1:8888/login 2>/dev/null| awk -F "\"" '{print $4}')
echo $auth_token
}

call_api()
{
if [[ $# -ne 1 ]]; then
    echo "Please provide brearer token for API"
    exit 1
fi
token=$1
curl -X GET -H "Authorization: Bearer $token" -F "password=aks111" http://127.0.0.1:8888/call_api 2>/dev/null
}

see_remaining_limit()
{
if [[ $# -ne 1 ]]; then
    echo "Please provide brearer token for API"
    exit 1
fi
token=$1
curl -X GET -H "Authorization: Bearer $token" -F "password=aks111" http://127.0.0.1:8888/see_remaining_limit 2>/dev/null
}

########## TEST ##########

register
token=$(login)
echo ""
echo $token

for i in $(seq 1 5);do
    echo "call $i th random value"
    call_api $token
    echo ""
done

echo "called API 5 times now, next calls should fail for rate limit "
call_api $token
echo ""
call_api $token
echo ""

echo "Remaining limit should be 0"
see_remaining_limit $token
echo ""
echo "Sleeping for a minute to replish tockens"
sleep 62s

echo "Now remainin limit should 5"
see_remaining_limit $token
echo""
echo "API call should succed"
call_api $token
echo ""
echo "Done"
