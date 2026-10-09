# Backend Codebase Structure - Chi Tiết Mô Tả

## 📋 Tổng Quan Ứng Dụng
Ứng dụng FastAPI backend được thiết kế để xử lý tài liệu (chunks) với các chức năng chính:
- **Semantic Tagging**: Tự động phân loại tài liệu dựa trên nội dung
- **Policy Engine**: Xác định role/quyền dựa trên tags
- **Data Enrichment**: Bổ sung metadata cho tài liệu

---

## 📁 Cấu Trúc Thư Mục Chi Tiết

### 🏠 **ROOT LEVEL**

#### `requirements.txt`
**Mục đích**: Danh sách tất cả dependencies Python
**Dependencies chính**:
- `fastapi==0.136.1` - Web framework
- `sqlalchemy==2.0.49` - ORM database
- `asyncpg==0.31.0` - Async PostgreSQL driver
- `pydantic==2.13.4` - Data validation
- `httpx==0.28.1` - Async HTTP client
- `alembic==1.18.4` - Database migrations
- `python-dotenv==1.2.2` - Environment variables
- `uvicorn==0.46.0` - ASGI server

#### `alembic.ini`
**Mục đích**: Cấu hình cho Alembic (database migration tool)
**Chứa**: Script location, version locations, logging config

#### `mock_chunks.json`
**Mục đích**: Dữ liệu mock chunks để testing
**Cấu trúc**: JSON array chứa các chunks với trường:
- `id`: Unique identifier
- `content`: Nội dung tài liệu
- `processed`: Boolean flag xem đã xử lý hay chưa
- `tags`: Array của tags được gán
- `roles`: Array của roles được phân quyền

---

### 📂 **alembic/** - Database Migrations

#### `env.py`
**Mục đích**: Cấu hình Alembic environment cho async SQLAlchemy
**Chức năng chính**:
- Load environment variables từ `.env`
- Cấu hình SQLAlchemy async engine
- Định nghĩa target metadata từ models
- Chạy migrations online/offline
**Biến quan trọng**:
- `target_metadata` - Metadata từ Base (SQLAlchemy declarative base)
- `DATABASE_URL` - Connection string từ env

#### `versions/4bf42c8598ac_init_policy_tables.py`
**Mục đích**: Initial database migration (tạo bảng)
**Tables được tạo**:
1. **roles**: Lưu trữ các role/quyền
   - `id` (Primary Key)
   - `name` (String 50, unique)
   - `description` (String, nullable)

2. **tags**: Lưu trữ semantic tags
   - `id` (Primary Key)
   - `name` (String 100, unique)
   - `description` (String, nullable)
   - `sensitivity_level` (Integer)

3. **tag_role_rules**: Mapping giữa tags và roles
   - `id` (Primary Key)
   - `tag_id` (Foreign Key → tags.id)
   - `role_id` (Foreign Key → roles.id)

---

### 📂 **app/main.py** - Entry Point

**Mục đích**: Khởi tạo FastAPI app và đăng ký tất cả routers
**Chức năng**:
- Tạo instance FastAPI
- Include 5 routers chính:
  - `role_router` - Quản lý roles
  - `tag_router` - Quản lý tags
  - `tag_role_rule_router` - Quản lý mapping tag-role
  - `policy_router` - Resolve roles từ tags
  - `chunk_router` - Xử lý tài liệu chunks

---

### 📂 **app/core/** - Database Configuration

#### `database.py`
**Mục đích**: Cấu hình kết nối database async
**Biến/Hàm**:
- `DATABASE_URL` - Connection string từ environment (PostgreSQL async)
- `engine` - SQLAlchemy async engine
- `AsyncSessionLocal` - Session factory (async)
- `Base` - DeclarativeBase cho tất cả models
- `get_db()` - Dependency injection async session cho endpoints

**Công nghệ**:
- SQLAlchemy 2.0 async
- asyncpg driver cho PostgreSQL
- Echo=True (log tất cả SQL queries)

