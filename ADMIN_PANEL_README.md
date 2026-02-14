# CivicQ Admin Panel

A comprehensive administrative interface for city staff and moderators to manage CivicQ's civic engagement platform.

## Overview

The CivicQ Admin Panel is a full-featured moderation and management system designed to handle 10,000+ voters efficiently. It provides city staff, moderators, and administrators with powerful tools to manage questions, users, content, elections, and analytics.

## Features

### 1. Dashboard
- **Real-time Statistics**: Total users, active users (24h), questions, answers, votes
- **Engagement Metrics**: Platform engagement rate and activity trends
- **System Alerts**: High-priority notifications for pending queues and reports
- **Recent Activity Feed**: Live audit log of moderation actions
- **Quick Actions**: One-click access to moderation queues

**Location**: `/admin`
**Component**: `/frontend/src/pages/admin/AdminDashboard.tsx`

### 2. Question Moderation
- **Pending Queue**: Review all pending questions with pagination
- **Bulk Operations**: Approve or reject multiple questions at once
- **Duplicate Detection**: Find and merge duplicate questions
- **Smart Filtering**: Search and filter by status, tags, date
- **Moderation History**: Track all actions with audit trail

**Features**:
- Approve questions with optional notes
- Reject questions with reason codes
- Merge duplicates into target questions
- Find similar questions automatically
- Bulk approve/reject up to 100 items

**Location**: `/admin/questions`
**Component**: `/frontend/src/pages/admin/QuestionModeration.tsx`

### 3. User Management
- **User Database**: Search and filter all platform users
- **Role-based Views**: Filter by voter, candidate, moderator, admin
- **Activity Tracking**: View questions submitted, votes cast, reports filed
- **Moderation Actions**:
  - Warn users (first offense)
  - Suspend users (temporary ban with duration)
  - Ban users (permanent removal)
  - Restore users (undo suspension/ban)
- **User History**: View all warnings and moderation history

**Location**: `/admin/users`
**Component**: `/frontend/src/pages/admin/UserManagement.tsx`

### 4. Content Moderation
- **Report Queue**: Review all flagged content
- **Report Types**: Questions, answers, rebuttals, user behavior
- **Action Options**:
  - Resolve and remove content
  - Dismiss reports as false positives
  - Review detailed report information
- **Bulk Resolution**: Process multiple reports simultaneously

**Location**: `/admin/content`
**Component**: `/frontend/src/pages/admin/ContentModeration.tsx`

### 5. Analytics Dashboard
- **Answer Coverage**: Track what percentage of questions have answers
- **Trending Topics**: View most popular issue tags
- **User Demographics**: Users by city and verification status
- **Export Options**: Download analytics as CSV or JSON
- **Time-series Data**: Daily active users, question submissions, vote activity

**Location**: `/admin/analytics`
**Component**: `/frontend/src/pages/admin/Analytics.tsx`

### 6. City Configuration
- **Election Management**:
  - Create new elections
  - Set election dates and deadlines
  - Activate/deactivate elections
  - Manage election metadata
- **City Settings**:
  - Configure moderation mode (auto/manual/hybrid)
  - Enable/disable features
  - Set verification requirements
  - Custom branding options
- **Ballot Import**: Import ballot data from external APIs

**Location**: `/admin/config`
**Component**: `/frontend/src/pages/admin/CityConfiguration.tsx`

### 7. Audit Log
- **Complete Audit Trail**: Every admin action is logged
- **Filter & Search**: Filter by event type, severity, date range
- **Export Logs**: Download complete audit logs for compliance
- **Event Types**:
  - Moderation actions
  - User management
  - System events
  - Security alerts

**Location**: `/admin/audit`
**Component**: `/frontend/src/pages/admin/AuditLog.tsx`

## Role-Based Access Control (RBAC)

### Permissions System

The admin panel implements a granular permission system:

```typescript
enum AdminPermission {
  VIEW_DASHBOARD = 'view_dashboard',
  MODERATE_QUESTIONS = 'moderate_questions',
  MODERATE_CONTENT = 'moderate_content',
  MANAGE_USERS = 'manage_users',
  VIEW_ANALYTICS = 'view_analytics',
  MANAGE_CITY_CONFIG = 'manage_city_config',
  VIEW_AUDIT_LOG = 'view_audit_log',
  MANAGE_ELECTIONS = 'manage_elections',
  BULK_OPERATIONS = 'bulk_operations',
}
```

### Role Permissions

| Permission | Admin | City Staff | Moderator |
|------------|-------|------------|-----------|
| View Dashboard | ✓ | ✓ | ✓ |
| Moderate Questions | ✓ | ✓ | ✓ |
| Moderate Content | ✓ | ✓ | ✓ |
| Manage Users | ✓ | ✗ | ✗ |
| View Analytics | ✓ | ✓ | ✓ |
| Manage City Config | ✓ | ✓ | ✗ |
| View Audit Log | ✓ | ✓ | ✗ |
| Manage Elections | ✓ | ✓ | ✗ |
| Bulk Operations | ✓ | ✓ | ✗ |

