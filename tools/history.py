#!/usr/bin/env python3
"""The School History archive: every record, where it came from, and the page.

This file is the source record the brief asks for. Each event carries its own
source, and anything that could not be settled is written down in NOTES —
never resolved on the page by guesswork. The page shows the public half of
each record (date, title, description, the exhibit and its source line); the
"note" field and UNRESOLVED below are for whoever confirms the history next,
and are never published.

The page is built in three parts, all from EVENTS:

    CHAPTERS   six chapters for the scrolled sequence, each naming the
               events it tells; its "Read more" opens the lead record
    EVENTS     the complete archive, in date order, every event with a
               unique id — two things can happen in one year
    EXHIBITS   the images, cut by tools/make-history.py

Sources are named plainly. "The school's published history" is
https://cirschool.org/history.html, the account on the school's own current
website. Documents already published on this site are linked; documents held
only in the old site's pdf/ folder are named but not linked, because that
folder is never deployed.
"""

import html

IMG = "assets/img/history"
PUBLISHED = ('The school&rsquo;s published history, '
             '<a href="https://cirschool.org/history.html" target="_blank" rel="noopener">'
             'cirschool.org</a>')

# name -> (small w, h, large w, h). tools/make-history.py prints these; the
# build writes them into the page so every image reserves its box before it
# loads, without the build needing Pillow.
EXHIBITS = {
    "gurudev":          (640, 881, 1400, 1927),
    "noc-1996":         (640, 906, 1400, 1981),
    "kalam-2007":       (640, 921, 1170, 1683),
    "sakshi-2008":      (640, 871, 1332, 1812),
    "reflections-2010": (640, 833, 1334, 1736),
    "isa-2010":         (640, 943, 1087, 1601),
    "vision-2012":      (640, 427, 1400, 933),
    "brainfeed-2017":   (640, 798, 1400, 1746),
    "report-2019":      (640, 940, 1087, 1597),
}

PERIODS = [
    ("before", "Before opening"),
    ("early", "Early years"),
    ("later", "Later milestones"),
]

