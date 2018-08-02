#!/bin/bash

module load AI/anaconda3-5.1.0_gpu
source activate $AI_ENV
#sacctmgr show events event=node -P Start=07/27/18-15:58:14 End=07/27/18-15:59:14

while true
do 
   
    
   START=`date '+%m/%d/%y-%H:%M:%S' --date='1 minute ago'`
   END=`date '+%m/%d/%y-%H:%M:%S'`
   START_FILE=`date '+%m%d%y_%H:%M:%S' --date='1 minute ago'`
   END_FILE=`date '+%m%d%y_%H:%M:%S'`
   START_ISO8601=`date '+%Y-%m-%dT%H:%M:%S' --date='1 minute ago'`
   END_ISO8601=`date '+%Y-%m-%dT%H:%M:%S'`
   echo $START $END
   echo $START_FILE $END_FILE
   
   sacct -a -P -X -S $START -E $END --format=Account,AllocTRES,JobName,JobID,User,Partition,Start,State,Submit,ReqMem,Timelimit,NodeList,End -s CANCELLED,TIMEOUT,FAILED,COMPLETED,NODE_FAIL,OUT_OF_MEMORY -r GPU,GPU-shared,GPU-small > "daily_sacct/${START_FILE}_${END_FILE}_sacct_gpu.csv"
   sacct -a -P -X -S $START -E $END --format=Account,AllocTRES,JobName,JobID,User,Partition,Start,State,Submit,ReqMem,Timelimit,NodeList,End -s CANCELLED,TIMEOUT,FAILED,COMPLETED,NODE_FAIL,OUT_OF_MEMORY -r RM,RM-shared,RM-small > "daily_sacct/${START_FILE}_${END_FILE}_sacct_rm.csv"
   sacct -a -P -X -S $START -E $END --format=Account,AllocTRES,JobName,JobID,User,Partition,Start,State,Submit,ReqMem,Timelimit,NodeList,End -s CANCELLED,TIMEOUT,FAILED,COMPLETED,NODE_FAIL,OUT_OF_MEMORY -r LM > "daily_sacct/${START_FILE}_${END_FILE}_sacct_lm.csv"
   sacctmgr show events event=node -P Start=$START End=$END > daily_sacct/${START_FILE}_${END_FILE}_sacctmgr.csv
   SACCT_GPU="daily_sacct/${START_FILE}_${END_FILE}_sacct_gpu.csv"
   SACCT_RM="daily_sacct/${START_FILE}_${END_FILE}_sacct_rm.csv"
   SACCT_LM="daily_sacct/${START_FILE}_${END_FILE}_sacct_lm.csv"
   SACCTMGR="daily_sacct/${START_FILE}_${END_FILE}_sacctmgr.csv"
   python Log_Preprocessing.py "$START_ISO8601" "$END_ISO8601" "$START_FILE" "$END_FILE" "$SACCT_GPU" "$SACCT_RM" "$SACCT_LM" "$SACCTMGR"
   sleep 60
   break
done
