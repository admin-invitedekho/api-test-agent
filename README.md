# AI API Test Agent

This project implements an AI agent that uses Langchain and OpenAI to execute BDD scenarios written in Gherkin. The agent is designed to interact with APIs by calling GET, POST, PUT, and DELETE methods based on the Gherkin steps.

## Rules

1.  The agent is built using the Langchain library with OpenAI models.
2.  The programming language is Python.
3.  Tests are written in BDD (Gherkin) format in `.feature` files.
4.  Each scenario and its steps from the feature files will be passed to the AI agent to perform actions.
5.  The agent will have tools to call POST, PUT, GET, and DELETE APIs.

## Project Structure

```
api-test-agent/
├── features/                 # Gherkin feature files
│   └── example.feature
├── src/
│   ├── agent.py              # Main AI agent logic
│   └── api_tools.py          # Tools for API interactions
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```
