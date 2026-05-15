# Database Schema for Kanban Studio

This document describes the MVP database schema, which is implemented in SQLite and stores the Kanban board as JSON.

## Goals

- Support a single Kanban board per user.
- Keep the schema simple and easy to extend.
- Store board data as JSON so the frontend can persist full state without a rigid column/card schema.
- Create the database automatically if it does not exist.

## Tables

### users

- `id` INTEGER PRIMARY KEY
- `username` TEXT NOT NULL UNIQUE
- `created_at` TEXT NOT NULL

This table stores users, with one row per unique username. For the MVP, authentication is hardcoded, but the schema supports multiple users in the future.

### boards

- `id` INTEGER PRIMARY KEY
- `user_id` INTEGER NOT NULL UNIQUE
- `board_data` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

Constraints:
- `user_id` references `users(id)`
- `user_id` is unique to enforce one board per user

## Board JSON structure

The Kanban board is stored in `board_data` as plain JSON text. The expected structure is:

```json
{
  "columns": [
    {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
    {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
    {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
    {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
    {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]}
  ],
  "cards": {
    "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
    "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
    "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
    "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
    "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
    "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
    "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
    "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."}
  }
}
```

### Notes on the JSON shape

- `columns` is an ordered array. Column order is preserved by the frontend.
- Each column has a fixed ID, a title, and an array of card IDs.
- The app supports renaming columns, so `title` is mutable.
- `cards` is a dictionary keyed by card ID.
- Each card includes `id`, `title`, and `details`.

## Future extension points

- Add `columnOrder` or support dynamic columns if required later.
- Add `lastEditedBy` or `version` fields for collaboration features.
- Replace `board_data` with a proper JSON column if migrating to a different database.

## Implementation note

A backend initializer will create the database and tables automatically on startup. The MVP stores board state in a single JSON field to keep the schema simple while supporting the required Kanban behavior.
