# Alternity Backend

This is the backend for the Alternity MBTI analysis application.

## Running with Docker

To run the application with Docker, follow these steps:

### 1. Build the Docker image

Open your terminal in the root directory of the project and run the following command to build the Docker image:

```bash
docker build -t alternity-backend .
```

### 2. Create a `.env` file

Create a file named `.env` in the root of the project and add your Gemini API key to it:

```
GEMINI_API_KEY="your_gemini_api_key_goes_here"
```

> **Note:** The `.env` file is included in `.gitignore` to prevent accidentally committing your secret keys.

### 3. Run the Docker container

After the image is built, run the following command to start the container. This command uses the `--env-file` flag to load your API key from the `.env` file.

```bash
docker run -d -p 5001:5001 --env-file .env alternity-backend
```

The application will be available at `http://localhost:5001`. 