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