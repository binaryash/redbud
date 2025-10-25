# 🌸 Redbud

**Redbud** is a unified **Employee Management and Training Onboarding Platform** that empowers organizations to manage employees, streamline onboarding, and deliver adaptive training experiences.  
It combines structured learning workflows with **Generative AI (GenAI)** capabilities for intelligent summarization, contextual Q&A, and personalized learning support.

## 🚀 Key Features
### 🧑‍💼 Employee & Role Management

- Maintain complete **employee profiles** (personal data, roles, departments).
- Managers can **assign employees to training courses**.
- Role-based access for **managers**, **trainers**, and **trainees**.

### 🎓 Course & Training Management

- Create and manage **courses** with multiple **modules**.
- Trainers can **add modules**, upload materials, and evaluate performance.
- Trainees can **suggest or import new courses** into their learning path.

### 📘 Learning Modules & Evaluation

- Organize modules by skill area or learning objective.
- Trainers can record **evaluations** and progress metrics.
- Built-in support for multi-format training content (videos, docs, slides).

### 🤖 GenAI-Powered Learning Assistant

- **RAG-based summaries**: Generate contextual summaries of training materials.
- **Chat with GenAI** to:
  - Ask clarifying questions.
  - Get relevant information from current training modules.
  - Receive AI-guided insights for improved learning outcomes.


## 🧩 System Architecture Overview

```

[ Django Backend ]  ←→  [ REST / GraphQL API ]  ←→  [ React Frontend ]
↓                                  ↓
[ PostgreSQL / Redis ]          [ GenAI Engine + RAG Layer ]

```

- **Backend (Django):** Handles authentication, data models, API endpoints, and integrations.  
- **Frontend (React):** Delivers a modern, interactive user interface.  
- **GenAI Layer:** Manages AI summarization and conversational support.  
- **Database:** PostgreSQL for relational data and Redis (optional) for caching.


## ⚙️ Technology Stack

| Layer               | Technology                                 |
|---------------------|--------------------------------------------|
| **Frontend**        | React, JavaScript, TailwindCSS             |
| **Backend**         | Django, Django REST Framework              |
| **Database**        | PostgreSQL                                 |
| **AI Layer**        | Google Gemini-based APIs with RAG pipeline |
| **Auth & Security** | JWT / OAuth2, Role-based Access            |



## 🛠️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/binaryash/redbud.git
cd redbud
```

### 2️⃣ Backend Setup (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

Backend runs on **[http://localhost:8000](http://localhost:8000)**

### 3️⃣ Frontend Setup (React)

```bash
cd ../frontend
npm install
npm run dev
```

Frontend runs on **[http://localhost:3000](http://localhost:3000)**

---

## 🧑‍💻 Development Workflow

* Use feature branches for all new development.
* Run linting and tests before commits:

  ```bash
  npm run lint
  pytest
  ```
* Submit pull requests with clear descriptions and references to issues.

---

## 📄 License

Redbud is distributed under the **GNU GPL License**.
See the [LICENSE](LICENSE) file for details.
