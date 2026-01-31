# Complexity Assessment Criteria

This document defines the criteria used to determine the appropriate organization method for task breakdown.

---

## Decision Framework

The skill uses a complexity score (0-40) to determine the best organization method:

```python
complexity_score = (
    min(feature_count, 10) +           # Max 10 points
    min(integration_points * 2, 10) +  # Max 10 points
    min(user_roles * 2, 10) +          # Max 10 points
    min(domain_contexts * 2, 10)       # Max 10 points
)
```

---

## Organization Selection Matrix

| Score Range | Organization | Use Case |
|-------------|--------------|----------|
| 0-10 | **FLAT_LIST** | Simple, linear work |
| 11-20 | **IMPLEMENTATION_PHASE** or **COMPONENT_LAYER** | Clear phases or layers |
| 21-30 | **FEATURE_MODULE** or **HYBRID** | Multiple modules |
| 31-40 | **USER_STORY** or **HYBRID** | Multiple user roles |
| Any | **CUSTOM_INTELLIGENT** | Best practice combination |

---

## Detailed Criteria

### 1. Feature Count

| Count | Points | Organization Tendency |
|-------|--------|----------------------|
| 1-3 features | 1-3 | FLAT_LIST |
| 4-6 features | 4-6 | IMPLEMENTATION_PHASE |
| 7-10 features | 7-10 | FEATURE_MODULE |
| 10+ features | 10 | HYBRID or USER_STORY |

**Examples:**
- **Simple**: Contact form, Login page, Settings page
- **Medium**: Authentication system, Data dashboard, API wrapper
- **Complex**: E-commerce platform, CRM system, Social network

---

### 2. Integration Points

| Count | Points | Organization Tendency |
|-------|--------|----------------------|
| 0-1 integrations | 0-2 | FLAT_LIST |
| 2-3 integrations | 4-6 | IMPLEMENTATION_PHASE |
| 4-5 integrations | 8-10 | FEATURE_MODULE |
| 5+ integrations | 10 | HYBRID |

**Examples:**
- **Simple**: Database only, Database + 1 external service
- **Medium**: Database + API + Email service
- **Complex**: Payment gateway, Email, SMS, Storage, Auth provider, Multiple APIs

---

### 3. User Roles

| Count | Points | Organization Tendency |
|-------|--------|----------------------|
| 1 role | 2 | FLAT_LIST or COMPONENT_LAYER |
| 2 roles | 4 | FEATURE_MODULE |
| 3+ roles | 6-10 | USER_STORY or HYBRID |

**Examples:**
- **Simple**: User only, Admin only
- **Medium**: User + Admin, Customer + Provider
- **Complex**: User + Admin + Moderator + Manager + Superadmin

---

### 4. Domain Scope (Bounded Contexts)

| Count | Points | Organization Tendency |
|-------|--------|----------------------|
| 1 context | 2 | FLAT_LIST or IMPLEMENTATION_PHASE |
| 2 contexts | 4 | FEATURE_MODULE |
| 3+ contexts | 6-10 | FEATURE_MODULE or HYBRID |

**Examples:**
- **Simple**: Authentication only, Data processing only
- **Medium**: Authentication + User Management
- **Complex**: Authentication + Orders + Inventory + Payments + Shipping + Analytics

---

## Organization Type Characteristics

### FLAT_LIST (Score: 0-10)

**Characteristics:**
- 1-3 features
- 1-2 integration points
- Single user role
- Single domain context
- Linear workflow

**Use When:**
- Adding a single feature
- Bug fixes grouped together
- Simple enhancement
- Single-purpose tool

---

### IMPLEMENTATION_PHASE (Score: 11-20)

**Characteristics:**
- 3-6 features
- 2-4 integration points
- Clear sequential phases
- Documentation mentions phases

**Use When:**
- Feature addition with clear steps
- Migration project
- Performance optimization
- System upgrade

---

### COMPONENT_LAYER (Score: 11-20)

**Characteristics:**
- Layered architecture
- Clear separation of concerns
- Frontend/Backend/Database split

**Use When:**
- Full-stack application
- API + Frontend
- Multi-tier system

---

### FEATURE_MODULE (Score: 21-30)

**Characteristics:**
- 6+ features
- 4+ integration points
- Clear module boundaries
- Independent components

**Use When:**
- Multi-module application
- Microservices architecture
- Platform with distinct features

---

### USER_STORY (Score: 31-40)

**Characteristics:**
- Multiple user roles
- Complex workflows
- Role-based permissions
- Distinct user journeys

**Use When:**
- E-commerce platform
- CRM system
- Social network
- Multi-tenant SaaS

---

### HYBRID Types

**PHASE_MODULE_HYBRID:**
- Use when: Clear phases AND distinct modules
- Structure: Phase 1 contains Module A tasks, Phase 2 contains Module B tasks

**PHASE_USER_STORY_HYBRID:**
- Use when: Clear phases AND multiple user roles
- Structure: Phase 1: Auth stories, Phase 2: Core feature stories

**MODULE_USER_STORY_HYBRID:**
- Use when: Distinct modules AND multiple user roles
- Structure: Auth Module → Login Story, Register Story

**CUSTOM_INTELLIGENT:**
- Use when: Complex project requiring best-practice combination
- Structure: Skill determines optimal mix based on domain standards

---

## Complexity Score Calculation Examples

### Example 1: Contact Form
```
Features: 1 (contact form) = 1 point
Integrations: 1 (email service) = 2 points
User roles: 1 (visitor) = 2 points
Domain contexts: 1 (contact) = 2 points
---
Total: 7 points → FLAT_LIST
```

### Example 2: Authentication System
```
Features: 3 (login, register, password reset) = 3 points
Integrations: 2 (database, email) = 4 points
User roles: 1 (user) = 2 points
Domain contexts: 1 (auth) = 2 points
---
Total: 11 points → IMPLEMENTATION_PHASE or COMPONENT_LAYER
```

### Example 3: E-Commerce Platform
```
Features: 10+ (catalog, cart, checkout, payment, shipping, orders, reviews, etc.) = 10 points
Integrations: 6 (database, payment, email, SMS, storage, analytics) = 10 points
User roles: 4 (customer, admin, support, manager) = 8 points
Domain contexts: 6 (catalog, orders, payments, shipping, inventory, analytics) = 10 points
---
Total: 38 points → USER_STORY or HYBRID
```

### Example 4: DataChat Survey Tool
```
Features: 1 (survey analysis pipeline) = 1 point
Integrations: 2 (LLM API, PSPP) = 4 points
User roles: 1 (analyst) = 2 points
Domain contexts: 1 (survey analysis) = 2 points
---
Total: 9 points → FLAT_LIST
```

---

*End of complexity-criteria.md*
