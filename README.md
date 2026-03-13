# Parallax

A life simulation application that uses AI and machine learning to help users compare different life choices and visualize their potential outcomes over a 10-year timeline.

**Live Demo**: [myparallax.vercel.app](https://myparallax.vercel.app)

## Features

- **AI-Powered Life Simulations**: Generate realistic 10-year projections for major life decisions
- **ML Prediction Engine**: XGBoost and TensorFlow models for career and salary predictions
- **Monte Carlo Simulations**: Statistical scenario modeling for outcome distributions
- **Interactive Timeline Visualization**: Explore simulation results with data visualizations
- **User Authentication**: Secure login and profile management with Clerk
- **Freemium Model**: Free tier with limited simulations, premium tier with unlimited access
- **Payment Processing**: Secure payments handled through Stripe integration
- **Responsive Design**: Modern React interface with Framer Motion animations

## Tech Stack

### Frontend

- React 19 + TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Clerk (auth)
- Stripe.js

### Backend

- Python 3.11+ (FastAPI)
- MongoDB Atlas (Motor async driver)
- Pydantic

### ML Pipeline

- XGBoost
- TensorFlow / Keras
- scikit-learn

### AI

- OpenRouter API (Claude, GPT-4)

### DevOps & Infrastructure

- Docker
- Vercel (frontend)
- Railway (backend)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- MongoDB Atlas instance
- OpenRouter API key
- Clerk account
- Stripe account

### Environment Setup

Create environment files:

**Frontend (`frontend/.env`):**

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key
VITE_REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_key
```

**Backend (`backend/.env`):**

```env
MONGO_URL=your_mongodb_connection_string
DB_NAME=parallax
OPENROUTER_API_KEY=your_openrouter_key
STRIPE_SECRET_KEY=your_stripe_secret_key
CLERK_JWKS_URL=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json
CORS_ORIGINS=http://localhost:5173
```

### Installation & Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/AndrewL05/Parallax.git
   cd Parallax
   ```

2. **Install frontend dependencies**

   ```bash
   cd frontend
   yarn install
   ```

3. **Install backend dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Start development servers**

   Backend (runs on port 8000):

   ```bash
   cd backend
   uvicorn server:app --reload --port 8000
   ```

   Frontend (runs on port 5173):

   ```bash
   cd frontend
   yarn dev
   ```

### Docker

```bash
docker-compose up --build
```

### Testing

```bash
cd backend
python -m pytest tests/ -v
```
