# News journal image sources

The ten WebP pairs in `assets/img/news/` are uncropped, resized versions of photographs published on CIRS sites. Each image belongs to one corresponding story on the News page.

| Story | Original CIRS image |
| --- | --- |
| Science Expo | https://new.cirschool.org/wp-content/uploads/2025/10/feature-science.jpg |
| English Week | https://new.cirschool.org/wp-content/uploads/2025/10/feature-eng.jpg |
| Mathematics Week 2025 | https://new.cirschool.org/wp-content/uploads/2025/10/feature-maths.jpg |
| Class Representative Elections | https://new.cirschool.org/wp-content/uploads/2025/10/feature-election.jpg |
| Seva Week | https://new.cirschool.org/wp-content/uploads/2025/10/feature-13.jpg |
| Vishu and Tamil Puthandu | https://cirschool.org/tamil%202025/images/pic02.JPG |
| Gayathri Havan | https://cirschool.org/gaythri%20havan%202025/images/pic03.JPG |
| Competitions | https://new.cirschool.org/wp-content/uploads/2025/10/feature-competition.jpg |
| Chinmaya Vraja | https://new.cirschool.org/wp-content/uploads/2025/10/feature-11.jpg |
| Social Science Week | https://new.cirschool.org/wp-content/uploads/2025/10/feature-12.jpg |

The three October 2025 WordPress stories and suggested descriptive alt text are:

| Story page | Suggested alt text |
| --- | --- |
| https://new.cirschool.org/competitions/ | Collage of CIRS students at award presentations and sporting events. |
| https://new.cirschool.org/chinmaya-vraja/ | CIRS community gathered for a puja in the Chinmaya Vraja hall. |
| https://new.cirschool.org/social-science-week/ | CIRS students and teachers holding certificates together. |

The 2026 IB and CBSE results have no verified event photograph; their News briefs are typography-led. The official “Solo Instrument” article has no event date and its body describes a dance competition, so it is presented without a photograph or invented event date. Its 10 October 2025 publication date is shown in the archive. The October 2025 WordPress publication dates are not used as event dates.

## Anand Utsav 2026

The cover of the article, which is also its picture in the News carousel, is the school's own "CIRS News Page Header" design from its Canva (`https://www.canva.com/design/DAHXg_OsUHE/`), three photographs side by side, supplied on 9 October 2026. Canva gives no stable address for the picture, so its PNG export is kept as `assets/source/anand-utsav/header.png` and `python3 tools/make-anand-utsav.py --cover` cuts the cover from it. (Until then the cover was the stage photograph `0C9A1479.JPG` from the school's Drive.) The seventeen after it in `assets/img/news/anand-utsav/` are the ones published with [Chinmaya Mission's report of the festival](https://www.chinmayamission.com/global/news/anand-utsav-at-cirs-family-values-creativity), in the order that page gives them (the first is its header image). Each is on `https://images.chinmayamission.com/uploads/<id>.webp`; `tools/anandutsav.py` lists the ids and `tools/make-anand-utsav.py` fetches and cuts them. The report prints no captions, so none are written.

## Date and content sources

The 2026 IB and CBSE figures and examination periods come from the [official CIRS News page](https://www.cirschool.org/news.html). That page gives no exact publication day for either result. The three added WordPress reports use the publication dates returned by the [official CIRS WordPress posts API](https://new.cirschool.org/wp-json/wp/v2/posts?per_page=100); their cards and archive rows explicitly say “Published.” Their event dates are either absent or more specific dates within the article, and are not inferred from upload paths. The existing English, Science, Mathematics, Elections and Seva reports use the event dates stated in their linked CIRS articles.
The rotating latest reports and archive are ordered by those official publication dates after the 2026 examination result briefs. The longer on-page reports retain the event dates given in their school sources.
