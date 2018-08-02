
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import time
import sys

#variables passed from preprocess.sh
var1 = sys.argv[1]
var2 = sys.argv[2]
start_file = sys.argv[3]
end_file = sys.argv[4]
sacct_gpu = sys.argv[5]
sacct_rm = sys.argv[6]
sacct_lm = sys.argv[7]
sacctmgr = sys.argv[8]



# # Process Data from ssact
# ### Sample sacct command for GPU nodes:
# sacct -a -P -X -S 071918-00:00:00 -E 072018-23:59:59 --format=Account,AllocTRES,JobName,JobID,User,Partition,Start,State,Submit,ReqMem,Timelimit,NodeList,End -s CANCELLED,TIMEOUT,FAILED,COMPLETED,NODE_FAIL,OUT_OF_MEMORY -r GPU,GPU-shared,GPU-small> today_gpu.csv
# 
# ### Sample sacct command for RM nodes:
# sacct -a -P -X -S 071918-00:00:00 -E 072018-23:59:59 --format=Account,AllocTRES,JobName,JobID,User,Partition,Start,State,Submit,ReqMem,Timelimit,NodeList,End -s CANCELLED,TIMEOUT,FAILED,COMPLETED,NODE_FAIL,OUT_OF_MEMORY -r RM,RM-shared,RM-small> today_rm.csv
# 
# ### Sample sacct command for LM nodes:
# sacct -a -P -X -S 071918-00:00:00 -E 072018-23:59:59 --format=Account,AllocTRES,JobName,JobID,User,Partition,Start,State,Submit,ReqMem,Timelimit,NodeList,End -s CANCELLED,TIMEOUT,FAILED,COMPLETED,NODE_FAIL,OUT_OF_MEMORY -r LM> today_lm.csv

# In[2]:


def lm_process_node_partition(df):
    xl = []
    l =[]
    for a in range(df["NodeList"].shape[0]):
        if df["NodeList"][a][0]=="x":
            xl.append(a)
        elif df["NodeList"][a][0]=="l":
            l.append(a)
    #xlm
    xlm=df.iloc[xl,:]
    xlm["NodeList_1"]=xlm["NodeList"].str.replace("xl","")
    xlm["type"]="xl"
    #lm    
    lm=df.iloc[l,:]
    lm["NodeList_1"]=lm["NodeList"].str.replace("l","")
    lm["type"]="l"
    all_lm=pd.concat([lm,xlm])
    return all_lm


# In[3]:


def process_AllocTRES(df,fileName):
    if "gpu" in str(fileName):
        df["Alloc_NODE"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[2].str[5:])
        df["Alloc_gres/gpu"]=np.where(df['AllocTRES']=='Not Allocated', 0,df['AllocTRES'])
        df["Alloc_gres/gpu"]=np.where(df['Alloc_gres/gpu'].str.split(",").str[4].str.contains(":"),df['Alloc_gres/gpu'].str.split(",").str[4].str[9:12],df['Alloc_gres/gpu'].str.split(",").str[5].str[9:12])
        df["Alloc_gres/gpu"]=np.where(df['Alloc_gres/gpu']=='p10', 'p100',df['Alloc_gres/gpu'])
        df["Alloc_GPU"]=np.where(df['AllocTRES']=='Not Allocated',0, df['AllocTRES'])
        df["Alloc_GPU"]=np.where(df['Alloc_GPU'].str.split(",").str[4].str.contains(":"),df['Alloc_GPU'].str.split(",").str[4].str[-2:],df['Alloc_GPU'].str.split(",").str[5].str[-2:])
        df["Alloc_GPU"]=df["Alloc_GPU"].str.replace("=","")
    elif "rm" in str(df):
        df["Alloc_CPU"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[0].str[4:])
        df["Alloc_MEM"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[1].str[4:-1])
        df["Alloc_NODE"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[2].str[5:])
    else:
        df["Alloc_CPU"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[0].str[4:])
        df["Alloc_MEM"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[1].str[4:-1])
        df["Alloc_NODE"]=np.where(df['AllocTRES']=='Not Allocated', 0, df['AllocTRES'].str.split(",").str[2].str[5:])


    print(df)
    return df
        
    


