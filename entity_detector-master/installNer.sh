logPath=./log

mkdir -p $logPath

downloadingModel(){

    echo "download model glove"
    mkdir entity_detector-master/results/ner/ -p
    wget -qO-  $urlModel | tar -xzv -C entity_detector-master/results/ner/
    code=$?
    if [ $code -ne 0 ]; then
        echo "[Error] code $code"
        echo "[Error] to download model glove"
        exit
    fi
    echo "OK"

    echo "download model resources "
    mkdir entity_detector-master/resources/ -p
    wget -qO-  $urlModelResources | tar -xzv -C entity_detector-master/resources/
    code=$?
    if [ $code -ne 0 ]; then
        echo "[Error] code $code"
        echo "[Error] to download model resources"
        exit
    fi
    echo "OK"
}



#downloadingNer(){
#
#    echo -ne "[INFO] download Ner from git ..."
#    mkdir -p entity_detector-master/
#    wget  --no-cache -qO-  'https://git.itainnova.es/api/v4/projects/96/repository/archive.tar.gz?ref=master&private_token=SHRCF-65tNzyifAuB6Vy'  | tar -xzv -C  entity_detector-master --strip-components=1

#    code=$?
#    if [ $code -ne 0 ]; then
#        echo "[Error] code $code"
#        echo "[Error] to download NER"
#        exit
#    fi
#    echo "OK"
#
#}


urlModel=http://193.144.231.29:8081/repository/war/models/model_glove_all_char100_300_3.weights.tar.gz
urlModelResources=http://193.144.231.29:8081/repository/war/models/glove_all.tar.gz

#downloadingNer
downloadingModel

#python apirest.py

