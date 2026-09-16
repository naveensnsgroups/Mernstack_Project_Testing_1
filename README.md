# MERN Stack Project Testing 1

An Express and MongoDB REST API for managing employee personal details. The backend includes request validation, rate limiting, secure HTTP headers, CORS controls, and input sanitization.

## Prerequisites

- Node.js 18 or later
- A MongoDB database (local MongoDB or MongoDB Atlas)

## Setup

1. Install dependencies:

   ```powershell
   cd backend
   npm install
   ```

2. Create `backend/.env` from the provided example and set your own database connection string:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Start the development server:

   ```powershell
   npm run dev
   ```

   The API runs at `http://localhost:5000` by default.

## Environment variables

Set these values in `backend/.env`. Never commit this file.

| Variable | Purpose |
| --- | --- |
| `MONGO_URI` | MongoDB connection string |
| `PORT` | API port (defaults to `5000`) |
| `NODE_ENV` | Runtime environment, such as `development` |
| `CLIENT_URL` | Allowed frontend origin; separate multiple origins with commas |

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `GET` | `/api/employees` | List employees; supports `page` and `limit` query parameters |
| `GET` | `/api/employees/:id` | Get one employee |
| `POST` | `/api/employees` | Create an employee |
| `PUT` | `/api/employees/:id` | Update an employee |
| `DELETE` | `/api/employees/:id` | Delete an employee |

## Employee payload example

```json
{
  "fullName": "Jane Doe",
  "employeeId": "EMP001",
  "email": "jane.doe@snsgroups.com",
  "phone": "9876543210",
  "department": "IT",
  "position": "Developer",
  "gender": "Female",
  "dateOfBirth": "1998-01-15",
  "joinDate": "2024-06-01",
  "address": "Coimbatore"
}
```

`employeeId` must start with `EMP`, and employee emails must use the `@snsgroups.com` domain.

## Production start

```powershell
cd backend
npm start
```