# In[4]:


def process_NodeList_Row(row):
    allNum = []
    [[allNum.append(i) for i in range(int(a.split("-")[0]), int(a.split("-")[1])+1, 1)] if "-" in a else allNum.append(int(a)) for a in row.split(",")] 
    return allNum

def process_NodeList(df,fileName):
    all_arr=[]
    if "gpu" in str(fileName):
        df["NodeList_1"]=df["NodeList"].str.replace("gpu","")
    elif "rm" in str(fileName):
        df["NodeList_1"]=df["NodeList"].str.replace("r","")
    else:
        df=lm_process_node_partition(df)
    df["NodeList_1"]=df["NodeList_1"].str.replace("[","")
    df["NodeList_1"]=df["NodeList_1"].str.replace("]","")
    for row in df["NodeList_1"]:
        if row=="None assigned":
            all_arr.append(None)
        elif "-" not in row and "," not in row:
            all_arr.append([int(row)])
        else:
            all_arr.append(process_NodeList_Row(row))
    df["nodeArray"]=all_arr
    
    return df
    


# In[5]:


#Transform the requested time to seconds
def process_TimeLimit(df):
    df["Timelimit"] = df["Timelimit"].str.replace("-",":") 
    temp=df['Timelimit'].str.split(":")
    df['ReqTime']=np.where(temp.str.len()==3,temp.str[0].astype(int)*3600+temp.str[1].astype(int)*60+temp.str[2].astype(int),temp.str[0].astype(int)*86400+temp.str[1].astype(int)*3600+temp.str[2].astype(int)*60+temp.str[3].fillna(0).astype(int))
    df=df.drop(['Timelimit'], axis=1)
    return df


# In[6]:


def sacct_data_cleansing(fileName):

    df = pd.read_csv(fileName, sep='|',error_bad_lines=False)
    df = df.dropna(subset=["AllocTRES"])
    df = df.sort_values('Start')
    df = process_AllocTRES(df,fileName)
    df = df.reset_index(drop=True)
    df["End"]=np.where(df['End']=='Unknown',None,df['End'])
    df["Start"]=np.where(df['Start']=='Unknown',None,df['Start'])
    df = process_NodeList(df,fileName)
    df=process_TimeLimit(df)
    return df.drop(['AllocTRES','NodeList_1'], axis=1)
    
    

        
df_gpu=sacct_data_cleansing(sacct_gpu)
#df_gpu.to_csv("gpu.csv")
df_rm=sacct_data_cleansing(sacct_rm)
#df_rm.to_csv("rm.csv")
df_lm=sacct_data_cleansing(sacct_lm)
#df_lm.to_csv("lm.csv")



# # Process Data from ssactmgr
# ### Get Events on downed or draining nodes on clusters.
# ### Sample sacctmgr command:
# sacctmgr show events -P event=node Start=071918-00:00:00 End=072018-23:59:59 > today_state.csv

# In[ ]:


# In[8]:


def sacctmgr_data_cleansing(fileName, df):
    df_state=pd.read_csv(sacctmgr, sep='|',error_bad_lines=False)
    df_state["Start"]=var1
    df_state["End"]=var2
    #"df_state=df_state.drop(["Cluster","User"], axis=1)
    df_state=df_state.drop(["Cluster","TimeStart","TimeEnd","Reason","User"],axis=1)
    if "gpu" in fileName:
        df_state= df_state.drop(df_state[df_state["NodeName"].str[:3]!='gpu'].index)
        df_state["Alloc_gres/gpu"]=np.where(df_state["NodeName"].str[3:].astype(int)<17,"k80","p100")
        df_state["nodeArray"]=[[row] for row in df_state["NodeName"].str[3:].astype(int)]
        df_state["Alloc_GPU"]=np.where(df_state["Alloc_gres/gpu"]=="k80",4,2)


    elif "rm" in fileName:
        df_state= df_state.drop(df_state[df_state["NodeName"].str[0]!='r'].index)
        df_state["nodeArray"]=[[row] for row in df_state["NodeName"].str[1:].astype(int)]
        df_state["Alloc_CPU"]=28
        
    else:

        df_lm= df_state.drop(df_state[df_state["NodeName"].str[0]!='l'].index)
        df_lm["nodeArray"]=[[row] for row in df_lm["NodeName"].str[1:].astype(int)]
        df_lm["type"]="l"
        df_lm["Alloc_MEM"]=3000
        df_xlm= df_state.drop(df_state[df_state["NodeName"].str[:2]!='xl'].index)
        df_xlm["type"]="xl"
        df_xlm["Alloc_MEM"]=12000
        df_xlm["nodeArray"]=[[row] for row in df_xlm["NodeName"].str[2:].astype(int)]
        df_state=df_lm.append(df_xlm)
   
    
    df_state["State"]=df_state["State"].str.replace("$","") 
    df_state["State"]=df_state["State"].str.replace("*","") 
