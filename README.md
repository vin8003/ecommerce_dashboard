Project Name: E-commerce Dashboard

Description:

This Django-based project provides an API-driven E-commerce dashboard for visualizing sales data, including volume, revenue, order details, and summary metrics. It supports dynamic querying for various dimensions like date ranges, categories, and platforms.

Setup Instructions:
1.	Clone the repository to your local machine.
2.	Navigate to the project directory where the Dockerfile and docker-compose.yml are located.
3.	Build and run the containers using Docker Compose:

        docker-compose up --build

    This command builds the Docker image if it doesn’t exist and starts the containers specified in the docker-compose.yml file.

4.	After the containers are running, the web service should be accessible via http://localhost:8000.

        API Endpoints:

        GET /api/monthly-sales-volume/ - Retrieves sales volume data aggregated monthly.

        GET /api/monthly-revenue/ - Retrieves revenue data aggregated monthly.

        GET /api/orders/ - Retrieves detailed order data with support for extensive filtering.

        GET /api/summary-metrics/ - Retrieves summary metrics for the dashboard.

        POST /api/import-data/ - Allows file upload to import data into the system.


    Data Import:
    To import data, use the POST /api/import-data/ endpoint. This endpoint accepts form data with a platform specification and a file in CSV format.

    Example Curl Command for Data Import:

        curl -X POST http://localhost:8000/api/import-data/ \
        -H 'Authorization: Token your_token_here' \
        -F 'platform=flipkart' \
        -F 'file=@path_to_your_file.csv'

5.	To stop and remove the containers, use:

        docker-compose down

Note: Ensure Docker is installed and running on your machine to use Docker Compose.

Project Structure:

	/sales/ - Contains the Django app for sales data.

	/sales/models.py - Defines the data models.

	/sales/views.py - Contains the views for the API endpoints.

	/sales/serializers.py - Contains serializers for converting model instances to JSON.

	/sales/tasks.py - Contains Celery tasks for asynchronous data processing.

