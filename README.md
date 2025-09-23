# Parallax

A life simulation application that uses AI to help users compare different life choices and visualize their potential outcomes over a 10-year timeline.

## Features

- **AI-Powered Life Simulations**: Generate realistic 10-year projections for major life decisions
- **Interactive Timeline Visualization**: Explore simulation results with D3-powered data visualizations
- **User Authentication**: Secure login and profile management with Clerk
- **Freemium Model**: Free tier with 3 simulations per month, premium tier with unlimited access
- **Payment Processing**: Secure payments handled through Stripe integration
- **Responsive Design**: Modern React interface with smooth animations

## Tech Stack

### Frontend

- React
- Tailwind CSS
- D3.js
- Clerk
- Stripe.js

### Backend

- Python (FastAPI)
- MongoDB
- Stripe

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- MongoDB instance
- OpenRouter API key
- Stripe account

### Environment Setup

Create environment files:

**Frontend (`frontend/.env`):**

```env
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_key
```

**Backend (`backend/.env`):**

```env
MONGODB_URI=your_mongodb_connection_string
OPENROUTER_API_KEY=your_openrouter_key
STRIPE_SECRET_KEY=your_stripe_secret_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

### Installation & Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Parallax
   ```

2. **Install frontend dependencies**

   ```bash
   cd frontend
   npm install
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
   python server.py
   ```

   Frontend (runs on port 3000):

   ```bash
   cd frontend
   npm run dev
   ```

### Testing

Run the comprehensive backend test suite:

```bash
python backend_test.py
```

The test suite validates:

- API health endpoints
- MongoDB connectivity and SSL/TLS configuration
- AI simulation functionality with realistic data
- User simulation retrieval
- Stripe payment integration
