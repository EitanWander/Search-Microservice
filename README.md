# Search-Microservice
 
## Requirements

This project requires the following Python packages:

- asyncpg
- python-dotenv

## Installation

Install the required packages using pip:

```
pip install asyncpg python-dotenv
```

## Environment Variables

The following environment variables are used (with defaults):
- DB_USER (default: testuser)
- DB_PASSWORD (default: testpass)
- DB_HOST (default: localhost)
- DB_PORT (default: 5432)
- DB_NAME (default: my_app_db)

You can set these in a `.env` file in the project root.