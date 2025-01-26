 # Python Developer Task
### Alastair Hirst

#### See this repo in action!

https://asciinema.org/a/nCW5KakSHaUByau33YdSIJfvl

 ## Overview


This repository contains 3 services that together form the image sharing application

- API, for performing CRUD operations on images and posts
- DB A postgres instance used for running and testing the application
- Inference Service, a separate microservice used for classifying images

This project uses a Makefile to easily start the services.
Since the Inference service downloads the model automatically if not found locally, you must be online
to start the inference service.

## Running the services
```bash
$ make build # Build the docker images

$ make start # Start the services

$ make migrate-head  # Run the alembic migrations

```
Once the services are up and running you can view and test the docs from their respective hosts:
API: http://localhost:8000/doc
Inference Service: http://localhost:9000/doc



## Testing
```bash

$ make coverage-tests # Run the integration tests for API 

$ make static-tests # Run linting for API

$ make attach-db # open a psql shell in postgres

$ make bash # open a bash shell in the API container

$ make bash-ai # open a bash shell in the Inference container

$ make inference-tests # Run the tests for the inference service

```


## Tasks

### Dockerization

Both services in here are dockerized. I wanted to create separate Dockerfiles for testing vs running the app,
this pattern works nicely in production where you don't want dev dependencies, or code that wipes the database.
I would also have liked to have used a multistage build for the API, to reduce the size of the final image, 
and remove poetry from the final image.

I also would have liked to use the tensorflow docker image to provide good CUDA support for the inference service,
but I was unable to get this working in time.

### CI Pipeline:
I've included a simple CI pipeline that runs against the API, running unit tests, coverage and linting (# TODO: Infernce service.)


### AI models

#### Classifier
I am using Mobile Net v2, I think it is a good all round option for real time image classification.
This is easily downloaded from tensorflow hub, and with a set of standard weights we get useful results for
image classification. There is a huge amount more that could be done here- no use of boundary boxes, no attempt to 
to analyse the output, I am just returning the raw output from the model.

In terms of performance I think it is very good. On my Mac, using CPU it processes in around 500ms, which is good enough for real time.
I would predict at least a 10x improvement on a GPU. Time is money in the cloud, so I think this model is a good fit, for 
a (presumably) non-critical task such as classifying a post.

#### Captioning

For Captioning, I have created an openai integration. I am using the 4o-mini model via API.
I didn't find any easy to use pre-trained model available out of the box. 4o-mini provides
quick and accurate image inference for around 1 cent a request. As this is an external service
performance will depend on both the internet speed + region, and the openai's response time.
It would seem to take around 1 second per request, again adequate for real time.

Testing this requires an openai API key, which naturally I have not included in this public repo.

There are also transformer based models, such as transformers from Hugging Face.
It would have been interesting to explore these, I did not find something that would work out of the box.
https://huggingface.co/docs/transformers/tasks/image_captioning


### Database schema

Getting the database schema correct is really import and this task presents some interesting challenges.
The users following/liking each other, requires a many-to-many relationship, achieved
with a junction table.

In general, I have tried to use idiomatic sqlachemy, including backpopulates, and relationships.
I have executed raw SQL to get the most liked posts. Since we need scan the entire table, we want an efficient query.
Sometimes it is useful to use raw SQL even with an ORM, especially when we have slow queries.

Indexes:

PSQL (not SQLite) creates indexes on the primary key by default, including composite PKs.
to efficiently allow query of link ID, email I have added indexes. Indexes slow down writes, but this is not normally a concern.

### microservices architecture

The decision to use two separate services gives us several benefits:

- we can reuse the inference service for other applications
- we can scale the inference service independently
- the CRUD api does not need to GPU, so we can run it on a cheaper instance
- tensorflow makes dependency management difficult; it makes the API much easier to update and maintain

#### TODO: add excalidraw ERD

### Database testing

> PostgreSQL preferred, SQLite acceptable.

When deploying an app, PSQL normally wins out over SQLite. It is more robust, and has better support for concurrent access.
Features like Enums and Partial indexes are also very useful.

Testing with SQLite is much easier, as you can just use an in memory database, and trivially wipe it between tests.
This often starts well, however with more complex projects, where the aforementioned Enums, special tools start to be used,
we can see the limitiations of this approach. N.B. that postgres also uses lower isolation levels by default than SQLite. 

For critical applications it is often desirable to have postgres testing, and I have used this here.
Between each tests we truncate all tables and restart the Pks. This is slower and also means we have to manually populate the 
database inside the tests rather than using fixtures. 
In the test we don't have enough information to really affirm any one choice, I would happily discuss this further.


Although FastAPI runs asynchronously, and I have used asyncpg, I have intentionally not used async code in the tests. This is because
this makes tests much more complex, without adding value.



Other technical points
- DI framework