# Every field but "note" is published. "exhibit" names an image in EXHIBITS,
# or is None for a record the archive holds as type alone.
EVENTS = [
    # ---- Before opening ------------------------------------------------
    {"id": "idea-1970s", "when": "1970s", "period": "before",
     "title": "An international school is imagined",
     "summary": "Pujya Gurudev Swami Chinmayananda conceives an international school in India.",
     "body": "The idea of starting an international school in India was conceived by Pujya "
             "Gurudev Swami Chinmayananda, and it met with an overwhelming response from all "
             "over the world. Bangalore, Lucknow, the Andamans and Himachal Pradesh were each "
             "evaluated before Coimbatore was chosen.",
     "exhibit": "gurudev",
     "alt": "A close colour portrait of Pujya Gurudev Swami Chinmayananda, smiling, in saffron "
            "robes and spectacles",
     "caption": "Pujya Gurudev Swami Chinmayananda. A portrait from the school&rsquo;s archive; "
                "the date of the photograph is not recorded.",
     "source": PUBLISHED},
    {"id": "rupee-1984", "when": "1984", "period": "before",
     "title": "One rupee at a time",
     "summary": "The first collection towards the land: one rupee from each person, gathered on foot.",
     "body": "Swami Sahayanandaji travelled the length and breadth of India on foot, making the "
             "initial collection towards the purchase of the land: one rupee from each "
             "individual.",
     "exhibit": None,
     "source": PUBLISHED,
     "note": "The earlier draft of this page named Pujya Gurudev and Br. Sahaja Chaitanyaji and "
             "said 'one rupee from every household'; it also said the land took 'another ten "
             "years' to procure. The school's published history names Swami Sahayanandaji and "
             "says 'from each individual', and gives no duration. The page follows the "
             "published history. Whether Br. Sahaja Chaitanya and Swami Sahayananda are the "
             "same person at different stages is NOT established — ask the school."},
    {"id": "mahasamadhi-1993", "when": "3 August 1993", "period": "before",
     "title": "Gurudev attains Mahasamadhi",
     "summary": "Pujya Gurudev attains Mahasamadhi, three years before the school opens.",
     "body": "Pujya Gurudev Swami Chinmayananda attained Mahasamadhi on 3 August 1993. He did "
             "not see the school he had conceived open its doors.",
     "exhibit": None,
     "source": 'The chronology of Gurudev&rsquo;s life on this site&rsquo;s '
               '<a href="founder.html#life">Founder</a> page',
     "note": "The school's published history does not mention 1993; it moves from 1984 to 1994. "
             "The earlier draft said that after the Mahasamadhi Pujya Guruji 'took the project "
             "upon his own shoulders' — that wording has no source in hand and is not used."},
    {"id": "guruji-1994", "when": "1994", "period": "before",
     "title": "The vision is made concrete",
     "summary": "Pujya Guruji Swami Tejomayananda carries the project forward.",
     "body": "Pujya Guruji Swami Tejomayananda proceeded to concretise the vision of Pujya "
             "Gurudev with unfailing vigour and energy, and the work progressed by leaps and "
             "bounds.",
     "exhibit": None,
     "source": PUBLISHED},
    {"id": "project-1996", "when": "Until 1996", "period": "before",
     "title": "Guided to completion",
     "summary": "Devotees give generously; the project is guided and executed to completion.",
     "body": "Many devotees around the world contributed generously. Swamini Vimalanandaji and "
             "Dr. G.&nbsp;S. Keshawamurthy played a significant role in guiding and executing "
             "the project to its completion.",
     "exhibit": None,
     "source": PUBLISHED,
     "note": "The published history gives no dates for this. The earlier draft said Swamini "
             "Vimalanandaji 'becomes Director of CIRS' in 1996; that is not in the published "
             "history and is not used."},

    # ---- Early years ---------------------------------------------------
    {"id": "inauguration-1996", "when": "6 June 1996", "period": "early",
     "title": "The school is inaugurated",
     "summary": "Inaugurated by Pujya Swami Chidanandaji, President of The Divine Life Society.",
     "body": "The Chinmaya International Residential School was inaugurated by Pujya Swami "
             "Chidanandaji, President of The Divine Life Society. The plaque at the main "
             "building records that he did so in the presence of Swami Tejomayananda, Head of "
             "Chinmaya Mission, on Thursday, 6 June 1996.",
     "exhibit": None,
     "source": PUBLISHED + '; the inauguration plaque at the main building',
     "note": "The plaque is legible only in part in a 2018 school photograph on Drive "
             "('bal sevak award.JPG'). A straight photograph of it would make a strong exhibit "
             "for this record; none is in hand. No photograph of the inauguration itself has "
             "been found."},
    {"id": "first-school-1996", "when": "June 1996", "period": "early",
     "title": "Ninety-six students, eleven teachers",
     "summary": "96 students in Grades V to VIII, and 11 academic staff.",
     "body": "CIRS started with 96 students from Grade V to Grade VIII and 11 academic staff, "
             "headed by Dr. Jaya Venugopal, with Brahmacharini Sumati Chaitanya and "
             "Brahmachari Samahita Chaitanya as spiritual guides.",
     "exhibit": None,
     "source": PUBLISHED,
     "note": "DISCREPANCY: the school's 2023 brochure (Drive, 'CIRS.pdf') says the school began "
             "'with just 94 students and eight teachers'. The page follows the published "
             "history (96 and 11). The school should say which is right."},
    {"id": "noc-1996", "when": "15 July 1996", "period": "early",
     "title": "The State&rsquo;s no-objection",
     "summary": "Tamil Nadu raises no objection to CBSE affiliation, on one condition.",
     "body": "The Director of School Education, Government of Tamil Nadu, wrote to the Central "
             "Board of Secondary Education that the department had no objection to the "
             "syllabus of the middle classes at CIRS being affiliated to the Board, subject to "
             "one condition: Tamil should be taught as a second language.",
     "exhibit": "noc-1996",
     "alt": "A typed letter from the Government of Tamil Nadu Education Department to the "
            "Secretary of the Central Board of Secondary Education, dated 15-7-96",
     "caption": "L.Dis.No.22864/E3/96, dated 15 July 1996. The letter as the school holds it.",
     "source": 'No Objection Certificate, published on '
               '<a href="school-info.html">School Information</a> &middot; '
               '<a href="assets/documents/school-info/state-noc.pdf" target="_blank" '
               'rel="noopener">Open the PDF</a>'},
    {"id": "director-2005", "when": "2005", "period": "early",
     "title": "A Resident Director",
     "summary": "Swami Swaroopanandaji becomes Resident Director of CIRS.",
     "body": "Pujya Guruji appointed Swami Swaroopanandaji as Resident Director of CIRS.",
     "exhibit": None,
     "source": "The school&rsquo;s own account, supplied for this website",
     "note": "From the content the school supplied for the redesign. No appointment letter or "
             "dated publication has been seen. Confirm the year."},
    {"id": "kalam-2007", "when": "7 May 2007", "period": "early",
     "title": "At Rashtrapati Bhavan",
     "summary": "Thirty-two students meet President A.&nbsp;P.&nbsp;J. Abdul Kalam in New Delhi.",
     "body": "Thirty-two students from Classes VI to XII, with one alumnus, four teachers and "
             "Principal Anurag Sangal, met President A.&nbsp;P.&nbsp;J. Abdul Kalam in the "
             "Committee Room of Rashtrapati Bhavan. The invitation grew out of a vacation "
             "assignment set in November 2006 on the President&rsquo;s &lsquo;Vision for India "
             "2020&rsquo;, which the school had recast for its students as &lsquo;My Vision "
             "for Myself, my Family, my School and my Country &ndash; in 2020&rsquo;. Selected "
             "projects were sent to the President, and led to his interest in meeting them.",
     "exhibit": "kalam-2007",
     "alt": "The first typed page of the school's account, headed 'Interaction of CIRS students "
            "with His Excellency, Dr APJ Abdul Kalam, President of India'",
     "caption": "The first page of the school&rsquo;s account of the meeting, with its "
                "transcript.",
     "source": "The school&rsquo;s account of the interaction, kept from its former website"},
    {"id": "sakshi-2008", "when": "May 2008", "period": "early",
     "title": "A newsletter the students made",
     "summary": "Chinmaya Sakshi, written, edited and laid out by students.",
     "body": "<i>Chinmaya Sakshi</i>, the school&rsquo;s e-newsletter, was put together by the "
             "students&rsquo; editorial team: they gathered the news, edited it and designed "
             "the layout, &lsquo;with a minimal assistance and guidance from the "
             "teachers&rsquo;, as the Principal&rsquo;s note in the October&ndash;November "
             "2007 edition puts it. The summer special of May 2008 opens on the campus beneath "
             "the hills and a portrait of Gurudev.",
     "exhibit": "sakshi-2008",
     "alt": "The cover of the Chinmaya Sakshi e-newsletter, May 2008 summer special, with a "
            "photograph of the campus and a portrait of Gurudev",
     "caption": "<i>Chinmaya Sakshi</i>, E-Newsletter, summer special, May 2008.",
     "source": "<i>Chinmaya Sakshi</i>, October&ndash;November 2007 and May 2008 editions, "
               "kept from the school&rsquo;s former website"},
    {"id": "principal-2009", "when": "2009", "period": "early",
     "title": "A new Principal",
     "summary": "Smt. Shanti Krishnamurthy becomes Principal of CIRS.",
     "body": "Smt. Shanti Krishnamurthy became Principal of CIRS.",
     "exhibit": None,
     "source": 'The school&rsquo;s introduction on <a href="leadership.html">Leadership</a>'},
    {"id": "reflections-2010", "when": "August 2010", "period": "early",
     "title": "Reflections, the IB newsletter",
     "summary": "The IB students&rsquo; own newsletter reports their tour of Sri Lanka.",
     "body": "<i>Reflections</i>, the newsletter of the school&rsquo;s IB Diploma students, "
             "reached its fourth issue with a special on the first-year students&rsquo; tour "
             "of Sri Lanka in August 2010 &mdash; &lsquo;a blend of the experience of a new "
             "culture and service to humanity&rsquo;, in the words of the IB Diploma "
             "Coordinator.",
     "exhibit": "reflections-2010",
     "alt": "The cover of Reflections, an IB newsletter of the Chinmaya International "
            "Residential School, August 2010, with students arriving with their luggage",
     "caption": "<i>Reflections</i>, Volume 1, Issue 4, August 2010.",
     "source": "<i>Reflections</i>, Volume 1, Issue 4, kept from the school&rsquo;s former "
               "website",
     "note": "The year the IB Diploma Programme was introduced at CIRS is not established. The "
             "Oct–Nov 2007 Chinmaya Sakshi already lists an 'IB Farewell', so it predates "
             "2007. This is a major milestone the archive should carry once the school "
             "confirms the year."},
    {"id": "isa-2010", "when": "December 2010", "period": "early",
     "title": "The world in the curriculum",
     "summary": "A holiday assignment set for the British Council&rsquo;s International School Award.",
     "body": "The Junior School&rsquo;s December 2010 holiday assignment was set as part of the "
             "British Council&rsquo;s International School Award programme, which CIRS had "
             "taken up to bring an international dimension into its curriculum. Class V "
             "studied tourist attractions across the world, Class VI music across the globe, "
             "Class VII national games, and Class VIII agricultural practices.",
     "exhibit": "isa-2010",
     "alt": "The first page of the CIRS Junior School Holiday Assignment, December 2010, "
            "explaining the International School Awards",
     "caption": "Junior School Holiday Assignment, December 2010, first page.",
     "source": "The assignment sheet, kept from the school&rsquo;s former website"},

    # ---- Later milestones ----------------------------------------------
    {"id": "isa-award-2011", "when": "2011", "period": "later",
     "title": "The International School Award",
     "summary": "The British Council recognises the international dimension of the curriculum.",
     "body": "CIRS received the British Council&rsquo;s International School Award, which "
             "recognises good practice in bringing an international dimension into the "
             "curriculum.",
     "exhibit": None,
     "source": "The school&rsquo;s own account, supplied for this website; its former website "
               "carried a gallery titled &lsquo;CIRS Receives ISA Award&rsquo;",
     "note": "The year 2011 is from the school-supplied content. The former website's gallery "
             "page (copyright 2011, file dated April 2012) confirms the award, not the year. "
             "The certificate would settle it."},
    {"id": "vision-award-2012", "when": "2012", "period": "later",
     "title": "The CCMT Education Cell Vision Award",
     "summary": "The Central Chinmaya Mission Trust&rsquo;s Education Cell names CIRS for 2012.",
     "body": "The Education Cell of the Central Chinmaya Mission Trust presented its Vision "
             "Award for 2012 to CIRS, Coimbatore.",
     "exhibit": "vision-2012",
     "alt": "A trophy inscribed 'Central Chinmaya Mission Trust Education Cell Vision Award "
            "2012, awarded to CIRS, Coimbatore', held up with its certificate by a woman in a "
            "sari and a swami in saffron",
     "caption": "The trophy and its certificate at the presentation. From the school&rsquo;s "
                "photograph archive; the people pictured are not named in the record.",
     "source": "The inscription on the award",
     "note": "DATE CORRECTED: the earlier draft said 'Chinmaya Vision Award', 2013. The trophy "
             "reads 'Vision Award – 2012' and the photograph's file is dated 25 July 2012. The "
             "people in the photograph (apparently Pujya Guruji and a member of staff) should "
             "be named by the school before a caption names them."},
    {"id": "poland-2014", "when": "2014", "period": "later",
     "title": "A partnership with a school in Poland",
     "summary": "A shared project on language, culture and advertising.",
     "body": "From February 2014 a CIRS class worked with an upper-secondary and technical "
             "college in Poland on a shared project, &lsquo;Trends in advertising: the impact "
             "of language and culture on advertising&rsquo;, exchanging videos, worksheets "
             "and advertisements of their own.",
     "exhibit": None,
     "source": "The school&rsquo;s newsletter page on the partnership, May 2014, kept from its "
               "former website"},
    {"id": "brainfeed-2017", "when": "12 November 2017", "period": "later",
     "title": "Brainfeed Top 500 Schools of India",
     "summary": "Named in Brainfeed&rsquo;s School Excellence Awards, 2017&ndash;18.",
     "body": "Brainfeed&rsquo;s School Excellence Awards named CIRS among the Top 500 Schools "
             "of India 2017&ndash;18, in the category Best International Boarding / Happiness "
             "Quotient Index / Influential School Brand School, and among the best "
             "international schools of Tamil Nadu. The award was presented in Bengaluru.",
     "exhibit": "brainfeed-2017",
     "alt": "A wooden plaque with a gold panel reading 'brainfeed school excellence awards, "
            "Top 500 Schools of India 2017-18, is awarded to Chinmaya International "
            "Residential School, Coimbatore'",
     "caption": "The plaque, dated 12 November 2017, Bengaluru.",
     "source": "The plaque itself, photographed for the school"},
    {"id": "director-2018", "when": "2018", "period": "later",
     "title": "Director &mdash; Academics and Administration",
     "summary": "Smt. Shanti Krishnamurthy takes on the direction of the school.",
     "body": "Smt. Shanti Krishnamurthy became Director &mdash; Academics and Administration.",
     "exhibit": None,
     "source": 'The school&rsquo;s introduction on <a href="leadership.html">Leadership</a>'},
    {"id": "report-2019", "when": "15 October 2019", "period": "later",
     "title": "The school in its twenty-fourth year",
     "summary": "580 students from 22 states and 18 countries; a CBSE Lead School.",
     "body": "In its 24th year the school reported 580 students &mdash; 345 boys and 235 girls "
             "&mdash; from 22 Indian states and 18 other countries, with 67 faculty members "
             "and 68 members of the administrative team. That year the CBSE selected CIRS as "
             "one of its Lead Schools, to guide five other CBSE schools, and Sanskrit became a "
             "compulsory subject, beginning in Class V.",
     "exhibit": "report-2019",
     "alt": "The first page of the CIRS Annual Report dated 15th Oct 2019",
     "caption": "Annual Report, 15 October 2019, first page.",
     "source": 'Annual Report, 15 October 2019, published on '
               '<a href="school-info.html">School Information</a> &middot; '
               '<a href="assets/documents/school-info/annual-report.pdf" target="_blank" '
               'rel="noopener">Open the PDF</a>',
     "note": "These are the latest figures with a confirmed reporting year. The published "
             "history's '577 students, 69 faculty and 78 staff, from 23 States of India and 19 "
             "other countries' carries no year (that page is copyright 2011, file dated 2013), "
             "and the 2023 brochure says 575 students, 120 staff, 27 other countries. None of "
             "them is presented as current."},
    {"id": "ranking-2019", "when": "2019", "period": "later",
     "title": "Education World survey",
     "summary": "Second among India&rsquo;s co-educational boarding schools; first in Tamil Nadu.",
     "body": "In Education World&rsquo;s 2019 survey, conducted by the Delhi-based C fore, CIRS "
             "moved from fourth to second place in the country among co-educational boarding "
             "schools, and kept first place in Tamil Nadu for the eighth consecutive year.",
     "exhibit": None,
     "source": 'The school&rsquo;s Annual Report, 15 October 2019 &middot; '
               '<a href="assets/documents/school-info/annual-report.pdf" target="_blank" '
               'rel="noopener">Open the PDF</a>',
     "note": "REPLACES two unsourced entries in the earlier draft: '2016, Education World ranks "
             "CIRS among the top four' and '2018, second in the country, first in CBSE'. The "
             "annual report implies fourth place in the preceding survey but does not give "
             "its year, and nothing supports 'first in CBSE'. Neither is published."},
    {"id": "cbse-2019", "when": "2019", "period": "later",
     "title": "Class XII results, 2019",
     "summary": "Every one of 45 candidates above 80%; 41 above 90%.",
     "body": "All 45 students who sat the Class XII examination secured above 80% in the "
             "aggregate, and 41 of them above 90%. The Science stream averaged 92.06% and the "
             "Management stream 94.23%.",
     "exhibit": None,
     "source": 'The school&rsquo;s Annual Report, 15 October 2019 &middot; '
               '<a href="our-results.html">Our Results</a>',
     "note": "The earlier draft's '2022: a 92% average in Science, 19 of 24 students at 90% or "
             "above' has no source in hand, and 92% is the 2019 Science average. It is not "
             "published; confirm whether 2022 is a separate result."},
    {"id": "cbse-2026", "when": "March&ndash;April 2026", "period": "later",
     "title": "CBSE Class XII, 2026",
     "summary": "The highest Management score is 99.0%.",
     "body": "In the 2026 CBSE Class XII examinations the highest score in the Management "
             "stream was 99.0%, and the stream averaged 94%.",
     "exhibit": None,
     "source": 'The school&rsquo;s results brief on <a href="news.html#cbse-results-2026">'
               'News</a>'},
    {"id": "ib-2026", "when": "May 2026", "period": "later",
     "title": "Twenty-four candidates, twenty-four diplomas",
     "summary": "Every IB candidate earns the diploma; two score 45 out of 45.",
     "body": "All 24 candidates in the May 2026 IB Diploma examination earned the diploma, with "
             "an average of 39.4 points. Two students scored the maximum, 45 out of 45.",
     "exhibit": None,
     "source": 'The school&rsquo;s results brief on <a href="news.html#ib-results-2026">'
               'News</a>'},
]

