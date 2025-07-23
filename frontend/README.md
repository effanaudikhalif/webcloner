# Frontend Setup

This is a Next.js React frontend for the Webcloner project.

## Prerequisites

- Node.js 18+ 
- npm or yarn

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser** and navigate to `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                 # Next.js app directory
│   ├── layout.tsx      # Root layout component
│   ├── page.tsx        # Main page component
│   └── globals.css     # Global styles
├── package.json         # Dependencies and scripts
├── next.config.js      # Next.js configuration
├── tsconfig.json       # TypeScript configuration
└── .eslintrc.json      # ESLint configuration
```

## Features

- **Website Cloning**: Enter a URL to clone and preview websites
- **Real-time Preview**: View the cloned website in an iframe
- **Modern UI**: Clean, responsive design with dark theme
- **TypeScript**: Full type safety throughout the application

## API Integration

The frontend communicates with the backend API running on `http://localhost:8000`. The Next.js configuration includes API rewrites to proxy requests to the backend. 