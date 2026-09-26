# Alumni page: source notes and details still needed from CIRS

The restored *Where CIRS Takes You* layout is built from `tools/pages/alumni.html`, `tools/alumni.py`, `assets/css/alumni.css`, and `assets/js/alumni-journey.js`. The original campus opening, destination map, quotations, alternating alumni chapters, pathway scenes, index, and closing scene remain. The scenes scroll in normal document flow.

## Material in use

- Four supplied photographs: Hari Om Jani, Soham Desai, Divyaj DT, and Shashwath Santosh. The Divyaj photo shows him on the right in the red kit. CIRS confirmed in the project conversation on 24 September 2026 that it has each alumnus's publication consent and the image rights, including any required credit arrangements. The underlying permission records remain with CIRS.
- Four short biographies with public source links in `tools/alumni.py`.
- Three alumni quotations and the school's 19 institution destination selection.
- The official alumni database form, school-office email, and telephone.

## Still needed from the school

- Preferred public spelling for **Hari Om Jani** (his Oxford profile uses **Hariom Jani**) and **Divyaj DT** (AIFF uses **Divyaj Dhaval Thakkar**).
- Graduating year or batch for **Hari Om Jani, Soham Desai, Divyaj DT, Shashwath Santosh, Kavya S, Roshan B, and Mugdha Sultania**. None is displayed without confirmation.
- Current alumni association or coordinator details, if an active association exists, plus its approved contact destination.
- Confirmation that the selected destination list is still current. It is presented as a selection, not a complete alumni register.
- Larger originals of three portraits. **Divyaj DT** (387×516), **Soham Desai** (497×618) and **Hari Om Jani** (732×732) are smaller than the frame the page draws them in on a tablet or a high-density screen. Until the originals arrive, each figure is capped at 1.25× its photograph's width (`PORTRAIT_STRETCH` in `tools/alumni.py`) rather than enlarged further; nothing is upscaled or sharpened. At least 1200px on the short side would serve every layout. The masters are in `assets/source/alumni/`; `tools/make-media.py` cuts the WebP copies the page uses.

If a visible photographer credit is required for any supplied photo, CIRS should provide its exact wording.
