# How to obtain the logs ( the hard way )

On the DeepRacer console under the Training or Evaluation block of your model you can go to the logs that have a name like `sim-xxxxxx`,
this are the ones that contain the *SIM_TRACE_LOG* records. Once in CloudWatch copy the **logStream** name and click on View Log Insigts. There you will have to set up the time for the query and copy this in the query form updating the **logStream**


```
fields @timestamp, @message
| filter @logStream like 'sim-#######'
| filter @message like 'SIM_TRACE'
| sort @timestamp desc
| limit 10000
```

# To analyze the logs while is trainig

```
fields @timestamp, @message
| filter @logStream like 'sim-#######'
| filter @message like 'SIM_TRACE'
| sort @timestamp desc
| parse @message "SIM_TRACE_LOG:*,*,*,*,*,*,*,*,*,*,*,*,*,*,*" as episodes,steps,x,y,heading,steering,speed,action_taken,reward,done, all_wheels_on_track, progress,closest_waypoint_index,track_length,time
| sort by progress desc
| limit 1000
```

Find the highest progress of an episode
```
fields @message 
| filter @logStream like 'sim-######'
| filter @message like 'SIM_T'
| parse @message "SIM_TRACE_LOG:*,*,*,*,*,*,*,*,*,*,*,*,*,*,*" as episodes,steps,x,y,heading,steering,speed,action_taken,reward,done, all_wheels_on_track, progress,closest_waypoint_index,track_length,time
| sort by progress desc
| display episodes, progress, steps, reward, time
| limit 100
```

Make a histogram of a variable
```
fields @message 
| filter @logStream like 'sim-####'
| filter @message like 'SIM_T'
| parse @message "SIM_TRACE_LOG:*,*,*,*,*,*,*,*,*,*,*,*,*,*,*" as episodes,steps,x,y,heading,steering,speed,action_taken,reward,done, all_wheels_on_track, progress,closest_waypoint_index,track_length,time
| sort by progress desc
| stats count(*) by steering, speed
| limit 100
```

Find out how much is taking a lap
```
fields @message 
| filter @logStream like 'sim-######'
| filter @message like 'SIM_T'
| parse @message "SIM_TRACE_LOG:*,*,*,*,*,*,*,*,*,*,*,*,*,*,*,*" as episodes,steps,x,y,heading,steering,speed,action_taken,reward,done, all_wheels_on_track, progress,closest_waypoint_index,track_length,time,status
| stats min(time) as m, max(time) as M, max(progress) as p, max(time) - min(time) as  t by episodes
| limit 100
| display episodes, t , p 
| sort t desc
```