**Permission Hook**: `/frontend/src/hooks/usePermissions.ts`
**Route Guard**: `/frontend/src/components/admin/AdminRoute.tsx`

## Architecture

### Frontend Structure

```
frontend/src/
├── pages/admin/
│   ├── AdminDashboard.tsx          # Main dashboard with stats
│   ├── QuestionModeration.tsx      # Question approval/rejection
│   ├── UserManagement.tsx          # User moderation
│   ├── ContentModeration.tsx       # Content flagging/reports
│   ├── Analytics.tsx               # Analytics & insights
│   ├── CityConfiguration.tsx       # Election/city settings
│   ├── AuditLog.tsx               # Audit trail viewer
│   └── index.ts                    # Exports
├── components/admin/
│   ├── AdminLayout.tsx             # Main layout with sidebar
│   ├── AdminRoute.tsx              # Permission guard
│   ├── DataTable.tsx               # Reusable table component
│   ├── BulkActionBar.tsx          # Bulk operation UI
│   ├── StatCard.tsx               # Dashboard stat cards
│   ├── Modal.tsx                  # Modal dialog
│   └── index.ts                    # Exports
├── services/
│   └── adminApi.ts                 # Admin API client
├── hooks/
│   └── usePermissions.ts           # RBAC hook
└── types/
    └── index.ts                    # TypeScript types (extended)
```

### Backend Structure

```
backend/app/
├── api/
│   ├── admin.py                    # Original ballot import endpoints
│   └── admin_moderation.py         # NEW: Moderation endpoints
├── models/
│   ├── user.py                     # User & roles
│   ├── question.py                 # Questions & votes
│   ├── answer.py                   # Video answers
│   └── moderation.py               # Reports, actions, audit logs
└── core/
    └── security.py                 # Auth & RBAC (updated)
```

## API Endpoints

### Dashboard
- `GET /api/admin/stats` - Get dashboard statistics
- `GET /api/admin/alerts` - Get system alerts
- `GET /api/admin/activity` - Get recent audit log

### Question Moderation
- `GET /api/admin/questions/pending` - Get pending questions (paginated)
- `POST /api/admin/questions/{id}/approve` - Approve question
- `POST /api/admin/questions/{id}/reject` - Reject question
- `POST /api/admin/questions/merge` - Merge duplicate questions
- `POST /api/admin/questions/bulk-approve` - Bulk approve
- `POST /api/admin/questions/bulk-reject` - Bulk reject
- `GET /api/admin/questions/{id}/duplicates` - Find duplicates

### User Management
- `GET /api/admin/users` - Get users (paginated, filtered)
- `GET /api/admin/users/{id}/activity` - Get user activity
- `POST /api/admin/users/{id}/warn` - Warn user
- `POST /api/admin/users/{id}/suspend` - Suspend user
- `POST /api/admin/users/{id}/ban` - Ban user
- `POST /api/admin/users/{id}/restore` - Restore user
- `POST /api/admin/users/bulk-action` - Bulk user actions

### Content Moderation
- `GET /api/admin/reports` - Get content reports (paginated)
- `GET /api/admin/reports/{id}` - Get report details
- `POST /api/admin/reports/{id}/resolve` - Resolve report
- `POST /api/admin/reports/{id}/dismiss` - Dismiss report
- `POST /api/admin/content/flag` - Flag content
- `POST /api/admin/content/remove` - Remove content
- `POST /api/admin/reports/bulk-resolve` - Bulk resolve

### Analytics
- `GET /api/admin/analytics` - Get analytics data
- `GET /api/admin/analytics/engagement` - Get engagement metrics
- `GET /api/admin/analytics/trending` - Get trending topics
- `GET /api/admin/analytics/export` - Export analytics (CSV/JSON)

### City Configuration
- `GET /api/admin/elections` - Get elections
- `POST /api/admin/elections` - Create election
- `PUT /api/admin/elections/{id}` - Update election
- `DELETE /api/admin/elections/{id}` - Delete election
- `GET /api/admin/cities/{id}/settings` - Get city settings
- `PUT /api/admin/cities/{id}/settings` - Update city settings

### Audit Log
- `GET /api/admin/audit-logs` - Get audit logs (paginated, filtered)
- `GET /api/admin/audit-logs/export` - Export audit logs

## Components

### Reusable Admin Components

#### DataTable
Sortable, selectable table with pagination:
```tsx
<DataTable
  columns={columns}
  data={items}
  keyExtractor={(item) => item.id}
  selectable
  selectedItems={selectedItems}
  onSelectionChange={setSelectedItems}
  onRowClick={handleRowClick}
/>
```

#### BulkActionBar
Sticky bottom bar for bulk operations:
```tsx
<BulkActionBar
  selectedCount={selectedItems.size}
  actions={[
    { label: 'Approve', onClick: handleBulkApprove, variant: 'success' },
    { label: 'Reject', onClick: handleBulkReject, variant: 'danger' },
  ]}
  onClear={() => setSelectedItems(new Set())}
/>
```

