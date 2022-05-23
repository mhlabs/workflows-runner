# workflows-runner
GCP workflows runner that enable re-runs and backfills (missing feature in workflows)

Make sure to set envar environment = production if you want to use gcp logging.

## endpoints
There are two important endpoints:

@app.post("/v1/projects/{project}/locations/{location}/workflows/{workflow}/executions")
Accepts a timezone query-parameter to enable generation of timestamps with timezone offsets.
Adds a scheduleTime attribute in the body (array) that is sent to the workflow for execution, this facilitate re-runs with timestamps that are immutable.

@app.post("/range")
Accepts a body with start and stop datetimes and a step defined as a cron schedule. Returns a list of datetimes.

```
   start: datetime.datetime
   stop: datetime.datetime
   step: str # cron schedule

   {
      "start":"2022-02-15T00:00:00Z", 
      "stop":"2022-02-18T00:00:00Z", 
      "step":"0 * * * *"
   }
```


gcloud auth application-default login
gcloud beta code dev --dockerfile=./Dockerfile --application-default-credential

```sh
curl -X POST <service_url>/v1/projects/<my_project>/locations/europe-west4/workflows/workflow-1/executions?timezone=Europe/Stockholm \
   -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
   -H 'Content-Type: application/json' \
   -H 'X-CloudScheduler-ScheduleTime: 2019-10-12T07:20:50.52Z' \
   -d '[{"firstName":"first"}, {"firstName":"last"}]'

# Results in two calls to workflow with the input:
=> {"firstName":"first", "scheduleTime":"2019-10-12T08:20:50.52+01:00"}
=> {"firstName":"last", "scheduleTime":"2019-10-12T08:20:50.52+01:00"}
```

```sh
curl -X POST <service_url>/range \
   -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
   -H 'Content-Type: application/json' \
   -H 'X-CloudScheduler-ScheduleTime: 2019-10-12T07:20:50.52Z' \
   -d '{"start":"2022-02-15T00:00:00Z", "stop":"2022-02-18T00:00:00Z", "step":"0 1 * * *"}'

=> ["2022-02-15T01:00:00+00:00","2022-02-16T01:00:00+00:00","2022-02-17T01:00:00+00:00"]
```
