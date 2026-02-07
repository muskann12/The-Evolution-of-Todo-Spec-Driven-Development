# Decision Record: Authentication Strategy

**ID:** DR-002
**Date:** December 31, 2025
**Status:** ✅ Implemented
**Decider:** Development Team

---

## Context and Problem Statement

Phase II web application requires secure user authentication to:
- Protect user data (tasks belong to specific users)
- Prevent unauthorized access to API endpoints
- Maintain user sessions across page refreshes
- Support future multi-device access

**Requirements:**
1. Secure authentication mechanism
2. Stateless backend (scalability)
3. Support for SPA architecture
4. Token expiration and refresh
5. Simple implementation for MVP

---

## Decision Drivers

- **Security**: Industry-standard authentication
- **Scalability**: Stateless authentication (no server-side sessions)
- **Simplicity**: Easy to implement for MVP
- **User Experience**: Persistent sessions, automatic login
- **Future-proof**: Support mobile apps later

---

## Considered Options

### Option 1: JWT Tokens with localStorage (Chosen)

**Approach:**
- User logs in → Backend generates JWT token
- Frontend stores token in localStorage
- All API requests include token in Authorization header
- Backend verifies token on each request

**Pros:**
- ✅ Stateless authentication (backend doesn't store sessions)
- ✅ Easy to implement
- ✅ Works across tabs
- ✅ Standard industry practice for SPAs
- ✅ Can be used for mobile apps

**Cons:**
- ⚠️ localStorage vulnerable to XSS attacks
- ⚠️ Token cannot be invalidated before expiry
- ⚠️ Need careful XSS prevention

---

### Option 2: JWT Tokens with httpOnly Cookies

**Approach:**
- Backend sets httpOnly cookie with JWT
- Browser automatically sends cookie with requests
- JavaScript cannot access token

**Pros:**
- ✅ Protected from XSS attacks
- ✅ More secure than localStorage

**Cons:**
- ❌ More complex CORS setup
- ❌ Requires CSRF protection
- ❌ Harder to implement with separate frontend/backend
- ❌ Cookies sent to all same-origin requests (performance)

---

### Option 3: Session-based Authentication

**Approach:**
- Server stores session data
- Client receives session ID
- Server looks up session on each request

**Pros:**
- ✅ Server can invalidate sessions immediately
- ✅ Traditional, well-understood approach

**Cons:**
- ❌ Requires server-side session storage (Redis, etc.)
- ❌ Not stateless (scalability issues)
- ❌ Harder to support mobile apps
- ❌ More infrastructure complexity

---

## Decision Outcome

**Chosen option:** JWT Tokens with localStorage (Option 1)

### Rationale

1. **MVP Speed**
   - Simplest to implement
   - No additional infrastructure needed
   - Standard pattern for SPAs

2. **Stateless Backend**
   - No session storage required
   - Easy to scale horizontally
   - Each API instance independent

3. **Flexibility**
   - Works for web and future mobile apps
   - Easy to test with tools like Postman
   - Clear separation of concerns

4. **Acceptable Security for MVP**
   - With proper XSS prevention (React's built-in escaping)
   - HTTPS in production
   - Short token expiration (can refresh)

### Implementation

**Token Structure:**
```json
{
  "sub": "user-id-uuid",
  "exp": 1704153600,
  "iat": 1701561600
}
```

**Token Generation (Backend):**
```python
def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
```

**Token Storage (Frontend):**
```typescript
// Store after login
localStorage.setItem('auth_token', token);

// Include in requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
}
```

**Token Verification (Backend):**
```python
async def verify_jwt(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
```

---

## Security Measures

### XSS Prevention
1. React's built-in escaping for all user input
2. Content Security Policy headers (planned)
3. Input validation on all forms

### Token Security
1. HTTPS only in production
2. Short expiration time (30 days for MVP, 1 day in production)
3. Token refresh mechanism (future enhancement)
4. Logout clears token immediately

### API Security
1. All endpoints require valid token
2. User ID verification (token user === URL user)
3. Rate limiting (planned)
4. CORS properly configured

---

## Migration Path

**Future Improvements:**

1. **Phase 3: httpOnly Cookies**
   - More secure storage
   - Requires backend cookie handling
   - CSRF protection needed

2. **Phase 4: Refresh Tokens**
   - Short-lived access tokens (15 min)
   - Long-lived refresh tokens (30 days)
   - Token rotation on refresh

3. **Phase 5: OAuth Support**
   - Google, GitHub login
   - Better Auth integration
   - Social authentication

---

## Validation

**Testing (Jan 6, 2026):**
- ✅ Token persists across page refreshes
- ✅ Expired tokens rejected (401)
- ✅ Invalid tokens rejected (401)
- ✅ Token includes correct user ID
- ✅ Logout clears token
- ✅ Protected routes redirect if no token

**Security Audit:**
- ✅ XSS prevention verified
- ✅ CORS configured correctly
- ✅ No token leakage in console/logs
- ✅ Tokens not exposed in URL params

---

## Related Decisions

- **DR-001**: Technology Stack (FastAPI + Next.js)
- **DR-003**: Tags Storage (related to API design)
- D-006: localStorage for Token Storage
- D-005: User ID in URL Path

---

## References

- JWT.io Introduction: https://jwt.io/introduction
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- OWASP JWT Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

---

**Decision Type:** Security & Architecture
**Impact Level:** High (affects all authenticated features)
**Reversibility:** Medium (can migrate to cookies)
**Review Date:** Before production deployment

---

*This decision record follows SpecKit Plus v2.0 format*
