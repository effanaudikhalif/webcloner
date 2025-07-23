# Webcloner

A full-stack web application that clones websites using AI-powered analysis and web scraping.

## 🚀 Features

- **Website Cloning**: Clone any website by entering its URL
- **AI-Powered Analysis**: Uses Claude AI to analyze and improve cloned content
- **Real-time Preview**: View cloned websites in an interactive iframe
- **Modern UI**: Clean, responsive design with dark theme
- **Full-stack Architecture**: React frontend with FastAPI backend

## 🏗️ Architecture

```
webcloner/
├── backend/           # FastAPI Python backend
│   ├── app/          # Application code
│   ├── requirements.txt
│   └── README.md
└── frontend/         # Next.js React frontend
    ├── app/          # Next.js app directory
    ├── package.json
    └── README.md
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Anthropic Claude** - AI for content analysis
- **Playwright** - Browser automation for web scraping
- **Stagehand** - Browserbase integration
- **Python 3.12+** - Latest Python features

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **React 18** - Modern React features
- **Tailwind CSS** - Utility-first CSS framework

## 📦 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

5. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   BROWSERBASE_API_KEY=your_browserbase_api_key
   BROWSERBASE_PROJECT_ID=your_project_id
   ```

6. **Start the backend server**:
   ```bash
   cd app && uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

## 🚀 Usage

1. **Start both servers**:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

2. **Enter a website URL** in the input field

3. **Click "Generate Clone"** to start the cloning process

4. **View the preview** in the iframe below

## 🔧 Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- Environment variables are loaded from `.env` file

### Frontend Development
- Next.js App Router for modern React development
- TypeScript for type safety
- Hot reloading for fast development

## 📝 API Endpoints

- `POST /generate` - Clone a website by URL
- `GET /docs` - Interactive API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Anthropic for Claude AI integration
- Browserbase for web scraping capabilities
- Next.js team for the excellent React framework 