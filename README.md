# AI Website Builder Backend

A production-ready backend for an AI-driven Website Builder using Python (Flask), MongoDB and Gemini. Includes JWT authentication, role-based access control, AI-powered content generation, website CRUD, live preview, rate limiting, caching, and interactive API documentation.

---

## 🚀 Features
- **User Authentication** (JWT-based sign-up/login)
- **Role-Based Access Control** (Admin, Editor, Viewer)
- **AI-Powered Website Generation** (Gemini integration)
- **Website Management APIs** (CRUD, edit, retrieve)
- **Live Website Preview** (dynamic HTML template)
- **Admin APIs** (role & permission management)
- **Rate Limiting & Caching** (Flask-Limiter, Flask-Caching)
- **API Documentation** (`/api-docs`)
- **Health Check** (`/health`)

---

## 🛠️ Setup Instructions

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. **Create & Activate Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Configure Environment Variables**
Edit `config.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URI=mongodb://localhost:27017/website_builder
SECRET_KEY=supersecretkey123
FLASK_ENV=development
```

### 5. **Run MongoDB**
Make sure MongoDB is running locally:
```bash
mongod
```

### 6. **Start the Flask App**
```bash
python app.py
```

---

## 🌐 API Documentation
- **Interactive Docs:** [http://localhost:5000/api-docs](http://localhost:5000/api-docs)
- **JSON Docs:** [http://localhost:5000/api-docs/json](http://localhost:5000/api-docs/json)

---

## 🔑 Authentication & Roles
- **JWT-based**: All protected endpoints require `Authorization: Bearer <token>`
- **Roles**: Admin (full access), Editor (own websites), Viewer (read-only)

---

## 🧠 AI Content Generation
- **OpenAI**: GPT-3.5-turbo
- **Gemini**: gemini-2.5-flash
- **Switch model**: Use `"model": "openai"` or `"model": "gemini"` in `/generate-website` API

---

## 🖥️ Website Preview
- **Public Preview**: `/preview/<website_id>`
- **Authenticated Preview**: `/preview-auth/<website_id>` (JWT required)

---

## 🛡️ Security & Performance
- **Rate Limiting**: 200/day, 50/hour (default), 50/hour per user (authenticated)
- **Caching**: 5-minute cache for common responses
- **Security Headers**: XSS, content type, frame options

---

## 🩺 Health Check
- **Endpoint**: `/health`
- **Response**: `{ "status": "healthy", "message": "AI Website Builder API is running" }`

---

## 📂 Project Structure
```
├── app.py                # Main Flask app
├── models.py             # MongoDB models
├── auth.py               # Auth & JWT logic
├── admin.py              # Admin APIs
├── website.py            # Website CRUD APIs
├── ai_generator.py       # AI content generation
├── preview.py            # Website preview routes
├── middleware.py         # Rate limiting, caching, security
├── docs.py               # API documentation blueprint
├── templates/
│   ├── website_template.html
│   └── api_docs.html
├── requirements.txt
├── config.env            # Environment variables
├── README.md
└── ...
```

---

## 🤝 Contributing
Pull requests and issues are welcome!

---

## 📜 License
MIT 