# The six chapters of the scrolled sequence. "events" are the records the
# chapter tells, in order; the first is the one "Read more" opens. "exhibit"
# is an image from EXHIBITS or one of the three designed compositions:
# "rupee", "diptych" and "opening".
CHAPTERS = [
    {"id": "chapter-idea", "short": "The idea", "when": "1970s",
     "headline": "The idea came first.",
     "text": "Pujya Gurudev Swami Chinmayananda conceived an international school in India, "
             "and the idea met with an overwhelming response from around the world. Bangalore, "
             "Lucknow, the Andamans and Himachal Pradesh were weighed before Coimbatore was "
             "chosen.",
     "exhibit": "gurudev", "events": ["idea-1970s"]},
    {"id": "chapter-rupee", "short": "The land", "when": "From 1984",
     "headline": "One rupee at a time.",
     "text": "To buy the land, Swami Sahayanandaji travelled the length and breadth of India on "
             "foot, making the first collection: one rupee from each person.",
     "aside": "The marks stand for many people taking part. They are not a count of those "
              "who gave.",
     "exhibit": "rupee", "events": ["rupee-1984"]},
    {"id": "chapter-shape", "short": "Taking shape", "when": "1993 &ndash; 1994",
     "headline": "The project takes shape.",
     "text": "Gurudev attained Mahasamadhi on 3 August 1993 and did not see the school open. "
             "In 1994, as the school&rsquo;s own account records, Pujya Guruji Swami "
             "Tejomayananda set about making the vision concrete, and the work progressed by "
             "leaps and bounds.",
     "exhibit": "diptych", "events": ["guruji-1994", "mahasamadhi-1993", "project-1996"]},
    {"id": "chapter-opening", "short": "The opening", "when": "6 June 1996",
     "headline": "The school opens.",
     "text": "Inaugurated by Pujya Swami Chidanandaji, President of The Divine Life Society. "
             "The first staff were headed by Dr. Jaya Venugopal, with Brahmacharini Sumati "
             "Chaitanya and Brahmachari Samahita Chaitanya as spiritual guides.",
     "exhibit": "opening", "events": ["inauguration-1996", "first-school-1996"]},
    {"id": "chapter-early", "short": "Early years", "when": "1996 &ndash; 2010",
     "headline": "A school finds its voice.",
     "text": "Within weeks of opening the State cleared the way to CBSE affiliation. In 2007 "
             "thirty-two students met President Kalam at Rashtrapati Bhavan, and by 2010 the "
             "students were writing and laying out newsletters of their own.",
     "exhibit": "sakshi-2008",
     "events": ["sakshi-2008", "noc-1996", "kalam-2007", "reflections-2010", "isa-2010",
                "director-2005", "principal-2009"]},
    {"id": "chapter-later", "short": "Later years", "when": "2011 &ndash; 2026",
     "headline": "A wider world, and a longer record.",
     "text": "The International School Award, the CCMT Education Cell&rsquo;s Vision Award for "
             "2012, and by 2019 a school of 580 students from 22 states and 18 other "
             "countries. Examination results and honours are kept in full on their own pages.",
     "exhibit": "vision-2012",
     "links": [("Our Results", "our-results.html"), ("Our Laurels", "our-laurels.html")],
     "events": ["vision-award-2012", "isa-award-2011", "poland-2014", "brainfeed-2017",
                "director-2018", "report-2019", "ranking-2019", "cbse-2019", "cbse-2026",
                "ib-2026"]},
]

