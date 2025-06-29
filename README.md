# Merx - A Conversational E-Commerce Agent

Merx is a shopping assistant backend powered by FastAPI, LangChain, and Google Generative AI. It provides APIs for managing user profiles, orders, and sessions, along with an AI-powered chatbot interface.

---

## Setup & Run Instructions

Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL

Installation

1. Clone the Repository:

```bash
git clone <repository-url>
cd "Conversational-AI-Customer-Service"
```

2. Set Up Environment Variables:
   Create a `.env` file in the root directory with the following content:

```env
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/postgres
GOOGLE_API_KEY=<your-google-api-key>
SECRET_KEY=<your-secret-key>
```

3. Run with Docker:
   Build and start the application using Docker Compose:

```bash
docker-compose up --build
```

4. Access the Application:
   Access the APIs test interface at http://localhost:8000.

## Populating the Database

To populate the database with sample data, run the following command:

```bash
docker-compose exec api python -m app.db.init_db
```

This will create sample users, products, and orders in the database.

However, to test the APIs, you will need to authorize, which means you need to register a user first. You can do this by sending a POST request to the `/api/auth/users` endpoint with the required user details.
There is a script that adds orders for a certain user to the database if you want to test asking the Agent about a certain order. You can run it with the following command:

```bash
docker-compose exec api python -m app.scripts.add_orders_for_user
```

Make sure to replace `<user_id>` in the script with the actual user ID you want to add orders for. The user ID can be found in the database or by registering a new user where it is returned in the response.

If you want to access the database directly, you can use the following command to connect to the PostgreSQL database:

```bash
docker-compose exec db psql -U postgres -d postgres
```

## API Documentation

Base URL

```
 `http://localhost:8000`
```

Endpoints

1. User Registration
   - Endpoint: `POST /api/auth/users`
   - Description: Register a new user.
   - Request Body:
   ```json
   {
     "email": "user@example.com",
     "name": "John Doe",
     "password": "securepassword"
   }
   ```
   - Response:
   ```json
   {
     "user_id": "7bc56007-ada0-4ca1-a640-a1fbddc16f48",
     "email": "user@example.com",
     "name": "John Doe"
   }
   ```

---

2. Login
   - Endpoint: POST /api/auth/token
   - Description: Generate an access token for authentication.
   - Request:
   ```json
   {
     "email": "user@example.com",
     "password": "securepassword"
   }
   ```
   - Response:
   ```json
   {
     "access_token": "<jwt-token>",
     "token_type": "bearer"
   }
   ```

---

3. Handle Messages
   - Endpoint: POST /messages
   - Description: Process user messages and return AI-generated responses.
   - Request:
   ```json
   {
     "message": "What is the status of my order?"
   }
   ```
   - Response:
   ```json
   {
     "response": {
       "intent": "get_order",
       "parameters": {
         "order_id": "12345"
       },
       "LLM_response": "Your order is currently being shipped."
     }
   }
   ```

---

4. Terminate Session
   - Endpoint: POST /sessions/terminate
   - Description: Clear the session state for a user. Here the session does not refer to their login session, but rather the conversation state.
   - Request:
   ```
       DELETE /sessions/7bc56007-ada0-4ca1-a640-a1fbddc16f48
   ```
   - Response:
   ```json
   {
     "detail": "Session deleted"
   }
   ```

---

You can find screenshots of API calls in the `screenshots` directory.

## Models
**Users**
Represents a user in the system.

- **Fields**:
    - user_id (UUID): Unique identifier for the user.
    - email (str): Email address of the user.
    - name (str): Name of the user.
    - hashed_password (str): Hashed password for authentication.
    - created_at (datetime): Timestamp when the user was created.

**Product**
Represents a product available in the system.

- **Fields**:
    - product_id (UUID): Unique identifier for the product.
    - name (str): Name of the product.
    - price (float): Price of the product.
    - specs (str): Specifications of the product.
    - type (str): Type/category of the product.

**Order**
Represents an order placed by a user.

- **Fields**:
    - order_id (UUID): Unique identifier for the order.
    - user_id (UUID): Identifier of the user who placed the order.
    - product_id (UUID): Identifier of the product ordered.
    - quantity (int): Quantity of the product ordered.
    - status (str): Status of the order (e.g., pending, shipped, delivered).
    - created_at (datetime): Timestamp when the order was created.

**Conversation**
Represents a conversation between the user and the chatbot. An entry to this table is created for each message sent by the user or the agent.

- **Fields**:
    - conversation_id (UUID): Unique identifier for the conversation.
    - user_id (UUID): Identifier of the user involved in the conversation.
    - message (str): Message content.
    - direction (str): Direction of the message (e.g., user or agent).
    - created_at (datetime): Timestamp when the message was sent.

## Example Chat

You can find screenshots of the chat interface and example conversations in the `screenshots` directory.
Here is a sample conversation:

```plaintext
User: can you tell me what'\''s the status of my order
```

```plaintext
Agent: Hi there! To get your order information, I just need a little more information from you. Could you please provide me with the order ID?
```

```plaintext
User: it is d0ba6eb9-167d-44bf-bbb5-ec3f7adb56f6
```

```plaintext
Agent: Your order (d0ba6eb9-167d-44bf-bbb5-ec3f7adb56f6) is currently pending. It contains 3 items and will be processed shortly.
```

```plaintext
User: okay I have another question
```

```plaintext
Okay, I'm ready for your next question.
```

```plaintext
do you have any phones that are for under 800 bucks?
```

```plaintext
Yes, I found one phone that fits your criteria: \n\n* ** Google Pixel 7 :** $799.99 (128GB storage, 5G) - In stock
```

```plaintext
User: can you update my email to zein_zein@example.com
```

```plaintext
Agent: Your email address has been successfully updated to zein_zein@example.com.
```

```plaintext
User: thanks. last thing, can you tell me what all of my orders are?
```

```plaintext
Agent: Here are your orders:\n\n* ** Order ID :** d0ba6eb9-167d-44bf-bbb5-ec3f7adb56f6 (Status: pending, Quantity: 3)\n* ** Order ID :** 5bb0ad8c-4e86-4408-9926-ac77e05db565 (Statu
s: shipped, Quantity: 1)\n* ** Order ID :** 206ad396-8dc2-43a4-8141-525fadaa3df2 (Status: delivered, Quantity: 2)
```