---

### 📂 **app/models/** - Database Models

#### `__init__.py`
**Mục đích**: Export tất cả models để Alembic có thể discover
**Exports**: `Role`, `Tag`, `TagRoleRule`

#### `tag.py`
**Mục đích**: ORM model cho tags
**Table**: `tags`
**Columns**:
- `id` (int, Primary Key)
- `name` (str[100], unique, required) - Tên tag
- `description` (str, optional) - Mô tả
- `sensitivity_level` (int, default=1) - Mức độ nhạy cảm của data

#### `role.py`
**Mục đích**: ORM model cho roles/permissions
**Table**: `roles`
**Columns**:
- `id` (int, Primary Key)
- `name` (str[50], unique, required) - Tên role
- `description` (str, optional) - Mô tả

#### `tag_role_rule.py`
**Mục đích**: ORM model cho mapping giữa tags và roles
**Table**: `tag_role_rules`
**Columns**:
- `id` (int, Primary Key)
- `tag_id` (int, Foreign Key) - Reference đến tag
- `role_id` (int, Foreign Key) - Reference đến role
**Mối quan hệ**: Many-to-many mapping quyết định tag nào thuộc role nào

---

### 📂 **app/schemas/** - Pydantic Validation Models

#### `tag_schema.py`
**Mục đích**: Validation schemas cho tag API requests/responses
**Models**:
- `TagCreate` - Input schema để tạo tag
  - `name` (str, required)
  - `description` (str, optional)
  - `sensitivity_level` (int, default=1)
- `TagResponse` - Output schema
  - `id`, `name`, `description`, `sensitivity_level`
  - `from_attributes=True` - Cho phép ORM model → Pydantic

#### `role_schema.py`
**Mục đích**: Validation schemas cho role API
**Models**:
- `RoleCreate` - Input schema
  - `name` (str, required)
  - `description` (str, optional)
- `RoleResponse` - Output schema
  - `id`, `name`, `description`

#### `tag_role_rule_schema.py`
**Mục đích**: Validation schemas cho tag-role rules
**Models**:
- `TagRoleRuleCreate` - Input schema
  - `tag_id` (int, required)
  - `role_id` (int, required)
- `TagRoleRuleResponse` - Output schema
  - `id`, `tag_id`, `role_id`

#### `policy_schema.py`
**Mục đích**: Validation schemas cho policy resolution API
**Models**:
- `ResolveRolesRequest` - Input schema
  - `tags` (list[str]) - List tags để resolve
- `ResolveRolesResponse` - Output schema
  - `roles` (list[str]) - List roles tương ứng

---

### 📂 **app/repositories/** - Data Access Layer

#### `tag_repository.py`
**Mục đích**: CRUD operations cho Tag model
**Methods**:
- `create(db, name, description, sensitivity_level)` - Tạo tag mới
  - Tạo Tag object, add vào session, commit, refresh
  - Return: Tag object
- `get_all(db)` - Lấy tất cả tags
  - Execute SELECT query, return scalars

#### `role_repository.py`
**Mục đích**: CRUD operations cho Role model
**Methods**:
- `create(db, name, description)` - Tạo role mới
- `get_all(db)` - Lấy tất cả roles

#### `tag_role_rule_repository.py`
**Mục đích**: CRUD operations cho TagRoleRule (mapping)
**Methods**:
- `create(db, tag_id, role_id)` - Tạo rule mới
- `get_all(db)` - Lấy tất cả rules

#### `chunk_repository.py`
**Mục đích**: Load/save chunks từ JSON file (không dùng database)
**Methods**:
- `load_chunks()` - Đọc `mock_chunks.json`
- `save_chunks(chunks)` - Ghi chunks vào file
- `get_unprocessed_chunks()` - Filter chunks chưa xử lý (processed=False)
- `update_chunk(chunk_id, updated_chunk)` - Update chunk cụ thể trong file
**Biến**:
- `MOCK_FILE = "mock_chunks.json"` - Path file mock data

