# Diagrams

Rendered as Mermaid — viewable directly on GitHub, or in any Markdown
viewer/IDE with Mermaid support (VS Code with the Markdown Preview Mermaid
extension, Obsidian, etc).

## Entity Relationship Diagram (ERD)

Reflects the actual models in `app/models/` as of ES-005. Every table uses
a UUID primary key and `created_at`/`updated_at` timestamps (via
`UUIDMixin`/`TimestampMixin`), omitted below for readability.

```mermaid
erDiagram
    DEPARTMENT ||--o{ USER : "has"
    DEPARTMENT ||--o{ COURSE : "offers"
    DEPARTMENT ||--o{ LECTURER : "employs"
    USER ||--o{ REFRESH_TOKEN : "has"
    USER ||--o{ CONVERSATION : "starts"
    USER ||--o{ NOTIFICATION : "receives"
    USER ||--o{ FEEDBACK : "submits"
    USER ||--o{ AUDIT_LOG : "performs"
    CONVERSATION ||--o{ MESSAGE : "contains"
    CONVERSATION ||--o{ FEEDBACK : "relates to"
    LECTURER }o--o| USER : "may link to"

    DEPARTMENT {
        string name
        string faculty
        string hod_name
    }
    USER {
        string email
        string username
        string role
        string status
    }
    REFRESH_TOKEN {
        string token_hash
        datetime expires_at
        bool revoked
    }
    COURSE {
        string code
        string title
        string level
        string semester
        int units
    }
    LECTURER {
        string full_name
        string title
        string office
    }
    KNOWLEDGE_ARTICLE {
        string title
        string category
        text content
        string status
    }
    FAQ {
        string category
        string question
        text answer
    }
    ANNOUNCEMENT {
        string title
        string priority
        string status
    }
    EVENT {
        string title
        datetime start_time
    }
    CONVERSATION {
        string title
        string ai_provider_used
    }
    MESSAGE {
        string role
        text content
        int response_time_ms
    }
    FEEDBACK {
        int rating
        string category
    }
    ANALYTICS_EVENT {
        string event_type
        json metadata_json
    }
    AI_PROVIDER_SETTING {
        string provider
        bool is_active
        float temperature
    }
    APPLICATION_SETTING {
        string key
        text value
    }
    AUDIT_LOG {
        string action
        string resource_type
    }
    NOTIFICATION {
        string type
        string title
        bool is_read
    }
```

## Use Case Diagram

```mermaid
graph LR
    Guest((Guest))
    Student((Student))
    Lecturer((Lecturer))
    Admin((Administrator))
    SuperAdmin((Super Admin))

    Guest --> UC1[View landing page]
    Guest --> UC2[Register / Login]

    Student --> UC3[Chat with COSIB AI]
    Student --> UC4[View announcements/courses/lecturers/events]
    Student --> UC5[Manage own conversations]
    Student --> UC6[Submit feedback]
    Student --> UC7[Upload & analyze documents]

    Lecturer --> UC3
    Lecturer --> UC4
    Lecturer --> UC5
    Lecturer --> UC6
    Lecturer --> UC8[Publish announcements]
    Lecturer --> UC9[Manage events]

    Admin --> UC10[Manage users' status]
    Admin --> UC11[Manage courses/lecturers]
    Admin --> UC12[Manage knowledge base/FAQs]
    Admin --> UC13[View analytics & feedback]
    Admin --> UC14[Configure AI provider]
    Admin --> UC15[Manage system settings]

    SuperAdmin --> UC10
    SuperAdmin --> UC16[Change user roles]
    SuperAdmin --> UC17[Delete user accounts]
    SuperAdmin --> UC18[View audit logs]
```

## Sequence Diagram: Sending a Chat Message (Streaming)

```mermaid
sequenceDiagram
    participant U as Student (Browser)
    participant API as FastAPI (/chat/stream)
    participant SVC as chat_service
    participant KB as knowledge_service
    participant AIM as AIManager
    participant AI as AI Provider
    participant DB as PostgreSQL

    U->>API: POST /chat/stream {message}
    API->>SVC: get_or_create_conversation()
    SVC->>DB: INSERT Conversation (if new)
    SVC->>DB: INSERT Message (role=user)
    API->>SVC: prepare_ai_call()
    SVC->>KB: search_knowledge(message)
    KB->>DB: SELECT matching articles/FAQs/courses
    KB-->>SVC: context string
    SVC->>AIM: resolve_provider()
    AIM->>DB: SELECT active AIProviderSetting
    AIM-->>SVC: provider instance + config
    SVC-->>API: history, mode, provider, config
    API->>AI: stream(history, config)
    loop each token
        AI-->>API: token chunk
        API-->>U: SSE event: token
    end
    API->>SVC: persist_assistant_message()
    SVC->>DB: INSERT Message (role=assistant)
    SVC->>DB: INSERT AnalyticsEvent
    API-->>U: SSE event: done {suggestions}
```

## Deployment Diagram (Vercel + Railway + Supabase)

```mermaid
graph TB
    subgraph GitHub
        REPO[cosib repository]
    end

    subgraph Vercel
        STATIC[Static Site<br/>cosib-frontend<br/>Vite build output]
    end

    subgraph Railway
        WEB[Web Service<br/>cosib-backend<br/>FastAPI + Uvicorn<br/>built from backend/Dockerfile]
    end

    subgraph Supabase
        DB[(Managed PostgreSQL)]
    end

    subgraph Users
        STUDENT[Students / Lecturers]
        ADMIN[Administrators]
    end

    subgraph AIVendors["AI Vendors (optional)"]
        GEMINI[Google Gemini API]
        OPENAI[OpenAI API]
    end

    REPO -->|auto-deploy on push| WEB
    REPO -->|auto-deploy on push| STATIC
    STUDENT -->|HTTPS| STATIC
    ADMIN -->|HTTPS| STATIC
    STATIC -->|REST + SSE, HTTPS, VITE_API_BASE_URL| WEB
    WEB -->|asyncpg, TLS, DATABASE_URL| DB
    WEB -.->|if configured| GEMINI
    WEB -.->|if configured| OPENAI
    WEB -->|health check /api/v1/health| WEB
```