# Held back from the page until the school supplies a source. Listed here so
# the next person knows what was taken out and why; see also each "note".
UNRESOLVED = [
    ("1979, the land is found", "The draft said the Coimbatore Chinmaya Mission Committee, "
     "guided by A. Somasundaram, identified the land, and that Gurudev called it 'the Sidhbari "
     "of the South'. The published history does not have it and no document was found."),
    ("2013, Chinmaya Vision Award", "Superseded: the award itself reads 2012 (vision-award-2012)."),
    ("2016, Education World top four", "No year-specific source."),
    ("2018, second in the country, first in CBSE", "No source; conflicts with the 2019 report."),
    ("2019, IB World Topper, 45/45", "No source in hand."),
    ("2019, the first CIRSMUN", "No dated source in hand (Drive has a 2025 CIRSMUN graphic)."),
    ("2022, 92% average in Science", "No source; the figure matches 2019's."),
    ("2024, IB World Toppers once more", "No source in hand."),
    ("2025, Vayu Nigrah first prize, SSVM Transforming India Conclave", "Drive holds the "
     "project's flyers dated October 2024, which suggests the year may be 2024. The prize "
     "itself is unconfirmed."),
]

BY_ID = {e["id"]: e for e in EVENTS}
assert len(BY_ID) == len(EVENTS), "every event needs a unique id"
for _c in CHAPTERS:
    for _id in _c["events"]:
        assert _id in BY_ID, f"{_c['id']} names an unknown event {_id}"


