# 🧠 AI Website Builder Backend

A **production-ready backend** for an AI-driven Website Builder using **Python (Flask)**, **MongoDB**, and **Gemini**.

This project includes JWT authentication, robust role-based access control, AI-powered content generation and re-generation, website CRUD operations, secure live previews, rate limiting, caching, and interactive API documentation.

---

## 🚀 Features

- ✅ **User Authentication** (JWT-based sign-up/login)
- 🛡️ **Role-Based Access Control** (Admin, Editor, Viewer)
- 🤖 **AI-Powered Website Generation** (Gemini integration for new site creation)
- ✨ **AI Website Editing** (Re-generate content of existing sites)
- 🧱 **Website Management APIs** (CRUD functionality)
- 🔐 **Secure Live Website Preview** (Authenticated dynamic HTML rendering)
- 🧑‍💼 **Admin APIs** (Role & permission management)
- ⚙️ **Rate Limiting & Caching** (Flask-Limiter, Flask-Caching)
- 📘 **Interactive API Documentation** (`/api-docs`)
- ❤️ **Health Check** (`/health`)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone git@github.com:arpan-xalxo/AI-Website-Builder-.git
cd AI-Website-Builder
```

### 2. Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` or `config.env` file in the root directory and add:

```
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URI=mongodb://localhost:27017/website_builder
SECRET_KEY=a_very_strong_and_secret_key
FLASK_ENV=development
```

### 5. Run MongoDB

Ensure MongoDB is running:

```bash
mongod
```

### 6. Start the Flask App

```bash
python app.py
```

The application will be running at: [http://localhost:5000](http://localhost:5000)

---

## 🌐 API Documentation

- **Interactive Swagger Docs**: [http://localhost:5000/api-docs](http://localhost:5000/api-docs)
- **Raw JSON Docs**: [http://localhost:5000/api-docs/json](http://localhost:5000/api-docs/json)

---

## 🔑 Authentication & Roles

**JWT-Based Authentication**  
All protected endpoints require an `Authorization: Bearer <token>` header.  
You can also pass the token as a query parameter for preview routes:
```
?token=<your_token>
```

### Roles:

- **Admin**: Full access to all APIs including user & role management.
- **Editor**: Can create, view, edit, and delete their own websites.
- **Viewer**: Can view all websites but cannot create or edit.

---

## 🧠 AI Content Generation

- **Model**: `gemini-1.5-flash`
- **Generate Website**:  
  `POST /ai/generate-website`
- **Re-generate Content**:  
  `PUT /ai/regenerate-website/<website_id>`

---

## 🖥️ Website Preview

- **Secure Preview Endpoint**:  
  `/preview/<website_id>`
- **Authentication**: Requires a valid JWT token as a query param:  
  `/preview/some_id?token=...`

---

## 🛡️ Security & Performance

- ✅ **Rate Limiting**: Default limits e.g., `200/day`, `50/hour`
- ✅ **Caching**: 5-minute cache for non-critical endpoints
- ✅ **Security Headers**: XSS protection, clickjacking prevention, etc.
- ✅ **No Circular Imports**: Centralized logic in `auth.py`

---

## 🩺 Health Check

- **Endpoint**: `/health`
- **Response**:
```json
{
  "status": "healthy",
  "message": "AI Website Builder API is running"
}
```

---

## 📂 Project Structure

```
├── app.py                # Main Flask app, blueprint registration
├── models.py             # MongoDB models (User, Role, Website)
├── auth.py               # JWT auth, permission logic
├── admin.py              # Admin-level APIs
├── website.py            # Website CRUD operations
├── ai_generator.py       # AI integration for generation/editing
├── preview.py            # Secure preview route
├── middleware.py         # Caching, rate-limiting, security headers
├── docs.py               # Swagger documentation
├── templates/
│   ├── website_template.html   # Final website view
│   ├── api_docs.html           # Swagger UI
│   ├── generate.html           # AI generation page
│   ├── edit_ai.html            # AI editing page
```

---

## 📄 License

MIT License — feel free to use, modify, and contribute.

---

## 🙌 Contributions

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.

---
