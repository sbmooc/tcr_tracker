# Track the thing

Track the thing is an application to track status of riders and trackers during long distant endurance events, such as the Transcontinental Race. 

Work is in the early stages, so the architecture is subject to change, but it is proposed that: 

- A serverless AWS api will store most of the required functionality
- Authorization will be via OAuth
- DB will likely be an AWS RDS instance of PostgreSQL

It is proposed that there will be two types of users, a 'superuser' who are able to edit all data and see personal details and a 'volunteer' who is just able to see basic information.

API will be documented using OpenAPI3.0 specifications, and this will be used to devlop front end functionality. 

Current work is to build a working API using flask, to later migrate to AWS lambda functionality. 
