---
title: Cloudflare checkbox focus under concurrent browser load
author: RiX
date: 2026-11-08
branch: fix/turnstile-3.5.4
id: l-38b435be
scope: repo
status: active
src: agent
touches:
  - CHANGELOG.md
  - README.md
  - package.json
  - src/flaresolverr_service.py
---

## Decided
Limit active page solves to two by default through MAX_CONCURRENT_SOLVES. Acquire capacity before browser creation and before the per-request challenge deadline. Locate the actual Turnstile checkbox through its matching CDP frame and use the existing trusted pointer gesture on recognized challenge interstitials. Preserve custom widget pages and explicit tab counts on the legacy path.

## Tried and ruled out
Three concurrent requests passing did not exclude a concurrency bug. Four callers reproduced a production timeout. In a two-CPU Docker container, the original solver failed all 12 mixed-budget requests; the final code returned full pages for 20 of 20 requests at four callers and 24 of 24 at eight callers. Captured failures showed an unchecked checkbox with keyboard focus on the widget Privacy link. Bare mouse events and Selenium closed-shadow clicks were not reliable; the existing trusted pointer gesture activated the actual checkbox.

## Watch out
Use OrbStack Docker, not native Chrome, for reproduction. Validate returned content as well as status: a cleared challenge can briefly yield a short page during navigation. Queue time is outside maxTimeout; client wall time can therefore exceed that value. Test concurrent callers and slow CPU conditions, and preserve legacy handling for custom offscreen widgets.
