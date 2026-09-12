# Important Documents — PDFs go here

This folder is the entire "backend" for the Important Documents portal. Every PDF the
portal and the School Information page can link to lives directly in this folder, as
a plain file in the repository — there is no database and no upload form.

**Do not rename files casually.** Each filename here must match the `"file"` value for
that document in `tools/documents.py` exactly, including case. If you want to rename a
file, change both places together.

See `ADMIN-DOCUMENTS.md` at the repository root for the full step-by-step: adding a new
document, replacing one, and removing one.

A document with no file here yet still appears in the portal and the document list —
marked "Awaiting upload" — rather than disappearing, so the published document list
never quietly drops something that is only pending.
