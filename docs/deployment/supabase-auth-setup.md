# Supabase Auth Setup

Status: manual configuration required.

1. Create a Supabase project.
2. Enable email/password authentication.
3. Disable public signup.
4. Create or select an asymmetric JWT signing key.
5. Collect the project URL and publishable key.
6. Create a server secret key for backend invitation calls.
7. Configure redirect URLs exactly:
   - `http://localhost:3000/auth/confirm`
   - `http://localhost:3000/update-password`
   - future production equivalents after approval.
8. Configure invite and password-recovery email templates to link to `/auth/confirm`.
9. Invite the initial administrator through the Supabase Dashboard.
10. Obtain that auth user UUID.
11. Run:

```powershell
uv run python -m contextos.cli bootstrap-admin --auth-user-id <uuid> --email <email>
```

12. Sign in through ContextOS.
13. Use ContextOS admin invitations to invite remaining beta users.

Never place the server secret key in frontend configuration. Do not claim production SMTP readiness until custom
SMTP is configured and verified.