---

### 📂 **app/api/v1/** - API Endpoints

#### `tag_router.py`
**Prefix**: `/tags`
**Endpoints**:
1. `POST /tags/` - Tạo tag mới
   - Input: `TagCreate`
   - Return: `TagResponse`
   - Calls: `TagRepository.create()`

2. `GET /tags/` - Lấy tất cả tags
   - Return: `list[TagResponse]`
   - Calls: `TagRepository.get_all()`

#### `role_router.py`
**Prefix**: `/roles`
**Endpoints**:
1. `POST /roles/` - Tạo role mới
2. `GET /roles/` - Lấy tất cả roles

#### `tag_role_rule_router.py`
**Prefix**: `/tag-role-rules`
**Endpoints**:
1. `POST /tag-role-rules/` - Tạo rule mapping tag-role
   - Input: `TagRoleRuleCreate` (tag_id, role_id)
   - Calls: `TagRoleRuleRepository.create()`

2. `GET /tag-role-rules/` - Lấy tất cả rules

#### `policy_router.py`
**Prefix**: `/policy`
**Endpoints**:
1. `POST /policy/resolve` - Resolve roles từ list tags
   - Input: `ResolveRolesRequest` (tags: list[str])
   - Output: `ResolveRolesResponse` (roles: list[str])
   - Calls: `PolicyEngine.resolve_roles_from_tags()`

#### `chunk_router.py`
**Prefix**: `/chunks`
**Endpoints**:
1. `GET /chunks/` - Lấy tất cả chunks
   - Calls: `ChunkRepository.load_chunks()`

2. `GET /chunks/unprocessed` - Lấy chunks chưa xử lý
   - Calls: `ChunkRepository.get_unprocessed_chunks()`

3. `POST /chunks/process` - Xử lý chunks chưa xử lý
   - Flow:
     1. Load unprocessed chunks
     2. Gọi `ChunkProcessor.process_chunk()` cho mỗi chunk
     3. Return list processed_chunks

---

### 📂 **app/services/ingestion/** - Tài Liệu Processing

#### `chunk_processor.py`
**Mục đích**: Orchestrate xử lý chunk (semantic tagging + policy resolution)
**Main Method**: `process_chunk(db, chunk)` - Async
**Processing Flow**:
1. **Semantic Tagging**: Gọi `SemanticTagger.detect_tags()`
   - Input: chunk["content"]
   - Output: list of tags

2. **Policy Resolution**: Gọi `PolicyEngine.resolve_roles_from_tags()`
   - Input: list tags
   - Output: list roles

3. **Metadata Enrichment**: Thêm vào chunk
   - `chunk["tags"]` = detected tags
   - `chunk["roles"]` = resolved roles
   - `chunk["processed"]` = True

4. **Persist**: Gọi `ChunkRepository.update_chunk()`

**Return**: Updated chunk dict

#### `semantic_tagger.py`
**Mục đích**: Detect semantic tags trong nội dung tài liệu bằng LLM
**Main Method**: `detect_tags(db, content)` - Async
**Process**:
1. Lấy danh sách allowed_tags từ DB: `TagRepository.get_all()`
2. Lấy danh sách available_roles từ DB: `RoleRepository.get_all()`
3. Build prompt: `PromptBuilder.build_semantic_tag_prompt()`
   - Input: content, allowed tags, roles
4. Gọi LLM: `LLMFactory.get_llm().generate(prompt)`
   - LLM: Ollama (gemma3:1b model)
5. Parse response: `ResponseParser.parse_json_array()`
   - Extract list tags từ JSON response
6. Return: list[str] - Detected tags

**Variables**:
- `allowed_tags` - List Tag objects từ DB
- `available_roles` - List Role objects từ DB
- `prompt` - Formatted prompt string
- `llm` - OllamaService instance
- `raw_response` - String response từ LLM
- `tags` - Parsed tags list

