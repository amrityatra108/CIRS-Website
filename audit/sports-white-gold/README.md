# Sports: white and gold, September 30, 2026

Sports only. Based on current main, including the shared media playback fixes.

- Removed the duplicate eight-scene wipe. Retained one six-discipline desktop photo stack, now with white reading panels; narrow and short windows and reduced motion use the normal document layout. All eight unique photographs and captions from the removed wipe remain in the same gallery as regular figures. No original Sports photograph was lost.
- Added warm white surfaces, accessible antique gold lettering and a quiet abstract line pattern. House colours continue to identify the four houses.
- Removed the entire “Performance Is Built Before the Match” section.
- Added four 2026 result summaries to “What They Carried Home”, linked to the school's existing reports. The authority is the current `tools/sakshi.py` transcription of Chinmaya Sakshi, October 2026: `football-2026`, `swimming-2026`, `tennis-pickleball-and-table-tennis-2026`, and `marathon-athletics-and-basketball-2026`. No achievements, dates, student names or records were inferred. The older 2008/2025 records, Maths Run and explicitly tentative calendar entry remain.
- The opening video configuration, shared playback code, Aarav Bhartia's essay, council pledge, student names and practical links are unchanged. Creative Writing and other pages are untouched.

## Verification

Full HTML validation; all links and asset references; repeated build freshness; eight shared media lifecycle regression tests; unchanged anthology integrity check. Source comparisons confirmed every original Sports photograph and exact essay/pledge/practical copy preservation.

Chromium: 1440×900 desktop, 768×1024 tablet, 390×844 mobile, 320×740 narrow mobile, and 390×844 reduced motion. Forward and reverse section scrolling, keyboard house accordion and focus, one gallery/no duplicate wipe, all images loaded, no horizontal overflow or runtime errors. Scroll-video targets reached the starting frame, intermediate frames, final frame (5.012 of 5.042 seconds), and returned to the starting frame; latest-target reverse seeking remained correct.

A focused card-fit check covered 1440×900, 900×760 and 1440×650. The narrow desktop case exposed a tight basketball panel, so the stack now starts at 1100px width; narrower/shorter windows remain ordinary cards. Maximum desktop text-panel height was 603px within a 900px viewport.

White-surface text contrast: gold `#806019` 5.77:1, secondary ink `#55554a` 7.47:1, primary ink `#272720` 14.89:1 against `#fffefa`. Gold source links are underlined and focus outlines are explicit. Untouched photo/video overlays retain their existing styling.

Screenshots: [desktop archive](desktop-archive.png), [mobile archive](mobile-archive.png), [desktop gallery](desktop-gallery.png).

Device checks used browser viewport emulation; no physical phone was available. Executor requests to the public Vercel host returned network CONNECT 403; public deployment verification must be performed by the parent session, without bypassing that restriction.
