Create view all_data2 as select row_number() over (order by short_date)::int as id, pifirstname,pilastname,pifirstname || ' ' || pilastname as piname,telephone,email,affiliation,lat,long, department, subgrantnumber,chargeid, username,machine,
 job_id ,prorated_su_charged,to_char(short_date, 'YYYY-MM-DD') as short_date,partition,allocation,credits,debits,alloc_start,alloc_end,start_time as job_start_time,title,consultant, EXTRACT(EPOCH FROM (walltime)) as walltime, EXTRACT(EPOCH FROM (start_time-submit_time))  as wait_time,submit_time 
 from (select * 
 	   from (
 	   	     Select subgrantnumber,chargeid,pifirstname,pilastname, affiliation,department,telephone,email,username,machine,job_id ,
 	   	     prorated_su_charged,short_date,lat,long,start_time,title,consultant
 	   	     from (
 	   	     	   select * 
 	   	     	   from (
 	   	     	   	     select distinct s.subgrantnumber,s.title, sgm.chargeid, u.firstname as pifirstname, u.lastname as 
 	   	     	   	     pilastname, na.affiliation,lat,long, department,s.consultant,u.telephone,u.email 
 	   	     	   	     from users u, subgrant s, 
 	   	     	   	     subgrantmach sgm, nsfaffiliations na where s.subgrantnumber = sgm.subgrantnumber and 
 	   	     	   	     s.pipscid = u.pscid and sgm.machine like 'BRIDGES%' and u.affilcode = na.affilcode  )n1 
 	   	     	   inner join (
 	   	     	   	      select username, machine, subgrantnumber as subgrantnumber_1 from platmachuser)n2 
 	   	     	   on n1.subgrantnumber=n2.subgrantnumber_1) n4 
 	   	           left outer join (
 	   	           	      select charge_id as charge_id_1, username as username_1,machine as machine_1, job_id, 
 	   	           	      prorated_su_charged, day_run_time, short_date, start_time from prorated_jobs where machine 
 	   	           	      LIKE 'BRIDGES%' )n3 
 	   	           on n4.username = n3.username_1 and n4.chargeid = n3.charge_id_1 and n4.machine = n3.machine_1 
 	               order by job_id)n5 
 	               left outer join (
 	               	      select partition, job_id as job_id2,machine as machine_3, walltime, submit_time from jobs where machine LIKE 'BRIDGES%')n6
 	               on n5.job_id = n6.job_id2 and n6.machine_3=n5.machine) n8
                   inner join (
                   	      select allocation, credits, debits, chargeid as chargeid2, machine as machine_2,startdate as alloc_start, enddate as alloc_end 
                   	      from subgrantmach) n7 
                   on n8.chargeid=n7.chargeid2 and n7.machine_2=n8.machine;

