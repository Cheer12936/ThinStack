# Frontend

Select evidence for the changed behavior:
- Presentation only: inspect a representative render at relevant viewport/content conditions; keep the artifact and criterion-specific observation.
- Interaction: prove entry -> action -> result, including relevant loading/error/recovery state.
- Persisted business behavior: verify the real API/persistence path and refresh when persistence is part of acceptance.

Component, browser or screenshot checks are alternatives/complements chosen by risk, not a mandatory bundle. A screenshot cannot prove persisted behavior; a DOM assertion cannot prove layout quality. Test changed visibility conditions with the data versions actual producers emit.

Security-sensitive UI also loads auth guidance; hiding an action never proves server authorization.
