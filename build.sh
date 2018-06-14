REPO=dockerhub.emoney.cn
GROUP=logplat
NAME=onlinestat
CONF_FILE=app/onlinestat.yml
TEST_CONF_FILE=onlinestat-test.yml

TAG=$(cat .dockertag)

IMG_NAMG=$REPO/$GROUP/$NAME:$TAG

if [ "$1" == "test" ];then
    mv $CONF_FILE ${CONF_FILE}.bak
    cp $TEST_CONF_FILE $CONF_FILE 
    IMG_NAMG="testenv/$NAME:$TAG"
fi

docker build app -t $IMG_NAMG

if [ "$1" == "test" ];then
    mv ${CONF_FILE}.bak $CONF_FILE
fi
