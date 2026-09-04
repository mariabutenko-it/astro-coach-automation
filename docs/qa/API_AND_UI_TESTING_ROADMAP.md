# AstroCoach QA roadmap

## UI automation — next stage

Precondition: provide a test build URL or connect a real device, plus a safe test account.

1. New-user onboarding: welcome screen and Skip keep the user in trial mode.
2. New-program preview: title, description, timeline, included content, CTAs, and chart reason for recommended programs.
3. One-day trial: Day 1 activities are available; later content is gated after the trial.
4. Purchase flow: available duration and intensity choices, successful activation.
5. Starting another program pauses the active program after a clear warning.
6. Ongoing program: missed activity state and pause/inactive state after 2–3 days without activity.

## API automation — staged coverage

### Completed / already covered

- Health and basic client behaviour
- Authentication contracts and invalid input
- Guest sessions and deviceId validation
- Zodiac Signs
- Membership plans
- User endpoints: unauthenticated and malformed-token boundaries
- Astro Programs: catalogue, themes, featured content, pagination and input validation

### Current known bugs

- AC-API-001 through AC-API-007 are documented in the separate bilingual bug report with Postman reproductions.

### Next API blocks

1. **Astro Programs — lifecycle and access**: enrolment, trial access, programme state, completion and restart. Depends on confirmed API endpoints and a test account.
2. **Wisdom**: daily content, filters, pagination, unsupported values and localisation.
3. **Location**: city lookup, mandatory query parameters, empty result, locale and validation.
4. **Payments and Karma Coins**: plans/catalogue access, authentication boundaries, idempotency and purchase callbacks. Use a test environment only.
5. **Authorised user scenarios**: preferences, devices, account state and token refresh using a safe test account.
6. **Cross-cutting checks**: response schema, error-contract consistency, localisation, pagination limits and authorization for every newly discovered endpoint.

## Working rule

For each block: study Postman/OpenAPI contract → add positive and negative API tests → run on dev → reproduce any discrepancy in Postman → add an RU/EN report entry and a direct Postman link.
