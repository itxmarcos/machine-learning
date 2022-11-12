#!/bin/sh
export PYTHONIOENCODING=UTF-8
cd /entity_detector-master
python apirest.py
#
#echo "$PYTHON_HOME/python $SERVICE_PATH/$ENTRY_POINT"
#${PYTHON_HOME}/python ${SERVICE_PATH}/${ENTRY_POINT}

