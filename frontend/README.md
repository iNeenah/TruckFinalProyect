# Route Optimizer Frontend

Frontend application for the Route Optimizer system built with React, TypeScript, and Tailwind CSS.

## Features

- **Authentication System**: JWT-based authentication with role-based access control
- **Dark Mode Support**: System-aware theme switching with manual override
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **State Management**: Context API for authentication and theme management
- **API Integration**: Axios-based API client with automatic token refresh
- **Route Protection**: Protected routes with role and permission checking
- **Modern UI**: Clean, accessible interface with Heroicons

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Query** for server state management
- **Axios** for HTTP requests
- **React Hot Toast** for notifications
- **Headless UI** for accessible components
- **Heroicons** for icons

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Auth/            # Authentication components
│   ├── Layout/          # Layout components (Header, Sidebar)
│   └── UI/              # Generic UI components
├── contexts/            # React contexts
│   ├── AuthContext.tsx  # Authentication state management
│   └── ThemeContext.tsx # Theme state management
├── pages/               # Page components
│   ├── Auth/            # Authentication pages
│   ├── Dashboard/       # Dashboard page
│   ├── Routes/          # Route calculator pages
│   ├── Vehicles/        # Vehicle management pages
│   ├── Admin/           # Admin panel pages
│   └── NotFound/        # 404 page
├── services/            # API services
│   ├── apiClient.ts     # Base API client
│   └── authService.ts   # Authentication service
├── types/               # TypeScript type definitions
│   └── auth.ts          # Authentication types
├── styles/              # Global styles
│   └── globals.css      # Tailwind CSS and custom styles
├── App.tsx              # Main application component
└── main.tsx             # Application entry point
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration:
```env
VITE_API_URL=http://localhost:8000/api
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building

Build for production:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Authentication

The application uses JWT-based authentication with the following features:

- **Login/Logout**: Standard email/password authentication
- **Token Management**: Automatic token refresh and storage
- **Role-Based Access**: Admin, Manager, and Operator roles
- **Permission System**: Granular permissions for different features
- **Protected Routes**: Automatic redirection for unauthorized access

### User Roles

- **Admin**: Full system access including user management and system configuration
- **Manager**: Fleet and route management capabilities
- **Operator**: Basic route calculation and viewing permissions

## Theming

The application supports both light and dark themes with:

- **System Detection**: Automatically detects user's system preference
- **Manual Override**: Users can manually select light/dark mode
- **Persistent Storage**: Theme preference is saved in localStorage
- **CSS Variables**: Theme-aware styling throughout the application

## API Integration

The API client includes:

- **Automatic Authentication**: JWT tokens are automatically attached to requests
- **Token Refresh**: Automatic token refresh on expiration
- **Error Handling**: Centralized error handling with user-friendly messages
- **Request/Response Interceptors**: Logging and debugging capabilities
- **Retry Logic**: Automatic retry for failed requests

## Development Guidelines

### Code Style

- Use TypeScript for all new code
- Follow React functional component patterns
- Use custom hooks for reusable logic
- Implement proper error boundaries
- Write accessible HTML with proper ARIA attributes

### Component Structure

```tsx
import React from 'react';

interface ComponentProps {
  // Define props with TypeScript
}

function Component({ prop1, prop2 }: ComponentProps) {
  // Component logic
  
  return (
    <div className="tailwind-classes">
      {/* Component JSX */}
    </div>
  );
}

export default Component;
```

### State Management

- Use React Context for global state (auth, theme)
- Use React Query for server state
- Use local state (useState) for component-specific state
- Avoid prop drilling by using appropriate context

### Styling

- Use Tailwind CSS utility classes
- Create custom components for repeated patterns
- Use CSS custom properties for theme variables
- Follow mobile-first responsive design principles

## Testing

Run tests:
```bash
npm run test
```

Run tests in watch mode:
```bash
npm run test:watch
```

Generate coverage report:
```bash
npm run test:coverage
```

## Linting and Formatting

Lint code:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

Format code:
```bash
npm run format
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api` |
| `VITE_MAPBOX_ACCESS_TOKEN` | Mapbox token for maps | - |
| `VITE_NODE_ENV` | Environment mode | `development` |
| `VITE_APP_NAME` | Application name | `Route Optimizer` |
| `VITE_ENABLE_DEVTOOLS` | Enable React Query devtools | `true` |

## Contributing

1. Create a feature branch from `main`
2. Make your changes following the coding guidelines
3. Write tests for new functionality
4. Run linting and tests before committing
5. Create a pull request with a clear description

## Deployment

The application can be deployed to any static hosting service:

1. Build the application: `npm run build`
2. Deploy the `dist` folder to your hosting service
3. Configure environment variables for production
4. Set up proper routing for SPA (Single Page Application)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is proprietary software. All rights reserved.