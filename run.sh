#!/bin/bash
# webcrawler 실행스크립트

echo "다크웹크라울러 시작"

if [ ! -f "config.yml" ]; then
	echo "config.yml 파일이 없습니다"
	exit 1
fi

#./webcrawler -c config.json http://c4hjyx6h2qp5lmq77ysvv5mv6yv6yfsokptwipqktibxvckyxfo7hkqd.onion/ 
./webcrawler -c config.yml http://dwkcmg5ewqvmuacunudjr7so5l2jq7wneafdzsnjllmbcec3nwu7o7id.onion