#     df_state.rename(columns = {'TimeStart':'Start','TimeEnd':'End'}, inplace = True)
    df_state=df_state.drop(["NodeName"], axis=1)
    df_state["Alloc_NODE"]=1
    df_all=df_state.append(df)
    df_all = df_all.reset_index(drop=True)
    df_all["Alloc_NODE"]=df_all["Alloc_NODE"].fillna(0)
    df_all["State"]=np.where(df_all["State"].str.contains("CANCELLED"),"CANCELLED",df_all["State"])
    
    if "gpu" in fileName:
        df_all["Alloc_GPU"]=df_all["Alloc_GPU"].fillna(0)
        df_all["GPU_used"]=df_all["Alloc_GPU"].astype(float)/df_all["Alloc_NODE"].astype(float)
        
    elif "rm" in fileName:

        df_all["Alloc_CPU"]=df_all["Alloc_CPU"].fillna(0)
        df_all["CPU_used"]=df_all["Alloc_CPU"].astype(float)/df_all["Alloc_NODE"].astype(float)
    else:
        df_all["Alloc_CPU"]=df_all["Alloc_CPU"].fillna(0)
        df_all["Mem_used"]=df_all["Alloc_MEM"].astype(float)/df_all["Alloc_NODE"].astype(float)
        df_all["Partition"]=df_all["type"]
        df_all=df_all.drop(["type"], axis=1)
        

    
    return df_all
       
df_all_gpu=sacctmgr_data_cleansing(sacct_gpu,df_gpu)
df_all_rm=sacctmgr_data_cleansing(sacct_rm,df_rm)
df_all_lm=sacctmgr_data_cleansing(sacct_lm,df_lm)
print(df_all_gpu)
# ### Prepare Data for graphs

# In[9]:


print(list(df_all_gpu))


# In[10]:


print(list(df_all_rm))


# In[11]:


print(list(df_all_lm))


# ### transform start and end time to minute per row
# *** This is how I transformed the data (like taking a snapshot at a specific point of time): If a job has a start time of 2018-07-19T13:28:35 and end time of 2018-07-19T13:32:21 in sacct, this single job will be converted to four rows with timestamp like the following:
# 
# 2018-07-19T13:29:00
# 
# 2018-07-19T13:30:00
# 
# 2018-07-19T13:31:00
# 
# 2018-07-19T13:32:00

# ### For GPU/RM/LM Utilization graphs

# In[86]:


from datetime import date, datetime, timedelta
import dateutil.parser

def perdelta(start, end, delta, job ):
    print(job)
    curr = start
    while curr < end:
        yield curr,job[0],job[1],job[2],job[3],job[4],job[5],job[6],job[7],job[8],job[9],job[10],job[11],job[12],job[13],job[14],job[15],job[16],job[17]
        curr += delta


# In[87]:


def transform_start_end_time(df_util):
    
    df_util["fakeEnd"]=df_util["End"].str[:17]+"59"
    temp_util = []
    for a in range(df_util.shape[0]):
        temp_util_time=[]
        startdate=dateutil.parser.parse(df_util.iloc[a,:]["Start"])
        enddate=dateutil.parser.parse(df_util.iloc[a,:]["fakeEnd"])
        for result in perdelta(startdate,enddate,timedelta(minutes=1),df_util.iloc[a,:]):
            if result[0]==startdate and str(result[0])[17:]!="00":
                pass
            else:
                temp_util_time.append(result)
        temp_util.append(pd.DataFrame(temp_util_time))
    return temp_util