---

### 📂 **app/services/policy/** - Policy Resolution

#### `policy_engine.py`
**Mục đích**: Resolve roles dựa trên semantic tags
**Main Method**: `resolve_roles_from_tags(db, tags)` - Async
**SQL Logic**:
```sql
SELECT DISTINCT role.name 
FROM roles role
JOIN tag_role_rules rule ON role.id = rule.role_id
JOIN tags tag ON tag.id = rule.tag_id
WHERE tag.name IN (tags)
```
**Process**:
1. Execute SQL join query:
   - Role table JOIN with TagRoleRule
   - TagRoleRule JOIN with Tag
   - WHERE Tag.name IN (list of input tags)
2. Get distinct role names
3. Return: list[str] - Unique role names
4. Removes duplicates using `set()`

**Variables**:
- `stmt` - SQLAlchemy select statement
- `result` - Query execution result
- `roles` - List of role names

---

### 📂 **app/services/llm/** - LLM Integration

#### `base_llm.py`
**Mục đích**: Abstract base class cho LLM providers
**Class**: `BaseLLM` (ABC)
**Abstract Method**:
- `generate(prompt: str) → str` - Async
  - Mỗi LLM implementation phải implement method này

#### `llm_factory.py`
**Mục đích**: Factory pattern để tạo LLM instances
**Method**:
- `get_llm()` - Returns OllamaService instance
  - Pattern: Factory pattern cho flexibility

#### `ollama_service.py`
**Mục đích**: Integration với Ollama LLM service
**Class**: `OllamaService(BaseLLM)`
**Constructor**:
- `model` (default: "gemma3:1b") - Model name
**Main Method**: `generate(prompt)` - Async
**Process**:
1. Create async HTTP client (httpx)
2. POST request to: `http://localhost:11434/api/generate`
3. JSON payload:
   - `model`: "gemma3:1b"
   - `prompt`: Input prompt
   - `stream`: False (không stream)
   - `timeout`: 120 seconds
4. Parse JSON response
5. Return: `response["response"].strip()`

**Variables**:
- `self.model` - LLM model name
- `client` - Async HTTP client
- `response` - HTTP response
- `data` - Parsed JSON response

#### `response_parser.py`
**Mục đích**: Parse LLM responses (expected JSON array format)
**Method**: `parse_json_array(raw_response)` - Static
**Logic**:
1. Try parse raw_response as JSON
2. Nếu parsed data là list → return as is
3. Nếu lỗi hoặc không phải list → return empty list `[]`
**Return**: list[str] - Tags hoặc empty list

---

### 📂 **app/services/prompt/** - Prompt Engineering

#### `prompt_builder.py`
**Mục đích**: Build prompts cho semantic tagging LLM
**Method**: `build_semantic_tag_prompt(content, tags, roles)`
**Process**:
1. Lấy template từ `SEMANTIC_TAGGING_PROMPT`
2. Format string với:
   - `content` - Document chunk content
   - `tags` - Joined list tags (comma-separated)
   - `roles` - Joined list roles (comma-separated)
3. Return: Formatted prompt string

**Variables**:
- `content` - Document text
- `tags` - list[str] → formatted to string
- `roles` - list[str] → formatted to string

---

### 📂 **app/prompts/** - Prompt Templates

#### `semantic_tagging_prompt.py`
**Mục đích**: Template prompt cho semantic tagging task
**Template**:
```
You are an enterprise semantic governance engine.

Your task is to classify document chunks using ONLY the allowed semantic tags.

IMPORTANT RULES:
- ONLY use tags from the allowed tags list
- DO NOT invent new tags
- DO NOT explain anything
- Return ONLY a JSON array
- If no tag matches, return []

Available Roles: {roles}
Allowed Tags: {tags}

Example Output: ["salary", "employee_data"]

Chunk: {content}
```

