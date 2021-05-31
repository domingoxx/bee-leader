#!/bin/bash

echo "$*"

BEE_ARGS="$*"

GET_ADDRESS=`curl -L http://bee-leader:5000/getAddress`
echo $GET_ADDRESS

case "$GET_ADDRESS" in
  "NotFound")

    echo "bee 初始化"
    BEE_INIT=`bee init $BEE_ARGS`
    echo "$BEE_INIT"
    GET_ADDRESS=`echo "$BEE_INIT" | grep "using ethereum address" | awk -Faddress'{print $6}' | awk -F\" '{print $1}'`
    
    if [ ! -z "$GET_ADDRESS" -a "$GET_ADDRESS" != " " ]; then

      echo "地址生成成功 $GET_ADDRESS"
      UPLOAD_RESULT=`curl -L http://bee-leader:5000/uploadAddress?address=$GET_ADDRESS`
      
      if [ "$UPLOAD_RESULT" == "OK" ]; then
        echo "上传地址成功"
        mkdir -p /opt/bee/$GET_ADDRESS
      else
        echo "上传地址失败 $UPLOAD_RESULT"
        exit -1
      fi
    else
      echo "地址生成失败"
      exit -1

    fi
  ;;
esac

bee start $BEE_ARGS --data-dir /opt/bee/$GET_ADDRESS

curl -L http://bee-leader:5000/getAddress?address=$GET_ADDRESS