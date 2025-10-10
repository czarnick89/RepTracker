# RepTracker

> **Note:** This project is for portfolio and educational purposes only. It is not licensed for reuse or distribution.

RepTracker is a full-stack workout tracker app that allows users to log workouts, track exercises, sets, reps, and weights, and visualize *progress over time (under construction)*. The app integrates with Google Calendar and ExerciseDB API to enhance workout planning and tracking.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- User registration, login, and profile management
- Create and log workouts, exercises, and sets
- Track reps, weights, and workout history
- Weight change preference for exercises (increase, decrease, maintain)
- Integration with Google Calendar (to schedule workouts from the app) and ExerciseDB API (to get info/tutorials on specific exercises)
- Cookie-based JWT authentication
- Dashboard for quick overview of progress and logging
- **Comprehensive E2E testing** with Playwright and Pytest (55+ tests covering authentication, forms, and navigation)
- **Automated CI/CD pipeline** with GitHub Actions (parallel testing, caching, and production deployment)
- **Security audited** with OWASP ZAP for vulnerabilities  

## Usage

- Log in or register a new account  
<img src="docs/screenshots/Login.png" width="400" />
- Create a new workout and add exercises  
<img src="docs/screenshots/Dashboard.png" width="400" />
- Add sets with reps and weight for each exercise 
<img src="docs/screenshots/DashboardEdit.png" width="400" /> 
- Get exercise info, animated demonstrations, and instructions via ExerciseDB API call
<img src="docs/screenshots/InfoModal.png" width="400" /> 
- Sync workouts to Google Calendar  
<img src="docs/screenshots/Profile.png" width="400" /> 

## Tech Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT, Google OAuth2 integration
- **Security:** OWASP ZAP audited for vulnerabilities
- **Testing:** pytest, pytest-django, Playwright (E2E testing)
- **CI/CD:** GitHub Actions with caching and parallel execution
- **Deployment:** AWS EC2, automated deployment scripts
- **Development Tools:** Python Decouple, django-sslserver

## Database Schema

![ERD Diagram](docs/erd.png)
*Note templates aren't currently implemented.*

**Relationships Overview:**  
- Users have many Workouts  
- Workouts have many Exercises  
- Exercises have many Sets  

## Setup & Installation

1. Clone the repository:  
```
git clone https://github.com/YOURUSERNAME/RepTrack.git
```
## Backend Setup
2. Navigate to the backend directory:  
```
cd RepTracker/backend
```
3. Create a virtual environment:  
```
python -m venv venv
```
4. Activate the virtual environment:  
- Windows: `venv\Scripts\activate`  
- Mac/Linux: `source venv/bin/activate`
5. Install dependencies:  
```
pip install -r requirements.txt
```
6. Apply database migrations:  
```
python manage.py migrate
```
7. Create a superuser:  
```
python manage.py createsuperuser
```
8. Run the development server:  
```
python manage.py runserver
```
## Frontend Setup
9. Navigate to the frontend directory:  
```
cd RepTracker/frontend
```
10. Install dependencies:  
```
npm install
```
11. Run the development server:  
```
npm run dev
```
12. Open your browser at the URL shown in the terminal (usually http://localhost:5173) to view the app.

## Testing

### Backend Tests
Run backend tests with coverage:
```
cd backend
pytest --cov=. --cov-report=term --cov-fail-under=90
```

### Frontend E2E Tests
Run Playwright end-to-end tests:
```
cd frontend
npm test
```

**Test Coverage:**
- ✅ User authentication (login, register, logout)
- ✅ Form validation and error handling
- ✅ Navigation and routing
- ✅ Dashboard functionality
- ✅ Responsive design across browsers
- ✅ 55+ automated tests with CI integration

### CI/CD Testing
- **Parallel execution** of backend and frontend tests
- **Dependency caching** for faster builds (pip, npm, Playwright browsers)
- **Automated testing** on every push to main branch
- **Security scanning** with OWASP ZAP

## CI/CD Pipeline

RepTracker uses GitHub Actions for automated testing and deployment:

### Pipeline Features
- **Parallel Test Execution**: Backend and frontend tests run simultaneously
- **Dependency Caching**: 
  - Python packages (pip)
  - Node.js packages (npm)
  - Playwright browser binaries
- **Security Audits**: Automated OWASP ZAP scanning
- **Production Deployment**: Automated AWS deployment on successful tests

### Build Optimization
- **Cache Hit Rates**: 50-60% faster CI runs with dependency caching
- **Sequential Local Testing**: Prevents test interference in development
- **Verbose Logging**: Detailed test output for debugging

### Workflow Triggers
- **Push to main**: Full CI/CD pipeline (test + deploy)
- **Pull Requests**: Test-only pipeline for code review

## Deployment

### Production Environment
- **Cloud Provider**: AWS EC2
- **Security**: HTTPS with SSL certificates, security groups, SSH key-based access
- **Monitoring**: Automated deployment scripts with error handling

### Deployment Process
1. **Automated Testing**: All tests pass in CI
2. **SSH Connection**: Secure connection to production server
3. **Code Deployment**: Pull latest changes and restart services
4. **Database Migrations**: Automatic Django migrations
5. **Health Checks**: Verify application is running correctly

### Security Features
- **OWASP ZAP Audits**: Regular security vulnerability scanning
- **HTTP-only Cookies**: Secure JWT token storage
- **Environment Variables**: Sensitive data not committed to repository
- **Firewall Rules**: Restricted access with AWS security groups

## Roadmap

### Completed ✅
- User authentication and profile management
- Workout creation, editing, and tracking
- Google Calendar integration
- ExerciseDB API integration
- Comprehensive E2E testing with Playwright
- CI/CD pipeline with GitHub Actions
- Production deployment on AWS
- Security auditing with OWASP ZAP

### In Progress 🚧
- Progress visualization and analytics
- Advanced workout templates

### Planned 📋
- **Containerization**: Docker setup for consistent environments
- **Infrastructure as Code**: Terraform for AWS resource management
- **Kubernetes Orchestration**: Container deployment and scaling
- **TypeScript Migration**: Enhanced type safety for frontend
- **Advanced Analytics**: Workout progress charts and insights
- **Mobile Responsiveness**: Optimized mobile experience
- **API Rate Limiting**: Enhanced security and performance

### Stretch Features 🎯
- Social features (workout sharing, leaderboards)
- Advanced exercise recommendations
- Integration with fitness wearables
- Offline workout capabilities

## Contributing

This project is for portfolio and educational purposes only.
It is **not open for external contributions**. Any use, copying, or distribution of the code requires explicit permission from the author.

### Development Guidelines
- **Testing**: All changes must include comprehensive tests
- **Code Quality**: Follow existing patterns and conventions
- **Security**: Changes are subject to security review
- **Documentation**: Update README for significant feature changes

## License

This project is **not licensed** and is provided for **portfolio and educational purposes only**.
All rights are reserved by the author. No part of this project may be reused, copied, or distributed without explicit permission.