# 📊 Training Data Template for Task Generation

This file contains templates and examples for creating high-quality training data for your LLM task generation system.

## 🎯 Training Data Schema

```json
{
  "id": "unique_identifier",
  "user_input": "Brief user description",
  "position": "backend|frontend|qa|devops|pm|designer",
  "task_type": "feature|bug_fix|improvement|technical_debt|research",
  "context": {
    "project_name": "Project Name",
    "component": "Component Name",
    "sprint": "Sprint Info",
    "team_size": "Number"
  },
  "expected_output": {
    "title": "Clear, actionable title",
    "description": "Detailed description with context",
    "acceptance_criteria": ["Criterion 1", "Criterion 2", "..."],
    "story_points": "1|2|3|5|8|13",
    "priority": "High|Medium|Low",
    "labels": ["tag1", "tag2", "..."],
    "component": "Component name",
    "user_story": "As a ... I want ... So that ...",
    "technical_notes": "Implementation details",
    "dependencies": ["Dependency 1", "..."],
    "risks": ["Risk 1", "..."]
  }
}
```

## 🔥 High-Quality Training Examples

### Backend Development Examples

```json
{
  "id": "backend_001",
  "user_input": "api endpoint for user preferences",
  "position": "backend",
  "task_type": "feature",
  "context": {
    "project_name": "E-commerce Platform",
    "component": "User Management API",
    "sprint": "Sprint 12"
  },
  "expected_output": {
    "title": "Implement user preferences API endpoint",
    "description": "Create a RESTful API endpoint to allow users to save and retrieve their application preferences such as theme, language, notification settings, and display options. The endpoint should support CRUD operations and maintain user data privacy.",
    "acceptance_criteria": [
      "GET /api/users/{id}/preferences returns user preferences in JSON format",
      "PUT /api/users/{id}/preferences updates user preferences with validation",
      "POST /api/users/{id}/preferences creates default preferences for new users",
      "DELETE /api/users/{id}/preferences resets preferences to default values",
      "Preferences are validated against predefined schema",
      "Only authenticated users can access their own preferences",
      "API returns appropriate HTTP status codes and error messages",
      "All endpoints are documented in OpenAPI/Swagger",
      "Unit tests cover all CRUD operations and edge cases"
    ],
    "story_points": "5",
    "priority": "Medium",
    "labels": ["api", "backend", "user-management", "preferences"],
    "component": "User Management API",
    "user_story": "As a user I want to customize my application preferences so that I can have a personalized experience",
    "technical_notes": "Use PostgreSQL for storage, implement caching with Redis, follow existing API patterns",
    "dependencies": ["User authentication service", "Database schema migration"],
    "risks": ["Performance impact with large preference objects", "Data migration for existing users"]
  }
}
```

```json
{
  "id": "backend_002",
  "user_input": "fix memory leak in payment service",
  "position": "backend",
  "task_type": "bug_fix",
  "context": {
    "project_name": "Payment Platform",
    "component": "Payment Processing Service",
    "sprint": "Hotfix"
  },
  "expected_output": {
    "title": "Fix memory leak in payment processing service",
    "description": "The payment service is experiencing memory leaks that cause gradual performance degradation and eventual service crashes under high load. Memory usage increases continuously during payment processing and doesn't release properly after transaction completion. This affects system stability and customer experience during peak hours.",
    "acceptance_criteria": [
      "Memory usage remains stable during load testing with 1000+ concurrent transactions",
      "No memory leaks detected using profiling tools (JProfiler/VisualVM)",
      "Service maintains consistent response times under sustained load",
      "Memory monitoring shows proper garbage collection patterns",
      "Unit tests verify proper resource cleanup in all code paths",
      "Integration tests confirm memory stability over 24-hour periods",
      "Performance metrics show no degradation after extended usage",
      "Production monitoring alerts are updated to track memory usage"
    ],
    "story_points": "8",
    "priority": "High",
    "labels": ["bug", "memory-leak", "payment", "performance", "critical"],
    "component": "Payment Processing Service",
    "user_story": "As a system administrator I want the payment service to maintain stable memory usage so that the system remains reliable during peak transaction periods",
    "technical_notes": "Focus on connection pooling, object lifecycle management, and proper resource disposal",
    "dependencies": ["Access to production monitoring tools", "Load testing environment"],
    "risks": ["Service downtime during investigation", "Potential impact on other services"]
  }
}
```

### Frontend Development Examples