# In[88]:


def createTimeMap(df):
    time=list(df[0])
    timeMaps = {}
    for i in range(len(time)):
        if time[i] not in timeMaps:
            timeMaps[time[i]]=[i]
        else:
            timeMaps[time[i]].append(i)
    return timeMaps


# In[89]:


def createNodeUsage(fileName,result):
    print(result)
    all_data=[]
    if "gpu" in fileName:  
        for key, value in createTimeMap(result).items():
            states = {}
            gpus = {}
            types = {}
            partitions = {}
            for i in value:
                row=result.iloc[i]
                for a in row[16].split(","):
                    if a not in gpus:
                        states[a] = row[13]
                        partitions[a] = row[9]
                        types[a] = row[4]
                        gpus[a]=row[17]
                    else:
                        if row[13]=="COMPLETED" or row[13]=="TIMEOUT" or row[13]=="CANCELLED" or row[13]=="NODE_FAIL" or row[13]=="OUT_OF_MEMORY":
                            gpus[a] = (gpus.get(a)+row[17])


            minute=pd.concat([pd.DataFrame(list(gpus.items())),pd.DataFrame(list(types.values())),pd.DataFrame(list(states.values())),pd.DataFrame(list(partitions.values())),pd.DataFrame([key]*len(gpus))],axis=1)    
            all_data.append(minute)  
    else:
        for key, value in createTimeMap(result).items():
            states = {}
            cpu_OR_mem = {}
            partitions = {}
            for i in value:
                row=result.iloc[i]
                for a in row[16].split(","):
                    if a not in cpu_OR_mem:
                        
                        states[a] = row[13]
                        partitions[a] = row[9]
                        cpu_OR_mem[a]=row[17]
                    else:
                        if row[13]=="COMPLETED" or row[13]=="TIMEOUT" or row[13]=="CANCELLED" or row[13]=="NODE_FAIL" or row[13]=="OUT_OF_MEMORY":
                            cpu_OR_mem[a] =(cpu_OR_mem.get(a)+row[17])


            minute=pd.concat([pd.DataFrame(list(cpu_OR_mem.items())),pd.DataFrame(list(states.values())),pd.DataFrame(list(partitions.values())),pd.DataFrame([key]*len(cpu_OR_mem))],axis=1)    
            all_data.append(minute)  
        
    return all_data


# In[90]:


import datetime as dt
def utilization_graph_data(fileName,df):
    df_util=df.dropna(subset=["Start","End"])
    df_util=df_util.drop(df_util[df_util.End=='Unknown'].index)
    
    if "gpu" in fileName:
        df_util=df_util.dropna(subset=["Alloc_gres/gpu"])
 
    temp_util=transform_start_end_time(df_util)
    if len(temp_util) == 0:return
    result = pd.concat(temp_util)
    result = result.reset_index(drop=True)
    print("::::")
    print(result)
    result[0] = pd.to_datetime(result[0])
    result[0]=result[0].map(lambda x: x.replace(second=0))
    result[16]=result[16].astype("str")
    result[16]=result[16].str.replace("[","")
    result[16]=result[16].str.replace("]","")
    all_data=createNodeUsage(fileName,result)
    if len(all_data) == 0:return
    print(all_data[0])
    all_data_df = pd.concat(all_data)
    
    if "gpu" in fileName:
        all_data_df.columns = ["Node","gpu","type","state","partition","time"]
    elif "rm" in fileName:
        all_data_df.columns = ["Node","core","state","partition","time"]
    else:
        all_data_df.columns = ["Node","mem","state","nodeType","time"]
    
    all_data_df2=all_data_df.reset_index(drop=True)
    all_data_df2['time']= all_data_df2['time'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    all_data_df2["time"]=all_data_df2["time"].str[:-1]
    
    if "gpu" in fileName:
        all_data_df2["partition"]=all_data_df2["partition"].fillna("NA")
        temp=all_data_df2.groupby(['time',"gpu","type","partition","state"])['Node'].count().reset_index()
        temp.to_csv("daily_logs/"+start_file+"_"+end_file+"util_gpu.csv")
        
    elif "rm" in fileName:
        all_data_df2["partition"]=all_data_df2["partition"].fillna("NA")
        temp=all_data_df2.groupby(['time',"core","partition","state"])['Node'].count().reset_index()
        temp.to_csv("daily_logs/"+start_file+"_"+end_file+"util_rm.csv")
        
    else:
        all_data_df2["nodeType"]=all_data_df2["nodeType"].fillna("NA")
        temp=all_data_df2.groupby(['time',"mem","nodeType","state"])['Node'].count().reset_index()
        temp.to_csv("daily_logs/"+start_file+"_"+end_file+"util_lm.csv")
                
    return temp




# In[91]:


start_time = time.time()
gpu_util_graph_data=utilization_graph_data(sacct_gpu,df_all_gpu)
print("--- %s seconds --- for gpu_util_graph_data" % (time.time() - start_time))


# In[92]:


start_time = time.time()
rm_util_graph_data=utilization_graph_data(sacct_rm,df_all_rm)
print("--- %s seconds --- for rm_util_graph_data" % (time.time() - start_time))


# In[93]:


start_time = time.time()
lm_util_graph_data=utilization_graph_data(sacct_lm,df_all_lm)
print("--- %s seconds --- for lm_util_graph_data" % (time.time() - start_time))


# ### For GPU/RM/LM Backlog graphs

# In[67]:


def transform_submit_start_time(df_backlog):
    temp_backlog = []
    for a in range(df_backlog.shape[0]):
        temp_backlog_time=[]
        startdate=dateutil.parser.parse(df_backlog.iloc[a,:]["Submit"])
        enddate=dateutil.parser.parse(df_backlog.iloc[a,:]["fakeStart"])
        for result in perdelta(startdate,enddate,timedelta(minutes=1),df_backlog.iloc[a,:]):
            if result[0]==startdate and str(result[0])[17:]!="00":
                pass
            else:
                temp_backlog_time.append(result)
        temp_backlog.append(pd.DataFrame(temp_backlog_time))

    
    return temp_backlog


# In[78]:


def backlog_graph_data(fileName,df):    
    if df.shape[0]==0: return
    df_backlog=df.dropna(subset=["Start","End","Submit"])
    df_backlog = df_backlog.drop(df_backlog[df_backlog.End=='Unknown'].index)
    df_backlog = df_backlog.drop(df_backlog[df_backlog.NodeList=='None assigned'].index)
    df_backlog=df_backlog.reset_index(drop=True)
    df_backlog["fakeStart"]=df_backlog["Start"].str[:17]+"59"
    
    if "gpu" in fileName:
        df_backlog=df_backlog.dropna(subset=["Alloc_gres/gpu"])    
    
    temp_backlog=transform_submit_start_time(df_backlog)
    print(len(temp_backlog))
    print(temp_backlog)
    if temp_backlog[0].shape[0] == 0:return 
    
    result = pd.concat(temp_backlog)
    result = result.reset_index(drop=True)
    print("!!!!")
    print(result)   
    if "gpu" in fileName:
        result_small=result.iloc[:,[0,4,9,11,15]]
        result_small.columns=["time","nodeType","partition","reqTime","user"]
    elif "rm" in fileName:
        result_small=result.iloc[:,[0,9,11,15]]
        result_small.columns=["time","partition","reqTime","user"]
    else:	
        result_small=result.iloc[:,[0,3,9,11,15]]
        result_small.columns=["time","mem","nodeType","reqTime","user"]
        
        
    result_small['time']=result_small['time'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    result_small['time']=result_small['time'].str[:-1]
    
    if "gpu" in fileName:
        result_small.to_csv("daily_logs/"+start_file+"_"+end_file+"backlog_gpu.csv")
    elif "rm" in fileName:
        result_small.to_csv("daily_logs/"+start_file+"_"+end_file+"backlog_rm.csv")
    else:
        result_small.to_csv("daily_logs/"+start_file+"_"+end_file+"backlog_lm.csv") 
    
    
    return result_small
    
    


# In[79]:


start_time = time.time()
gpu_backlog_graph_data=backlog_graph_data(sacct_gpu,df_all_gpu)
print("--- %s seconds --- for gpu_backlog_graph_data" % (time.time() - start_time))


# In[80]:


start_time = time.time()
rm_backlog_graph_data=backlog_graph_data(sacct_rm,df_all_rm)
print("--- %s seconds --- for rm_backlog_graph_data" % (time.time() - start_time))


# In[81]:


start_time = time.time()
lm_backlog_graph_data=backlog_graph_data(sacct_lm,df_all_lm)
print("--- %s seconds --- for lm_backlog_graph_data" % (time.time() - start_time))


# ### For GPU/RM/LM Interactive Jobs Graphs

# In[101]:


def process_time(df_interact):
    df_interact['Start'] = pd.to_datetime(df_interact['Start'])
    df_interact['Submit'] = pd.to_datetime(df_interact['Submit'])
    df_interact['Start']= df_interact['Start'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    df_interact['Submit']= df_interact['Submit'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
    df_interact['Start']=df_interact['Start'].str[:-1]
    df_interact['Submit']=df_interact['Submit'].str[:-1]
    df_interact["Start"]=df_interact["Start"]+".000"
    df_interact["Submit"]=df_interact["Submit"]+".000"
    return df_interact



# In[110]:


def Interact_graph_data(fileName,df): 
    df_backlog=df.dropna(subset=["Start","End","Submit"])
    if "gpu" in fileName:
        df_backlog=df.dropna(subset=["Alloc_gres/gpu"])
        
    df_backlog = df_backlog.drop(df_backlog[df_backlog.End=='Unknown'].index)
    df_backlog = df_backlog.drop(df_backlog[df_backlog.NodeList=='None assigned'].index)
    df_backlog=df_backlog.reset_index(drop=True)
    
    if "gpu" in fileName:
        df_interact=df_backlog[df_backlog['JobName']=="Interact"].loc[:,["Start","Submit","Partition","Alloc_gres/gpu","Alloc_NODE"]]
    elif "rm" in fileName:
        df_interact=df_backlog[df_backlog['JobName']=="Interact"].loc[:,["Start","Submit","Partition","Alloc_NODE"]]
    else:
        df_interact=df_backlog[df_backlog['JobName']=="Interact"].loc[:,["Start","Submit","Partition","Alloc_MEM","Alloc_NODE"]]

        
    df_interact["waittime"]=[dateutil.parser.parse(df_interact.iloc[a,:]["Start"])-dateutil.parser.parse(df_interact.iloc[a,:]["Submit"]) for a in range (df_interact.shape[0])]    
    if df_interact["waittime"].shape[0]==0:return
    df_interact["waittime"]=df_interact["waittime"].dt.total_seconds()
    df_interact=df_interact.reset_index(drop=True)
    
    if "gpu" in fileName:
        df_interact.columns=["Start","Submit","Partition","nodeType","Alloc_NODE","Waittime"]
    elif "rm" in fileName:
        df_interact.columns=["Start","Submit","Partition","Alloc_NODE","Waittime"]
    else:
        df_interact.columns=["Start","Submit","nodeType","Alloc_MEM","Alloc_NODE","Waittime"]

    df_interact=process_time(df_interact)
    df_interact=df_interact.drop(["Start"],axis=1)
    
    if "gpu" in fileName:
        df_interact.to_csv("daily_logs/"+start_file+"_"+end_file+"interact_gpu.csv")
    elif "rm" in fileName:
        df_interact.to_csv("daily_logs/"+start_file+"_"+end_file+"interact_rm.csv")        
    else:
        df_interact.to_csv("daily_logs/"+start_file+"_"+end_file+"interact_lm.csv") 
    
    return df_interact
    


# In[111]:


start_time = time.time()
gpu_interact_graph_data=Interact_graph_data(sacct_gpu,df_all_gpu)
print("--- %s seconds --- for gpu_interact_graph_data" % (time.time() - start_time))


# In[115]:


start_time = time.time()
rm_interact_graph_data=Interact_graph_data(sacct_rm,df_all_rm)
print("--- %s seconds --- for rm_interact_graph_data" % (time.time() - start_time))


# In[117]:


start_time = time.time()
lm_interact_graph_data=Interact_graph_data(sacct_lm,df_all_lm)
print("--- %s seconds --- for lm_interact_graph_data" % (time.time() - start_time))

