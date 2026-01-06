---
name: reminder-web-fetch-cache
description: Reminder about web page caching when using WebFetch. This skill should be used proactively whenever fetching or browsing web pages, especially when checking for recently updated content or verifying changes on a page.
---

# Web Fetch Cache Reminder

## Overview

When fetching web pages, responses may be cached. If checking for recent changes or updated content on a page, consider strategies to get fresh data.

## Caching Awareness

When fetching a web page and the content seems stale or doesn't reflect expected recent changes:

1. **Cache-busting query parameters** - Add a unique query parameter to bypass caching:
   - `?nocache=<timestamp>` or `?nc=<unique-value>`
   - Example: `https://example.com/page?nc=1736188200`

2. **Retry with variation** - If initial fetch returns unexpected results, try fetching again with a modified URL

3. **Consider timing** - Recently updated content may take time to propagate; caching is one possible cause of stale data, but not the only one

## When This Applies

This reminder is most relevant when:
- Verifying that changes have been made to a page
- Checking for recently posted content (reviews, comments, updates)
- Fetching the same URL multiple times in a session
- Content seems inconsistent with what the user reports seeing

This is a suggestion, not a requirement. Use judgment about whether caching is the likely cause of any discrepancy.
