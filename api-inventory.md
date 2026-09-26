# API Inventory Per Service

> Analysis of the architecture defined in [requirements.md](requirements.md) against the current codebase.

---

## Current Implementation Status

| Service | Status | Notes |
|---|---|---|
| **API Gateway** | ✅ Implemented | JWT auth, RBAC, rate limiting, proxy, CORS, logging |
| **Auth Service** | ✅ Completed | Fully implemented (Register, Login, Refresh, Logout) |
| **User Service** | ✅ Completed | All APIs implemented (CRUD, search, pagination, me routes) |
| **Content Service** | 🟡 Bootstrapped | Base app created, `GET /api/v1/health` implemented. Core domain logic pending. |
| **Media Service** | 🔴 Not started | Can use local filesystem initially |
| **Search Service** | 🔴 Deferred | Needs Elasticsearch |
| **Notification Service** | 🔴 Deferred | Needs event bus (Kafka/Redis) |

---

## API Gateway

The gateway doesn't own business APIs — it proxies to backend services.

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | Public | ✅ Done | Gateway health check |
| `ANY` | `/api/v1/{path}` | Varies | ✅ Done | Reverse proxy to backend services |

**Gateway Responsibilities (middleware, not APIs):**

* JWT validation → 401 on invalid/missing token
* Role-based authorization → 403 on insufficient role
* Rate limiting
* CORS
* Request ID injection
* Security headers
* Request/response logging

---

## Auth Service

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | Public | ✅ Done | Service health check |
| `POST` | `/api/v1/auth/register` | Public | ✅ Done | Register new user (creates credential + calls user-service) |
| `POST` | `/api/v1/auth/login` | Public | ✅ Done | Login with email/password → returns access + refresh tokens (Opportunistic cleanup) |
| `POST` | `/api/v1/auth/refresh` | Public | ✅ Done | Exchange refresh token for new access + refresh tokens |
| `POST` | `/api/v1/auth/logout` | Authenticated | ✅ Done | Revoke & delete refresh token |
| `POST` | `/api/v1/auth/password/change` | Authenticated | ✅ Done | Change password (requires current password) |
| `POST` | `/api/v1/auth/password/forgot` | Public | 🔴 TODO | Request password reset (email flow — can be stubbed) |
| `POST` | `/api/v1/auth/password/reset` | Public (with token) | 🔴 TODO | Reset password using reset token |

---

## User Service

| Method | Path | Auth | Status | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | Public | ✅ Done | Service health check (with DB ping) |
| `POST` | `/api/v1/users` | Internal (Service Mesh) | ✅ Done | Create user (called by auth-service during registration) |
| `GET` | `/api/v1/users` | Admin | ✅ Done | List all users (paginated) |
| `GET` | `/api/v1/users/{user_id}` | Authenticated | ✅ Done | Get user by ID |
| `GET` | `/api/v1/users/me` | Authenticated | ✅ Done | Get current user's profile (resolves from JWT `sub`) |
| `PUT` | `/api/v1/users/me` | Authenticated | ✅ Done | Update current user's profile |
| `DELETE` | `/api/v1/users/{user_id}` | Admin | ✅ Done | Delete user |
| `GET` | `/api/v1/users/search` | Admin | ✅ Done | Search users |
| `PATCH` | `/api/v1/users/{user_id}` | Admin | ✅ Done | Admin update user (e.g., deactivate) |

---

## Content Service (🟡 Bootstrapped)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | Public | Service health check |
| **Posts / Articles** | | | |
| `POST` | `/api/v1/posts` | Authenticated | Create a new post/article |
| `GET` | `/api/v1/posts` | Public | List posts (paginated, filterable by tag/category/status) |
| `GET` | `/api/v1/posts/{post_id}` | Public | Get single post by ID |
| `GET` | `/api/v1/posts/slug/{slug}` | Public | Get single post by slug |
| `PUT` | `/api/v1/posts/{post_id}` | Author/Admin | Update post |
| `DELETE` | `/api/v1/posts/{post_id}` | Author/Admin | Delete post |
| `PATCH` | `/api/v1/posts/{post_id}/publish` | Author/Admin | Publish a draft post |
| `PATCH` | `/api/v1/posts/{post_id}/unpublish` | Author/Admin | Unpublish a post |
| `GET` | `/api/v1/posts/me` | Authenticated | List current user's posts |
| **Categories** | | | |
| `POST` | `/api/v1/categories` | Admin | Create category |
| `GET` | `/api/v1/categories` | Public | List all categories |
| `GET` | `/api/v1/categories/{category_id}` | Public | Get category |
| `PUT` | `/api/v1/categories/{category_id}` | Admin | Update category |
| `DELETE` | `/api/v1/categories/{category_id}` | Admin | Delete category |
| **Tags** | | | |
| `POST` | `/api/v1/tags` | Admin | Create tag |
| `GET` | `/api/v1/tags` | Public | List all tags |
| `DELETE` | `/api/v1/tags/{tag_id}` | Admin | Delete tag |
| **Comments** | | | |
| `POST` | `/api/v1/posts/{post_id}/comments` | Authenticated | Add comment to post |
| `GET` | `/api/v1/posts/{post_id}/comments` | Public | List comments for a post |
| `DELETE` | `/api/v1/comments/{comment_id}` | Author/Admin | Delete comment |

---

## Media Service (Deferred — Use Local Filesystem Initially)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | Public | Service health check |
| `POST` | `/api/v1/media/upload` | Authenticated | Upload file (image/video/document) |
| `GET` | `/api/v1/media` | Authenticated | List user's uploaded media (paginated) |
| `GET` | `/api/v1/media/{media_id}` | Public | Get media metadata |
| `GET` | `/api/v1/media/{media_id}/file` | Public | Serve/download file |
| `DELETE` | `/api/v1/media/{media_id}` | Owner/Admin | Delete media |

---

## Search Service (Deferred — Needs Elasticsearch)

> Basic search should live inside Content Service using PostgreSQL full-text search (`to_tsvector` / `to_tsquery`). Migrate to a dedicated Search Service + Elasticsearch later.

---

## Notification Service (Deferred — Needs Event Bus)

> Skip for now. When Kafka/Redis is available, this service would consume events and dispatch emails/push notifications. For now, notification-like behavior can be logged or stubbed.

---

## Recommended Build Order

| Priority | Service | Rationale |
|---|---|---|
| **1** | Content Service | Core CMS functionality — the reason this project exists |
| **2** | Media Service | Enables image uploads for posts (local FS initially) |
| **3** | Gateway updates | Add new service routes as services come online |
