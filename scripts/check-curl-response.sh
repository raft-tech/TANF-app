if cf curl "/v2/apps" -v | grep 203
then 
   echo "OK";
else
   echo "NOT OK";
fi

while [cf curl "/v2/apps" -v | grep "HTTP/1.1 200 OK"]
do
  sleep 0.1
done