#### Modal
Customizable modal dialog:
```tsx
<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Confirm Action"
  footer={<>...</>}
>
  {children}
</Modal>
```

#### StatCard
Dashboard metric cards:
```tsx
<StatCard
  title="Total Users"
  value={1234}
  subtitle="50 active today"
  icon={UserIcon}
  color="blue"
  trend={{ value: 12, isPositive: true }}
/>
```

## Performance Optimizations

### Efficient Moderation at Scale

The admin panel is designed to handle 10,000+ voters:

1. **Pagination**: All data tables use server-side pagination (20-100 items per page)
2. **Bulk Operations**: Process up to 100 items at once
3. **Smart Caching**: React Query caches API responses (5 min stale time)
4. **Optimistic Updates**: UI updates immediately, syncs with server in background
5. **Virtual Scrolling**: Future enhancement for very large lists
6. **Database Indexes**: Backend uses indexes on frequently queried fields

### Backend Performance

- **Query Optimization**: Use SQLAlchemy query optimization and eager loading
- **Database Indexes**: Indexed on `status`, `created_at`, `user_id`, etc.
- **Rate Limiting**: Prevents API abuse
- **Async Operations**: Background tasks for heavy operations

## Security

### Authentication & Authorization

1. **JWT Tokens**: Secure token-based authentication
2. **Role Verification**: Every endpoint checks user role
3. **Permission Guards**: Frontend routes protected by RBAC
4. **Audit Logging**: All admin actions logged with actor, target, timestamp

### Security Best Practices

- HTTPS enforced in production
- CORS configured for allowed origins
- Rate limiting on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via React's built-in escaping
- CSRF tokens for state-changing operations

## Usage

### Accessing the Admin Panel

1. **Login** as an admin, moderator, or city staff user
2. **Navigate** to `/admin` (or click "Admin Panel" in user menu)
3. **Dashboard** loads showing platform overview
4. **Navigate** using sidebar to access different admin features

### Common Workflows

#### Moderating Questions

1. Go to **Question Moderation** (`/admin/questions`)
2. Review pending questions in the table
3. **Individual**: Click approve/reject icons for single questions
4. **Bulk**: Select multiple questions, use bulk action bar
5. **Duplicates**: Click merge icon to find and merge duplicates

#### Managing Users

1. Go to **User Management** (`/admin/users`)
2. Search or filter users by role, status
3. Click action icons to warn, suspend, or ban
4. View user activity details before taking action

#### Reviewing Reports

1. Go to **Content Moderation** (`/admin/content`)
2. Review flagged content reports
3. Resolve by removing content or dismissing report
4. All actions are logged in audit trail

#### Configuring Elections

1. Go to **City Configuration** (`/admin/config`)
2. Click "New Election" to create
3. Fill in election details (name, date, city)
4. Activate election when ready

## Development

### Adding a New Admin Feature

1. **Create Type** in `/frontend/src/types/index.ts`
2. **Create API Method** in `/frontend/src/services/adminApi.ts`
3. **Create Page Component** in `/frontend/src/pages/admin/`
4. **Add Route** in `/frontend/src/App.tsx`
5. **Add Backend Endpoint** in `/backend/app/api/admin_moderation.py`
6. **Test** locally with dev server

### Testing

```bash
# Frontend
cd frontend
npm test

# Backend
cd backend
pytest tests/
```

## Deployment

### Environment Variables

Frontend:
```bash
REACT_APP_API_URL=https://api.civicq.com/api/v1
```

Backend:
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALLOWED_ORIGINS=https://civicq.com,https://admin.civicq.com
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure HTTPS/SSL
- [ ] Set secure CORS origins
- [ ] Enable rate limiting
- [ ] Configure database backups
- [ ] Set up audit log retention policy
- [ ] Test all permissions and roles
- [ ] Review security headers

## Future Enhancements

### Planned Features

1. **Advanced Analytics**:
   - Real-time dashboards
   - Custom date ranges
   - Exportable reports
   - Data visualizations (charts/graphs)

2. **AI-Powered Moderation**:
   - Auto-detect inappropriate content
   - Suggest duplicate questions
   - Sentiment analysis
   - Spam detection

3. **Enhanced Audit Log**:
   - Full-text search
   - Advanced filtering
   - Diff views for changes
   - Rollback capabilities

4. **Workflow Automation**:
   - Auto-approve trusted users
   - Scheduled reports
   - Alert notifications (email/SMS)
   - Custom moderation rules

5. **Multi-City Management**:
   - Switch between cities
   - Cross-city analytics
   - City comparison tools

## Support

For issues or questions:
- **Documentation**: See `/docs` folder
- **GitHub Issues**: Submit bug reports
- **Email**: support@civicq.com

## License

MIT License - See LICENSE file

---

**Built with**: React, TypeScript, FastAPI, PostgreSQL, TailwindCSS
**Version**: 1.0.0
**Last Updated**: 2024
