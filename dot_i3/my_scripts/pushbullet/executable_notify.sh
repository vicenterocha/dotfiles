#!/usr/bin/env bash

while getopts t:b: opt; do
    case $opt in
    t)
        title=$OPTARG
        ;;
    b)
        body=$OPTARG
        ;;
    esac
done

# Send notification to Pushbullet to specific device (device_iden) with the given title and body
curl --header 'Access-Token: '"$PUSHBULLET_API_KEY"'' \
     --header 'Content-Type: application/json' \
     --data-binary '{"title":"'"$title"'",
					"body":"'"$body"'",
					"type":"note",
					"device_iden":"'$PUSHBULLET_S10_IDEN'"}' \
     --request POST \
     https://api.pushbullet.com/v2/pushes

