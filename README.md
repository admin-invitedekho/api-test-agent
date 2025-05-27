# AI API Test Agent

An intelligent API testing framework that uses AI to interpret natural language test scenarios and execute them automatically.

## Overview

This project implements an AI-powered agent that:
- Interprets BDD scenarios written in natural language
- Automatically determines the appropriate API calls to make
- Validates responses intelligently
- Provides concise, actionable feedback

## Key Features

- **Natural Language Testing**: Write tests in plain English
- **AI-Driven Execution**: Smart interpretation of test intentions
- **Minimal Logging**: Clean, focused output without redundancy
- **Flexible Validation**: Intelligent response checking

## Project Structure

```
api-test-agent/
├── features/                 # Gherkin feature files
│   ├── ai_api_tests.feature # Sample AI-driven tests
│   └── steps/               # Step definitions
│       ├── ai_steps.py      # AI-powered step handler
│       └── api_steps.py     # Compatibility layer
├── src/
│   ├── agent.py             # Main AI agent logic
│   ├── api_tools.py         # API interaction tools
│   ├── ai_step_handler.py   # AI step processing
│   └── intelligent_validator.py # Smart validation
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up your OpenAI API key in `.env`
3. Run tests: `behave features/ai_api_tests.feature`

## Philosophy

Less is more. This framework focuses on:
- Clarity over verbosity
- Intelligence over rigid rules
- Simplicity over complexity