def attr(text):
    """Text for an attribute: entities are kept, quotes are escaped."""
    return text.replace('"', "&quot;")


def plain(text):
    """An entity-laden string as the words it says, for an aria-label."""
    import re
    return attr(html.unescape(re.sub(r"<[^>]+>", "", text)))


def img_html(name, alt, sizes, cls="", eager=False):
    sw, sh, lw, lh = EXHIBITS[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    klass = f' class="{cls}"' if cls else ""
    return (f'<img{klass} src="{IMG}/{name}-sm.jpg" '
            f'srcset="{IMG}/{name}-sm.jpg {sw}w, {IMG}/{name}-lg.jpg {lw}w" '
            f'sizes="{sizes}" width="{sw}" height="{sh}" alt="{attr(alt)}" '
            f'{load} decoding="async">')


def ratio(name):
    sw, sh, _, _ = EXHIBITS[name]
    return f"{sw / sh:.4f}"


# ---- the designed compositions ---------------------------------------------

def rupee_html():
    """Small marks that gather into one field.

    Each mark starts scattered and settles into a block of rows. The
    positions are fixed here rather than random, so the page is the same on
    every load and the stylesheet can place them before any script runs."""
    cols, rows = 9, 6
    marks = []
    n = 0
    for r in range(rows):
        for c in range(cols):
            # The settled field: a block of rows, centred.
            x1 = 14 + c * (72 / (cols - 1))
            y1 = 22 + r * (50 / (rows - 1))
            # A scatter that is deterministic but not a grid: two
            # incommensurate steps walk each mark to its own start.
            x0 = (n * 37.3 + 11) % 92 + 4
            y0 = (n * 23.7 + 7) % 84 + 8
            marks.append(f'<i style="--x0:{x0:.1f};--y0:{y0:.1f};--x1:{x1:.1f};--y1:{y1:.1f};'
                         f'--d:{(n % 9) * 0.02 + (n // 9) * 0.035:.3f}"></i>')
            n += 1
    return (f'<div class="hx-ex hx-ex--type hx-ex--rupee" style="--ar:.8" data-exhibit="rupee">'
            f'<div class="hx-rupee__field" aria-hidden="true">{"".join(marks)}</div>'
            f'<p class="hx-type__when">1984</p>'
            f'<p class="hx-type__title">One rupee,<br>from each person.</p>'
            f'</div>')


def diptych_html():
    return ('<div class="hx-ex hx-ex--type hx-ex--diptych" style="--ar:1.18" data-exhibit="diptych">'
            '<div class="hx-dip hx-dip--a">'
            '<p class="hx-type__when">3 August 1993</p>'
            '<p class="hx-type__title">Gurudev attains Mahasamadhi.</p>'
            '<p class="hx-type__src">Founder chronology</p></div>'
            '<div class="hx-dip hx-dip--b">'
            '<p class="hx-type__when">1994</p>'
            '<p class="hx-type__title">Pujya Guruji makes the vision concrete.</p>'
            '<p class="hx-type__src">The school&rsquo;s published history</p></div>'
            '</div>')


def opening_html():
    """96 squares for the students and 11 marks for the academic staff.

    Grouped so they arrive in a few beats rather than counting up one at a
    time; the numbers themselves are in the text beside it, for everyone."""
    students = "".join(f'<i style="--g:{i // 24}"></i>' for i in range(96))
    staff = "".join(f'<i style="--g:{4 + i // 6}"></i>' for i in range(11))
    return ('<div class="hx-ex hx-ex--type hx-ex--opening" style="--ar:1.02" data-exhibit="opening">'
            '<p class="hx-type__when">6 June 1996</p>'
            '<div class="hx-open__groups" aria-hidden="true">'
            f'<div class="hx-open__set hx-open__set--students"><div class="hx-open__marks">{students}</div>'
            '<p class="hx-open__label"><b>96</b> students</p></div>'
            f'<div class="hx-open__set hx-open__set--staff"><div class="hx-open__marks">{staff}</div>'
            '<p class="hx-open__label"><b>11</b> academic staff</p></div>'
            '</div>'
            '<p class="hx-type__title hx-open__grades">Grades V&ndash;VIII</p>'
            '</div>')


def exhibit_html(chapter, eager=False):
    ex = chapter["exhibit"]
    if ex == "rupee":
        return rupee_html()
    if ex == "diptych":
        return diptych_html()
    if ex == "opening":
        return opening_html()
    lead = next(BY_ID[i] for i in chapter["events"] if BY_ID[i].get("exhibit") == ex)
    return (f'<figure class="hx-ex hx-ex--img" style="--ar:{ratio(ex)}" data-exhibit="{ex}">'
            + img_html(ex, lead["alt"], "(max-width: 900px) 86vw, 34vw", eager=eager)
            + '</figure>')


# ---- the page's parts --------------------------------------------------------

def chapter_nav_html():
    items = "".join(
        f'<li><a href="#{c["id"]}" data-hx-jump="{i}"><span class="hx-nav__n">{i + 1:02d}</span>'
        f'<span class="hx-nav__t">{c["short"]}</span></a></li>'
        for i, c in enumerate(CHAPTERS))
    return (f'<nav class="hx-nav" aria-label="Chapters of the history">'
            f'<ol class="hx-nav__list">{items}</ol>'
            f'<a class="hx-nav__all" href="#timeline">View all milestones</a></nav>')


def chapters_html():
    out = []
    for i, c in enumerate(CHAPTERS):
        lead = BY_ID[c["events"][0]]
        aside = f'<p class="hx-ch__aside">{c["aside"]}</p>' if c.get("aside") else ""
        extra = ""
        if c["exhibit"] == "opening":
            # The composition's figures, as text, for every reader.
            extra = ('<dl class="hx-ch__facts"><div><dt>Students</dt><dd>96</dd></div>'
                     '<div><dt>Academic staff</dt><dd>11</dd></div>'
                     '<div><dt>Grades</dt><dd>V&ndash;VIII</dd></div></dl>')
        links = "".join(f'<a class="hx-ch__link" href="{href}">{label}</a>'
                        for label, href in c.get("links", []))
        more = (f'<a class="hx-ch__more" href="#record-{lead["id"]}" data-hx-record="{lead["id"]}">'
                f'Read more<span class="sr-only"> about {plain(lead["title"])}</span></a>')
        out.append(
            f'<li class="hx-ch" id="{c["id"]}" data-hx-chapter="{i}">'
            f'<div class="hx-ch__visual">{exhibit_html(c, eager=(i == 0))}</div>'
            f'<div class="hx-ch__text">'
            f'<p class="hx-ch__when"><span class="hx-ch__n">{i + 1:02d}</span>{c["when"]}</p>'
            f'<h3 class="hx-ch__head">{c["headline"]}</h3>'
            f'<p class="hx-ch__copy">{c["text"]}</p>{extra}{aside}'
            f'<p class="hx-ch__actions">{more}{links}</p>'
            f'</div></li>')
    return "\n".join(out)


def filters_html():
    buttons = ['<button type="button" class="hx-filter" data-hx-filter="all" aria-pressed="true">'
               f'All <span class="hx-filter__n">{len(EVENTS)}</span></button>']
    for key, label in PERIODS:
        n = sum(1 for e in EVENTS if e["period"] == key)
        buttons.append(f'<button type="button" class="hx-filter" data-hx-filter="{key}" '
                       f'aria-pressed="false">{label} <span class="hx-filter__n">{n}</span></button>')
    return "".join(buttons)


def archive_html():
    """Every record, as a card that opens its own detail view.

    Without scripting the detail is simply there under each card, so the
    archive reads as a list of complete records. With it, the card opens the
    detail in a dialog and the URL names the record (#record-<id>)."""
    out = []
    periods = dict(PERIODS)
    for e in EVENTS:
        ex = e.get("exhibit")
        if ex:
            thumb = (f'<span class="hx-card__thumb" style="--ar:{ratio(ex)}">'
                     + img_html(ex, "", "(max-width: 700px) 44vw, 220px") + '</span>')
            full = (f'<figure class="hx-rec__figure">'
                    f'<a class="hx-rec__full" href="{IMG}/{ex}-lg.jpg" target="_blank" rel="noopener">'
                    + img_html(ex, e["alt"], "(max-width: 900px) 92vw, 560px", cls="hx-rec__img")
                    + f'<span class="sr-only"> (open the full image)</span></a>'
                    f'<figcaption>{e["caption"]}</figcaption></figure>')
        else:
            thumb = (f'<span class="hx-card__thumb hx-card__thumb--type" aria-hidden="true">'
                     f'<span>{e["when"]}</span></span>')
            full = ""
        out.append(
            f'<li class="hx-item" data-hx-period="{e["period"]}">'
            f'<article class="hx-rec" id="record-{e["id"]}" aria-labelledby="record-{e["id"]}-t">'
            f'<button type="button" class="hx-card" data-hx-open="{e["id"]}" aria-haspopup="dialog">'
            f'{thumb}<span class="hx-card__when">{e["when"]}</span>'
            f'<span class="hx-card__title" id="record-{e["id"]}-t">{e["title"]}</span></button>'
            f'<div class="hx-rec__detail">'
            f'<p class="hx-rec__meta"><span>{e["when"]}</span> &middot; {periods[e["period"]]}</p>'
            f'<h3 class="hx-rec__title">{e["title"]}</h3>'
            f'{full}<p class="hx-rec__body">{e["body"]}</p>'
            f'<p class="hx-rec__source"><span>Source</span> {e["source"]}</p>'
            f'</div></article></li>')
    return "\n".join(out)


def opening_records_html():
    """The records drifting behind the opening's title, at shallow depths.

    Real exhibits, set back and small; the copy is the thing to read. They are
    decoration here — every one appears again, captioned, further down — so
    the whole field is hidden from assistive technology."""
    picks = [("gurudev", 1), ("noc-1996", 2), ("kalam-2007", 3), ("sakshi-2008", 2),
             ("report-2019", 3), ("brainfeed-2017", 1)]
    cards = []
    for n, (name, depth) in enumerate(picks):
        cards.append(f'<span class="hx-float hx-float--{n + 1}" style="--z:{depth};--ar:{ratio(name)}">'
                     + img_html(name, "", "220px", eager=(n < 3)) + '</span>')
    cards.append('<span class="hx-float hx-float--type" style="--z:2;--ar:.8">'
                 '<span class="hx-float__when">1984</span>'
                 '<span class="hx-float__t">One rupee at a time</span></span>')
    cards.append('<span class="hx-float hx-float--type hx-float--type2" style="--z:3;--ar:.8">'
                 '<span class="hx-float__when">6.6.1996</span>'
                 '<span class="hx-float__t">96 students</span></span>')
    return f'<div class="hx-opening__field" aria-hidden="true">{"".join(cards)}</div>'


def expand(content):
    return (content.replace("{{HISTORY_OPENING_RECORDS}}", opening_records_html())
                   .replace("{{HISTORY_CHAPTER_NAV}}", chapter_nav_html())
                   .replace("{{HISTORY_CHAPTERS}}", chapters_html())
                   .replace("{{HISTORY_FILTERS}}", filters_html())
                   .replace("{{HISTORY_ARCHIVE}}", archive_html())
                   .replace("{{HISTORY_COUNT}}", str(len(EVENTS))))


if __name__ == "__main__":
    # A report for whoever confirms the history next: every record's source,
    # every open note, and what was held back.
    #     python3 tools/history.py
    for e in EVENTS:
        print(f"{e['id']:<20} {html.unescape(e['when']):<18} {plain(e['title'])}")
        print(f"{'':<20} source: {plain(e['source'])}")
        if e.get("note"):
            print(f"{'':<20} NOTE:   {e['note']}")
    print("\nHeld back until a source is found:")
    for what, why in UNRESOLVED:
        print(f"  - {what}: {why}")
