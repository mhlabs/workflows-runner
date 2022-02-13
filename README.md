# datahem.astro
GCP Astro data integration using FastApi on cloud run and pubsub

gcloud auth application-default login
gcloud beta code dev --dockerfile=./Dockerfile --application-default-credential

Build locally (on Mac m1)
```sh
docker build -t my-app --platform=linux/amd64 .
```

Run locally (make sure you have credentials file in the path)
```sh
GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/gcp_credentials.json
docker run -d \                                    
-p 8080:8080 \
-e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/gcp_credentials.json \
-v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/gcp_credentials.json:ro \
-e DRIVER='DRIVER={ODBC Driver 17 for SQL Server};SERVER=<host>;PORT=1443;DATABASE=veddesta;UID=<user>;PWD=<password>;ApplicationIntent=ReadOnly' \
my-app
```

```sh
curl -X POST http://0.0.0.0:8081/v1/projects/project/locations/location/workflows/workflow/executions \
   -H 'Content-Type: application/json' \
   -H 'X-CloudScheduler-ScheduleTime: 2019-10-12T07:20:50.52Z' \
   -d '{"query":"select top 60000 10 as storeid, L62T1.partno from malmo.dbo.L62T1;", "topic_id":"fastapi-astro", "project_id":"mathem-ml-datahem-test"}'
```
curl -X POST http://0.0.0.0:8081/v1/projects/mathem-ml-datahem-test/locations/europe-west4/workflows/workflow-1/executions \
   -H 'Content-Type: application/json' \
   -H 'X-CloudScheduler-ScheduleTime: 2019-10-12T07:20:50.52Z' \
   -d '{"query":"select top 60000 10 as storeid, L62T1.partno from malmo.dbo.L62T1;", "topic_id":"fastapi-astro", "project_id":"mathem-ml-datahem-test", "firstName":"first"}'