# Repair Platform API

Backend for an appliance repair freelance marketplace. Connects customers who need repairs with skilled workers.

**Interactive API docs (OpenAPI/Swagger):** `http://localhost:8000/api/docs`

---

## API Overview

All endpoints are under `/api/`. Authenticated endpoints require `Authorization: Bearer <access_token>`.

Paginated list endpoints return `{"count": N, "items": [...]}` and accept `?page=N&page_size=N`.

### Auth `/api/auth/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | — | Register a new user (`user_type`: `customer` or `worker`) |
| POST | `/login` | — | Login, returns `{access, refresh}` JWT tokens |
| POST | `/refresh` | — | Refresh access token |
| POST | `/logout` | ✓ | Logout |

### Repairs `/api/repairs/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | List all repair requests (paginated) |
| GET | `/search` | — | Search by keyword, device type, status (paginated) |
| GET | `/filters` | — | Get available filter values |
| GET | `/my/requests` | ✓ | Get current user's repair requests |
| GET | `/{id}` | — | Get repair request by ID |
| POST | `/` | ✓ customer | Create repair request (multipart, supports file uploads) |
| PUT | `/{id}` | ✓ | Update repair request |
| DELETE | `/{id}` | ✓ | Delete repair request |

### Responses `/api/responses/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/request/{id}` | ✓ worker | Submit a response/bid to a repair request |
| GET | `/request/{id}` | ✓ | Get all responses for a repair request |
| GET | `/my` | ✓ worker | Get worker's own responses |
| POST | `/{id}/accept` | ✓ customer | Accept a response (auto-rejects others atomically) |

### Reviews `/api/reviews/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/request/{id}` | ✓ customer | Leave a review for a completed repair |
| GET | `/worker/{id}` | — | Get reviews for a worker (paginated) |
| GET | `/my` | ✓ customer | Get my submitted reviews |
| PUT | `/{id}` | ✓ customer | Update a review |
| DELETE | `/{id}` | ✓ customer | Delete a review |

### Users `/api/users/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/profile/me` | ✓ | Get my full profile |
| PUT | `/profile/me/info` | ✓ | Update name / email |
| PUT | `/profile/me/customer` | ✓ customer | Update customer profile |
| PUT | `/profile/me/worker` | ✓ worker | Update worker profile |
| POST | `/profile/me/avatar` | ✓ | Upload avatar (max 5 MB, JPEG/PNG/WebP/GIF) |
| POST | `/profile/me/password` | ✓ | Change password |
| GET | `/profile/me/stats` | ✓ | Get user statistics |
| GET | `/profile/me/activities` | ✓ | Activity history (paginated) |

### Chat `/api/chat/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/request/{id}` | ✓ | Send a message |
| GET | `/request/{id}` | ✓ | Get messages for a repair request |
| POST | `/request/{id}/read` | ✓ | Mark messages as read |

### Notifications `/api/notifications/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | ✓ | Get notifications |
| POST | `/{id}/read` | ✓ | Mark notification as read |

### Geolocation `/api/geo/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/location/update` | ✓ | Set my location by address (geocodes via 2GIS) |
| GET | `/location/me` | ✓ | Get my stored location |
| DELETE | `/location/me` | ✓ | Delete my location |
| GET | `/workers/nearby` | ✓ | Find workers near an address |
| GET | `/shops/parts/nearby` | ✓ | Find nearby parts shops |
| POST | `/workers/{id}/service-area` | ✓ | Add a service area for a worker |

### Bookmarks `/api/bookmarks/`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/folders` | ✓ worker | Create bookmark folder |
| GET | `/folders` | ✓ worker | List my bookmark folders |
| PUT | `/folders/{id}` | ✓ worker | Update a folder |
| DELETE | `/folders/{id}` | ✓ worker | Delete a folder |
| POST | `/bookmarks` | ✓ worker | Create bookmark on a response |
| GET | `/bookmarks` | ✓ worker | List bookmarks (supports filters) |
| GET | `/bookmarks/upcoming` | ✓ worker | Upcoming bookmarks |
| GET | `/bookmarks/stats` | ✓ worker | Bookmark statistics |
| PUT | `/bookmarks/{id}` | ✓ worker | Update bookmark |
| DELETE | `/bookmarks/{id}` | ✓ worker | Delete bookmark |

---

## Validation Rules

- **Repair request title**: max 200 characters
- **Repair request description**: max 5000 characters
- **Repair request address**: max 500 characters
- **device_type**: must be one of `fridge`, `washer`, `oven`, `dishwasher`, `other`
- **Phone number**: 7–20 characters, digits with optional `+`, spaces, dashes, parentheses
- **Password**: minimum 8 characters
- **Uploaded files** (repair requests): max 10 MB per file
- **Avatar**: max 5 MB, must be JPEG, PNG, WebP, or GIF

---

## Rate Limits

- Unauthenticated: **100 requests / hour**
- Authenticated: **1000 requests / hour**

---

Backend для платформы услуг по ремонту бытовой техники.

## 🚀 Технологии

- Django + Django Ninja
- PostgreSQL
- JWT аутентификация
- Docker + Docker Compose

## 📦 Установка и запуск

### С помощью Docker (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd repair-platform