```json
{
  "id": "frontend_001",
  "user_input": "responsive dashboard layout",
  "position": "frontend",
  "task_type": "feature",
  "context": {
    "project_name": "Analytics Dashboard",
    "component": "Dashboard UI",
    "sprint": "Sprint 8"
  },
  "expected_output": {
    "title": "Implement responsive dashboard layout with grid system",
    "description": "Create a responsive dashboard layout that adapts seamlessly across desktop, tablet, and mobile devices. The dashboard should use a flexible grid system to reorganize widgets and charts based on screen size while maintaining usability and visual hierarchy.",
    "acceptance_criteria": [
      "Dashboard displays correctly on desktop (1920x1080+), tablet (768-1024px), and mobile (320-767px)",
      "Widget grid automatically reflows and stacks appropriately on smaller screens",
      "All charts and graphs remain readable and interactive on touch devices",
      "Navigation menu collapses to hamburger menu on mobile devices",
      "Typography scales appropriately for different screen sizes",
      "Touch targets meet minimum 44px accessibility standards",
      "Page loading performance remains optimal across all device types",
      "Cross-browser compatibility verified on Chrome, Firefox, Safari, Edge",
      "Responsive design tested on actual devices, not just browser dev tools"
    ],
    "story_points": "8",
    "priority": "High",
    "labels": ["frontend", "responsive", "dashboard", "mobile", "ui"],
    "component": "Dashboard UI",
    "user_story": "As a user I want to access my dashboard on any device so that I can monitor my data wherever I am",
    "technical_notes": "Use CSS Grid and Flexbox, implement mobile-first approach, consider using React breakpoint hooks",
    "dependencies": ["Design system components", "Chart library mobile optimization"],
    "risks": ["Performance impact on mobile devices", "Complex chart interactions on touch screens"]
  }
}
```

### QA Testing Examples

```json
{
  "id": "qa_001",
  "user_input": "test automation for checkout flow",
  "position": "qa",
  "task_type": "improvement",
  "context": {
    "project_name": "E-commerce Platform",
    "component": "Checkout Process",
    "sprint": "Sprint 15"
  },
  "expected_output": {
    "title": "Implement automated test suite for checkout flow",
    "description": "Create comprehensive automated tests for the entire checkout process including cart management, payment processing, shipping calculations, and order confirmation. Tests should cover happy path scenarios, edge cases, and error conditions to ensure checkout reliability.",
    "acceptance_criteria": [
      "Automated tests cover complete checkout flow from cart to confirmation",
      "Tests include multiple payment methods (credit card, PayPal, digital wallet)",
      "Different shipping options and tax calculations are validated",
      "Error scenarios are tested (payment failures, inventory issues, network errors)",
      "Tests run in CI/CD pipeline and block deployments on failures",
      "Test data is properly managed and cleaned up after test runs",
      "Tests execute in under 10 minutes for the full suite",
      "Test reports include clear failure descriptions and screenshots",
      "Tests are maintainable and use page object model pattern"
    ],
    "story_points": "13",
    "priority": "High",
    "labels": ["qa", "automation", "checkout", "testing", "ci-cd"],
    "component": "Checkout Process",
    "user_story": "As a QA engineer I want automated checkout tests so that we can catch regressions quickly and deploy with confidence",
    "technical_notes": "Use Selenium/Playwright, implement data-driven tests, integrate with existing CI/CD pipeline",
    "dependencies": ["Test environment setup", "Test data management system"],
    "risks": ["Test flakiness due to timing issues", "Maintenance overhead for UI changes"]
  }
}
```

## 📋 Training Data Collection Template

Use this template to collect examples from your team:

```markdown
## Training Example Request

**Instructions**: Please provide a high-quality example of a task you would want the AI to generate.

### Input Information
- **What did you type/say?**: _Brief description like "fix login bug"_
- **Your role**: _backend/frontend/qa/devops/pm/designer_
- **Task type**: _feature/bug_fix/improvement/technical_debt/research_
- **Project context**: _What project/component is this for?_

### Expected Output
Please write what the PERFECT task description would look like:

**Title**: _Clear, actionable title_

**Description**: _Detailed explanation with context_

**Acceptance Criteria** (3-8 specific, testable criteria):
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Additional Info**:
- **Story Points**: _1, 2, 3, 5, 8, or 13_
- **Priority**: _High/Medium/Low_
- **Labels**: _Relevant tags_
- **Dependencies**: _What needs to be done first?_
- **Risks**: _What could go wrong?_

---

**Why is this example important?**: _What makes this a good example for training?_
```

## 🎯 Data Quality Checklist

### ✅ Good Training Examples Have:
- **Clear Intent**: User input clearly indicates what they want
- **Appropriate Scope**: Task is neither too large nor too small
- **Specific Details**: Description provides context and rationale
- **Testable Criteria**: Acceptance criteria can be objectively verified
- **Realistic Estimates**: Story points reflect actual complexity
- **Proper Categorization**: Labels and priority make sense
- **Complete Information**: All required fields are filled thoughtfully

### ❌ Avoid These Common Issues:
- **Vague Input**: "make it better" or "fix stuff"
- **Missing Context**: No information about the component or project
- **Weak Acceptance Criteria**: "should work" or "user is happy"
- **Inconsistent Format**: Different structures across examples
- **Unrealistic Scope**: Tasks that are too big or too small
- **Generic Descriptions**: Could apply to any project

## 🚀 Getting Started

1. **Start Small**: Create 10-15 high-quality examples covering your most common scenarios
2. **Get Team Input**: Ask different team members to contribute examples from their domain
3. **Test Early**: Use these examples to improve your prompt engineering first
4. **Iterate**: Collect feedback and refine your examples over time
5. **Scale Up**: Gradually build to 50-100 examples for fine-tuning

Remember: Quality over quantity! 20 excellent examples will give you better results than 100 mediocre ones.