**Format Variables**:
- `{roles}` - Available roles (for context)
- `{tags}` - Allowed tags (constraints)
- `{content}` - Document chunk to classify

---

## 🔄 Data Flow

### Chunk Processing Flow
```
/chunks/process endpoint
    ↓
ChunkProcessor.process_chunk()
    ├─ SemanticTagger.detect_tags()
    │   ├─ TagRepository.get_all() [get allowed tags]
    │   ├─ RoleRepository.get_all() [get roles context]
    │   ├─ PromptBuilder.build_semantic_tag_prompt()
    │   ├─ LLMFactory.get_llm().generate()
    │   │   └─ OllamaService POST to localhost:11434
    │   └─ ResponseParser.parse_json_array()
    │
    ├─ PolicyEngine.resolve_roles_from_tags()
    │   └─ Execute SQL JOIN query
    │
    ├─ Enrich chunk metadata
    └─ ChunkRepository.update_chunk()
```

### Tag-Role Resolution Flow
```
/policy/resolve endpoint
    ↓
PolicyEngine.resolve_roles_from_tags()
    ↓
SQL: SELECT roles WHERE tags IN (input_tags)
    ↓
Return unique roles
```

---

## 📊 Database Schema

```
TABLES:
├─ roles
│  ├─ id (PK)
│  ├─ name (unique)
│  └─ description
│
├─ tags
│  ├─ id (PK)
│  ├─ name (unique)
│  ├─ description
│  └─ sensitivity_level
│
└─ tag_role_rules
   ├─ id (PK)
   ├─ tag_id (FK→tags.id)
   └─ role_id (FK→roles.id)

RELATIONSHIPS:
roles ←→ tag_role_rules ←→ tags (M:N through junction table)
```

---

## 🔧 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI (Python web framework) |
| **Database** | PostgreSQL (via SQLAlchemy async ORM) |
| **Async** | asyncio, asyncpg |
| **Validation** | Pydantic v2 |
| **LLM** | Ollama (local LLM service) |
| **Migrations** | Alembic |
| **HTTP Client** | httpx |
| **Server** | Uvicorn (ASGI) |

---

## 🌐 Environment Variables (from .env)

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

---

## 📌 Key Variables Summary

| Variable | Type | Location | Purpose |
|----------|------|----------|---------|
| `DATABASE_URL` | str | env | PostgreSQL connection string |
| `engine` | AsyncEngine | database.py | SQLAlchemy async engine |
| `Base` | DeclarativeBase | database.py | ORM base class |
| `MOCK_FILE` | str | chunk_repository.py | Mock chunks file path |
| `allowed_tags` | list[Tag] | semantic_tagger.py | Tags from DB |
| `available_roles` | list[Role] | semantic_tagger.py | Roles from DB |
| `prompt` | str | semantic_tagger.py | Formatted LLM prompt |
| `tags` | list[str] | semantic_tagger.py | Detected tags |
| `roles` | list[str] | policy_engine.py | Resolved roles |
| `chunks` | list[dict] | chunk_repository.py | Mock chunks data |

---

## 🚀 Workflow Example

1. **User uploads document chunk**
   - Chunk added to `mock_chunks.json`
   - `processed=False`

2. **Call `/chunks/process`**
   - Load unprocessed chunks
   - For each chunk:
     - Send content to Ollama with prompt
     - Get semantic tags back
     - Query DB to find roles matching tags
     - Update chunk with tags + roles
     - Mark `processed=True`
     - Save back to JSON

3. **Result**
   - Chunk enriched with semantic tags
   - Permissions/roles assigned
   - Ready for policy enforcement

---

## 📝 Notes

- **Async-first**: Tất cả DB operations và LLM calls đều async
- **No auth**: Hiện tại không có authentication layer
- **Mock data**: Chunks lưu trong JSON, không database
- **Master data**: Tags, Roles, Rules lưu trong PostgreSQL
- **LLM-powered**: Semantic tagging dùng LLM (Ollama) để phân loại
