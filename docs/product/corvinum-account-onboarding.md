# CorvinumEU account onboarding

Status: **Production blocker — role authority approved by the owner on
2026-08-07; workflow not implemented.**

This decision covers internal PeopleOps accounts only. It does not create
public registration, worker accounts, or a worker portal. Seeded demo accounts
and accounts created manually by SyncMetric are acceptable for fictional-data
testing, but they do not satisfy the production onboarding requirement.

## Invitation authority

| Inviter | Recruiter | Coordinator | Manager | Observer |
|---|---:|---:|---:|---:|
| Observer | ✅ | ✅ | ✅ | — |
| Manager | ✅ | ✅ | ✅ | — |
| Recruiter | — | — | — | — |
| Coordinator | — | — | — | — |

The target role is checked on the server for every invitation. An Observer and
a Manager may each invite a Recruiter, Coordinator, or Manager. No PeopleOps
role may invite an Observer. The first Observer is a deployment bootstrap
account created through a controlled SyncMetric operator procedure, never
through public registration or an ordinary invitation.

Observer remains read-only for worker, finance, compliance, and operational
records. Account invitation is a narrow administrative exception; it must not
grant Observer the broader existing `user.manage` capability. Implementation
therefore needs a dedicated invitation action with client-policy target-role
checks instead of widening `user.manage`.

## Minimum production behavior

Before Corvinum PeopleOps admits production users, the onboarding flow must:

1. Let an authorized inviter enter the invitee's email address and one of the
   three permitted target roles.
2. Deliver a single-use, time-limited account-setup link without creating or
   communicating a temporary password.
3. Validate expiry, revocation, single use, the inviter's current authority,
   and the requested role on the server.
4. Refuse self-registration and any invitation targeting Observer.
5. Handle an existing account or pending invitation without leaking account
   information to an unauthorized user.
6. Require the invitee to set their own password. An invited Manager must also
   complete the production TOTP requirement before ordinary application use,
   and the deployment-bootstrapped Observer must enroll TOTP before inviting
   anyone.
7. Audit invitation creation, resend, revocation, acceptance, expiry outcome,
   inviter, recipient identity, and assigned role. Passwords, setup tokens,
   TOTP secrets, and SMTP credentials must never enter audit data.
8. Provide the account-lifecycle controls needed after onboarding: at minimum
   secure password recovery, account deactivation, and controlled recovery from
   a lost Manager TOTP enrolment.

Email delivery must use Corvinum's secret-injected SMTP configuration. No
mailbox credential or setup token belongs in Git, logs, screenshots, or Help
captures.

## Decisions still required before implementation

The authority matrix above is settled. The implementation plan must still fix:

- invitation lifetime and resend/revocation behavior;
- the approved sender, subject, and SK/HU email wording;
- behavior for active, inactive, and already-invited email addresses;
- who may deactivate accounts, change existing roles, and recover lost TOTP;
- whether an accepted account becomes active immediately or needs a final
  approval step.

These choices affect authentication and authorization, so they must be decided
and covered by an ADR/security review before migrations or routes are added.

## Production acceptance

The gate is complete only after both client unit lanes, Corvinum authorization
and audit tests, invitation expiry/replay tests, and desktop/mobile browser
flows pass. A staging rehearsal must use fictional addresses on the configured
recipient allowlist. The production bootstrap procedure and first successful
Observer-to-Manager invitation must be recorded in `deployment_journal.md`.
