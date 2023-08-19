# habit-tracker

## Overview
[Pixela](https://pixe.la/) is an API that allows you to track a habit or effort, such as learning a new skill or training for a sport. This can then be visualised nicely via a graph:

![Pixela heat map](https://pixe.la/static/img/catch.gif)

habit-tracker allows you to interact with the Pixela API via a Lambda function. This could be called via an Alexa skill or a Zapier workflow for example.

```mermaid
graph LR;
    DataSource[/Alexa/]-->Alexa Trigger-->habit-tracker;
    DataSource[/Zapier/]-->API Gateway-->habit-tracker;
    habit-tracker-.-Pixela API;
```

## Input
The lambda function expects an action along with required arguments :

```json
    {
        "action": "create_graph",
        "graph": "test-graph",
        "description": "Graph for test case",
        "unit": "hours"
    }

```
