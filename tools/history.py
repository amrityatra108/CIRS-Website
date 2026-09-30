#!/usr/bin/env python3
"""The School History archive: every record, where it came from, and the page.

This file is the source record the brief asks for. Each event carries its own
source, and anything that could not be settled is written down in NOTES —
never resolved on the page by guesswork. The page shows the public half of
each record (date, title, description, the exhibit and its source line); the
"note" field and UNRESOLVED below are for whoever confirms the history next,
and are never published.

The page is built in three parts, all from EVENTS:

    SCENES     the moments of the journey at the top of the page, each
               naming the records it tells and the exhibits it shows
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

AR2025 = ('The school&rsquo;s Annual Report, 7 October 2025 &middot; '
          '<a href="assets/documents/school-info/annual-report.pdf" target="_blank" '
          'rel="noopener">Open the PDF</a>')

# name -> (small w, h, large w, h). tools/make-history.py prints these; the
# build writes them into the page so every image reserves its box before it
# loads, without the build needing Pillow.
EXHIBITS = {
    "samadhi-sthal": (640, 427, 1024, 683),
    "report-2025": (640, 828, 1400, 1812),
    "supplied-rupee": (640, 480, 1448, 1086),
    "supplied-opening": (640, 480, 1448, 1086),
    "supplied-isa": (640, 425, 1600, 1063),
    "supplied-poland": (640, 427, 1536, 1024),
    # The school's "history" folder on Drive, each file named for its year
    # (30 September 2026); cut by tools/make-history-supplied.py.
    "supplied-1970": (640, 876, 701, 960),
    "supplied-1994": (640, 480, 1448, 1086),
    "supplied-until-1996": (640, 427, 1536, 1024),
    "supplied-june-1996": (640, 480, 1448, 1086),
    "supplied-2005": (640, 427, 1536, 1024),
    "supplied-2009": (640, 960, 1467, 2200),
    "supplied-2018": (279, 279, 279, 279),
    "supplied-2019": (640, 820, 1600, 2050),
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
     "exhibit": "supplied-1970",
     "alt": "An archival black-and-white photograph of a swami in robes walking across rough "
            "ground on a building site, with others behind him",
     "caption": "A building site, in the photograph the school filed under 1970. The place and "
                "the people pictured are not named in the record.",
     "source": PUBLISHED + '; photograph from the ' + '<a href="https://drive.google.com/file/d/1nAJOfr2_rt_8lhWjU5EZMlPWVXe9ss5b/view" target="_blank" rel="noopener">supplied school archive</a>'},
    {"id": "rupee-1984", "when": "1984", "period": "before",
     "title": "One rupee at a time",
     "summary": "The first collection towards the land: one rupee from each person, gathered on foot.",
     "body": "Swami Sahayanandaji travelled the length and breadth of India on foot, making the "
             "initial collection towards the purchase of the land: one rupee from each "
             "individual.",
     "exhibit": "supplied-rupee",
     "alt": "An archival black-and-white photograph of a collection on foot outside a shop",
     "caption": "A collection on foot. Photograph supplied for the fundraising chapter; "
                "the date and identities in the photograph are not independently recorded.",
     "source": PUBLISHED + '; photograph from the <a href="https://drive.google.com/file/d/1hwLnhl-qm21F-NUtLYMaAdZan2G4BESe/view" target="_blank" rel="noopener">supplied school archive</a>',
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
     "exhibit": "gurudev",
     "alt": "A close colour portrait of Pujya Gurudev Swami Chinmayananda, smiling, in saffron "
            "robes and spectacles",
     "caption": "Pujya Gurudev Swami Chinmayananda. A portrait from the school&rsquo;s archive; "
                "the date of the photograph is not recorded.",
     "source": 'The chronology of Gurudev&rsquo;s life on this site&rsquo;s '
               '<a href="founder.html#life">Founder</a> page; portrait from the ' + '<a href="https://drive.google.com/file/d/1amUjwTsvRJDy5LaRs1lZcMsCy_oA22Qj/view" target="_blank" rel="noopener">supplied school archive</a>',
     "note": "The school's published history does not mention 1993; it moves from 1984 to 1994. "
             "The earlier draft said that after the Mahasamadhi Pujya Guruji 'took the project "
             "upon his own shoulders' — that wording has no source in hand and is not used."},
    {"id": "guruji-1994", "when": "1994", "period": "before",
     "title": "The vision is made concrete",
     "summary": "Pujya Guruji Swami Tejomayananda carries the project forward.",
     "body": "Pujya Guruji Swami Tejomayananda proceeded to concretise the vision of Pujya "
             "Gurudev with unfailing vigour and energy, and the work progressed by leaps and "
             "bounds.",
     "exhibit": "supplied-1994",
     "alt": "An archival black-and-white photograph of a swami holding a plan and pointing "
            "across a building site, men in shirts beside him and foundations behind",
     "caption": "Plans on the site, in the photograph the school filed under 1994. The people "
                "pictured are not named in the record.",
     "source": PUBLISHED + '; photograph from the ' + '<a href="https://drive.google.com/file/d/1cZGB8kauMLJO0K_x0p8ltXiITze37n3e/view" target="_blank" rel="noopener">supplied school archive</a>'},
    {"id": "project-1996", "when": "Until 1996", "period": "before",
     "title": "Guided to completion",
     "summary": "Devotees give generously; the project is guided and executed to completion.",
     "body": "Many devotees around the world contributed generously. Swamini Vimalanandaji and "
             "Dr. G.&nbsp;S. Keshawamurthy played a significant role in guiding and executing "
             "the project to its completion.",
     "exhibit": "supplied-until-1996",
     "alt": "A swamini in saffron at a desk spread with plans, beneath a framed portrait of "
            "Gurudev, a man seated across the desk from her",
     "caption": "Plans on a desk, in the photograph the school filed under &lsquo;Until "
                "1996&rsquo;. The camera&rsquo;s date stamp reads 28 6 1996; the people "
                "pictured are not named in the record.",
     "source": PUBLISHED + '; photograph from the ' + '<a href="https://drive.google.com/file/d/1nGP6aThh6fCOKrK7NsP2yUDtveItFoxz/view" target="_blank" rel="noopener">supplied school archive</a>',
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
     "exhibit": "supplied-opening",
     "alt": "The school inauguration ceremony, with the unveiled plaque recording 6 June 1996",
     "caption": "The inauguration at CIRS. The plaque in the supplied photograph records "
                "Thursday, 6 June 1996, and names the inaugurator and those in whose presence it took place.",
     "source": PUBLISHED + '; <a href="https://drive.google.com/file/d/1XvYfF_NTKD1TYHTh5cIyUqWU_FSrGLcM/view" target="_blank" rel="noopener">the inauguration photograph and its plaque</a>',
     "note": "The plaque is legible only in part in a 2018 school photograph on Drive "
             "('bal sevak award.JPG'). A straight photograph of it would make a strong exhibit "
             "for this record; none is in hand. No photograph of the inauguration itself has "
             "been found at that time. A ceremony photograph was supplied on 30 September 2026; "
             "its legible plaque corroborates the date and occasion. The user approved its use."},
    {"id": "first-school-1996", "when": "June 1996", "period": "early",
     "title": "Ninety-six students, eleven teachers",
     "summary": "96 students in Grades V to VIII, and 11 academic staff.",
     "body": "CIRS started with 96 students from Grade V to Grade VIII and 11 academic staff, "
             "headed by Dr. Jaya Venugopal, with Brahmacharini Sumati Chaitanya and "
             "Brahmachari Samahita Chaitanya as spiritual guides.",
     "exhibit": "supplied-june-1996",
     "alt": "Students in uniform standing in rows before the school's main building, teachers "
            "and guests on its steps and the hills behind",
     "caption": "Students before the main building, in the photograph the school filed under "
                "June 1996. The occasion is not recorded.",
     "source": PUBLISHED + '; photograph from the ' + '<a href="https://drive.google.com/file/d/1R9buBM6OmFiA_V98BRhd77qmf_g6ZPQR/view" target="_blank" rel="noopener">supplied school archive</a>',
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
     "exhibit": "supplied-2005",
     "alt": "A swami in saffron lighting a lamp before a garlanded portrait of Gurudev, staff "
            "and students watching",
     "caption": "A lamp lit before Gurudev&rsquo;s portrait, in the photograph the school "
                "filed under 2005. The occasion and the people pictured are not named in the "
                "record.",
     "source": "The school&rsquo;s own account, supplied for this website; photograph from the "
               + '<a href="https://drive.google.com/file/d/15d6GgKpuhPpvoz50dtOSiEtsr3PuEvqY/view" target="_blank" rel="noopener">supplied school archive</a>',
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
     "exhibit": "supplied-2009",
     "alt": "A woman in a blue silk sari standing on a lawn, smiling",
     "caption": "The photograph the school filed under 2009.",
     "source": 'The school&rsquo;s introduction on <a href="leadership.html">Leadership</a>; '
               'photograph from the ' + '<a href="https://drive.google.com/file/d/14poW2KoFidGFBdhagGkJmGVX3Y9hulgC/view" target="_blank" rel="noopener">supplied school archive</a>'},
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
     "exhibit": "supplied-isa",
     "alt": "The British Council presents a framed International School Award certificate naming CIRS",
     "caption": "The British Council&rsquo;s International School Award presentation. "
                "The supplied photograph names CIRS on the certificate; the photograph date "
                "and the people pictured are not independently recorded.",
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
     "exhibit": "supplied-poland",
     "alt": "Students in a CIRS classroom on a video call with Poland; the whiteboard describes the February 2014 collaboration",
     "caption": "The CIRS&ndash;Poland Student Collaboration Project. The whiteboard in the "
                "supplied photograph names the advertising project and dates it February 2014.",
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
     "exhibit": "supplied-2018",
     "alt": "A portrait of a smiling woman in a pale sari",
     "caption": "The photograph the school filed under 2018.",
     "source": 'The school&rsquo;s introduction on <a href="leadership.html">Leadership</a>; '
               'photograph from the ' + '<a href="https://drive.google.com/file/d/1bDirpVyUpnabY3gKYsHSREsCSpRwMQyG/view" target="_blank" rel="noopener">supplied school archive</a>',
     "note": "The supplied photograph is 279 pixels square, too small for the journey, so it "
             "is shown only in this record, at its own size. Ask the school for a larger copy."},
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
               '<a href="assets/documents/school-info/annual-report-2019.pdf" target="_blank" '
               'rel="noopener">Open the PDF</a>',
     "note": "Superseded as the latest figures by report-2025. The published "
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
     "exhibit": "supplied-2019",
     "alt": "A framed EducationWorld certificate, India School Rankings 2019-20, Co-Ed Boarding "
            "Schools, naming Chinmaya International Residential School, Coimbatore: India 2, "
            "Tamil Nadu 1",
     "caption": "The EducationWorld India School Rankings 2019&ndash;20 certificate, Co-Ed "
                "Boarding Schools: India 2, Tamil Nadu 1. Signed by the publisher and dated "
                "28 September 2019.",
     "source": 'The school&rsquo;s Annual Report, 15 October 2019 &middot; '
               '<a href="assets/documents/school-info/annual-report-2019.pdf" target="_blank" '
               'rel="noopener">Open the PDF</a>; the certificate, from the ' + '<a href="https://drive.google.com/file/d/1-gNcHmuBKqYSS8qVXu3TEgL3v44BxTts/view" target="_blank" rel="noopener">supplied school archive</a>',
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
    # ---- From the Annual Report of 7 October 2025 -----------------------
    {"id": "vigyan-goshti-2024", "when": "2&ndash;6 December 2024", "period": "later",
     "title": "Vigyan Goshti at CIRS",
     "summary": "A five-day seminar for 130 science teachers from across the country.",
     "body": "CIRS hosted Vigyan Goshti, a five-day seminar for science teachers organised by "
             "CCMTEC and led by Smt. Shanti Krishnamurthy, Director of CCMTEC. 130 science "
             "teachers from all over the country attended, with CIRS teachers among the "
             "resource persons.",
     "exhibit": None,
     "source": AR2025},
    {"id": "results-2025", "when": "2025", "period": "later",
     "title": "Board results, 2025",
     "summary": "Class XII: 45 of 47 above 80%. Class X: an average of 89.2%.",
     "body": "In the 2025 CBSE Class XII examination, 34 of 47 students secured above 90% and "
             "45 of 47 above 80% in the aggregate; the Science stream averaged 89% and the "
             "Management stream 93%. In Class X, 56 of 95 students secured 90% or more, 85 "
             "were above 80%, and the class averaged 89.2%. In the IB Diploma, 8 of 19 "
             "students scored above 40 points out of 45, the highest 44, and the class "
             "averaged 38.9.",
     "exhibit": None,
     "source": AR2025,
     "note": "The report gives the IB average as '38.9 %'; with scores 'out of 45' it is "
             "points, and is published as 38.9. The report's 'Out of 600 up IB school, CIRS "
             "stands 15th in the world' cannot be read reliably and is not published."},
    {"id": "solar-2025", "when": "9 May 2025", "period": "later",
     "title": "An alumnus gives the school solar power",
     "summary": "Raghav Agarwalla, who left CIRS in 2004, funds a 200&nbsp;kVA solar plant.",
     "body": "Raghav Agarwalla, an alumnus who passed out of CIRS in 2004, donated "
             "&#8377;83,74,000 for the 200&nbsp;kVA solar panels installed behind the school "
             "auditorium.",
     "exhibit": None,
     "source": AR2025,
     "note": "The report writes the sum as 'Rs. 83,74,000 (84 Lakh, 74 thousand)'. The figure "
             "and the words disagree (83,74,000 is 83 lakh 74 thousand); the figure is "
             "published. Confirm with the school."},
    {"id": "ncc-2025", "when": "1&ndash;10 July 2025", "period": "later",
     "title": "Best Cadets at the NCC camp",
     "summary": "36 CIRS cadets attend the annual training camp; the school wins Best Cadets.",
     "body": "36 NCC cadets from CIRS took part in the Annual Training Camp at Kalaignar "
             "Karunanidhi Institute of Technology, winning medals in the drill test, quiz, "
             "relay, shot put and football, and CIRS received the overall Best Cadets award.",
     "exhibit": None,
     "source": AR2025},
    {"id": "yoga-2025", "when": "13 July 2025", "period": "later",
     "title": "South Zone Yoga overall championship",
     "summary": "Six gold, five silver and six bronze medals at Erode.",
     "body": "At the South Zone Yoga Competition organised by the School Games Sport "
             "Development Foundation India at Erode, CIRS students won 6 gold, 5 silver and 6 "
             "bronze medals and the overall championship.",
     "exhibit": None,
     "source": AR2025},
    {"id": "mun-2025", "when": "August 2025", "period": "later",
     "title": "Harvard and IIMUN",
     "summary": "40 students at Harvard Model United Nations; 34 at IIMUN in Mumbai.",
     "body": "Forty CIRS students took part in Harvard Model United Nations from 14 to 17 August "
             "2025, where two received Outstanding Delegate awards; over the same dates, 34 "
             "students represented nations at the IIMUN Championship Conference in Mumbai.",
     "exhibit": None,
     "source": AR2025},
    {"id": "report-2025", "when": "7 October 2025", "period": "later",
     "title": "The school in its twenty-ninth year",
     "summary": "596 students from 16 Indian states and 16 countries; second in India&rsquo;s "
                "co-educational boarding schools.",
     "body": "In its 29th year the school reported 596 students &mdash; 378 boys and 218 girls "
             "&mdash; from 16 Indian states and 16 countries, with 70 faculty members and 71 "
             "members of the administrative team, and remained one of the CBSE&rsquo;s Lead "
             "Schools. Education World ranked CIRS second in the country among co-educational "
             "boarding schools and first in Tamil Nadu and Coimbatore for the 14th consecutive "
             "year; Brainfeed ranked it third in the country and first in the state and the "
             "city.",
     "exhibit": None,
     "source": AR2025,
     "note": "The report says '16 states in India and 16 different countries across the "
             "world'; the 2019 report said '18 other countries'. Whether India is counted "
             "among the 16 is not stated, so the page says '16 countries'. The ranking's "
             "survey year is not given. Fourteenth consecutive year agrees with the 2019 "
             "report's eighth."},
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

# The journey: the history told as one continuous passage, a moment at a
# time. Every sentence is a record's own wording or a plain shortening of it.
#   records  the events a moment tells; the first is the one its
#            "Read the record" link opens
#   plates   images shown with it, each the exhibit of one of those records
#   notes    further records, listed with their dates
#   index    the moment's label in the small index at the edge of the window
# The 3D placement of each plate is presentation, and lives with the rest of
# the camera path in assets/js/history-world.js.
SCENES = [
    {"id": "chapter-idea", "index": "1970s", "year": "1970s",
     "head": "The idea came first.",
     "text": ["Pujya Gurudev Swami Chinmayananda conceived an international school in India, "
              "and the idea met with an overwhelming response from around the world. Bangalore, "
              "Lucknow, the Andamans and Himachal Pradesh were weighed before Coimbatore was "
              "chosen."],
     "records": ["idea-1970s"], "plates": ["gurudev"]},
    {"id": "chapter-rupee", "index": "1984", "year": "1984", "big": "&#8377;1",
     "head": "One rupee at a time.",
     "text": ["To buy the land, Swami Sahayanandaji travelled the length and breadth of India on "
              "foot, making the first collection: one rupee from each person."],
     "records": ["rupee-1984"]},
    {"id": "chapter-shape", "index": "1993", "year": "3 August 1993", "quiet": True,
     "head": "Gurudev attains Mahasamadhi.",
     "text": ["Pujya Gurudev Swami Chinmayananda attained Mahasamadhi on 3 August 1993. He did "
              "not see the school he had conceived open its doors."],
     "records": ["mahasamadhi-1993"]},
    {"id": "chapter-concrete", "index": "1994", "year": "1994",
     "head": "The vision is made concrete.",
     "text": ["Pujya Guruji Swami Tejomayananda proceeded to concretise the vision of Pujya "
              "Gurudev with unfailing vigour and energy, and the work progressed by leaps and "
              "bounds.",
              "Devotees around the world contributed generously. Swamini Vimalanandaji and "
              "Dr. G.&nbsp;S. Keshawamurthy guided and executed the project to its completion."],
     "records": ["guruji-1994", "project-1996"]},
    {"id": "chapter-opening", "index": "1996", "year": "6 June 1996",
     "head": "The school opens.",
     "text": ["The Chinmaya International Residential School was inaugurated by Pujya Swami "
              "Chidanandaji, President of The Divine Life Society. The plaque at the main "
              "building records that he did so in the presence of Swami Tejomayananda, Head of "
              "Chinmaya Mission, on Thursday, 6 June 1996."],
     "records": ["inauguration-1996"]},
    {"id": "chapter-first", "index": None, "year": "June 1996",
     "head": "Ninety-six students, eleven teachers.",
     "text": ["CIRS started with 96 students from Grade V to Grade VIII and 11 academic staff, "
              "headed by Dr. Jaya Venugopal, with Brahmacharini Sumati Chaitanya and "
              "Brahmachari Samahita Chaitanya as spiritual guides.",
              "Within weeks, on 15 July 1996, the Government of Tamil Nadu raised no objection "
              "to the middle classes being affiliated to the CBSE, on one condition: that Tamil "
              "be taught as a second language."],
     "facts": [("96", "students"), ("11", "academic staff"), ("V&ndash;VIII", "grades")],
     "records": ["first-school-1996", "noc-1996"], "plates": ["noc-1996"]},
    {"id": "chapter-early", "index": "2005", "year": "2005 &ndash; 2010",
     "head": "A school finds its voice.",
     "text": ["A Resident Director, a meeting with the President at Rashtrapati Bhavan, and "
              "newsletters the students wrote, edited and laid out themselves."],
     "notes": ["director-2005", "kalam-2007", "sakshi-2008", "principal-2009",
               "reflections-2010", "isa-2010"],
     "records": ["director-2005"], "plates": ["kalam-2007", "sakshi-2008", "reflections-2010"]},
    {"id": "chapter-later", "index": "2011", "year": "2011 &ndash; 2019",
     "head": "A wider world, and a longer record.",
     "text": ["The International School Award, the CCMT Education Cell&rsquo;s Vision Award for "
              "2012, and by 2019 a school of 580 students from 22 Indian states and 18 other "
              "countries."],
     "notes": ["isa-award-2011", "vision-award-2012", "poland-2014", "brainfeed-2017",
               "director-2018", "report-2019"],
     "links": [("Our Results", "our-results.html"), ("Our Laurels", "our-laurels.html")],
     "records": ["vision-award-2012"], "plates": ["vision-2012", "brainfeed-2017", "report-2019"]},
]

# Photographs of the campus as it stands, cut by tools/make-photos.py for
# other pages. Neither carries a date, so neither caption gives one.
CAMPUS = {
    "forest-air": (1600, 900, "The CIRS campus from the air, the forest closing around it on "
                              "every side",
                   "The campus from the air, the forest closing around it on every side."),
    "campus-band": (1920, 1080, "The CIRS campus below the Western Ghats",
                    "The campus below the Western Ghats."),
}

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
     "itself is unconfirmed. The Annual Report of 7 October 2025 records a different "
     "prize: Team Vayunigrah overall winners of the JK Lakshmipat University 'My City, My Lab' "
     "Ideathon on 1 December 2024. That does not settle the SSVM claim."),
]

BY_ID = {e["id"]: e for e in EVENTS}
assert len(BY_ID) == len(EVENTS), "every event needs a unique id"
BY_EXHIBIT = {e["exhibit"]: e for e in EVENTS if e.get("exhibit")}
# Context images supplement a record without changing its historical account
# or replacing its original exhibit/caption. Each photograph belongs to one
# presentation on this page. Source masters and URLs are recorded alongside it.
CONTEXT_EXHIBITS = {
    "samadhi-sthal": {
        "record": "mahasamadhi-1993",
        "alt": "Gurudev's Samadhi Sthal in Sidhbari with the mountains behind it",
        "caption": "Gurudev&rsquo;s Samadhi Sthal at Sidhbari. Memorial photograph from Chinmaya Archives; photograph date unrecorded.",
        "source": '<a href="https://archives.chinmayamission.com/sidhbari-samadhi-sthal" target="_blank" rel="noopener">Chinmaya Archives photograph</a>',
    },
    "report-2025": {
        "record": "report-2025",
        "alt": "First page of the CIRS Annual Report headed 7 October 2025",
        "caption": "The school&rsquo;s Annual Report, 7 October 2025, first page.",
    },
}
for _name, _context in CONTEXT_EXHIBITS.items():
    BY_EXHIBIT[_name] = {**BY_ID[_context["record"]], **_context}
for _s in SCENES:
    # The school's own photographs, placed by the year each was filed under.
    if _s['id'] == 'chapter-idea':
        _s['plates'] = ['supplied-1970']
    if _s['id'] == 'chapter-shape':
        _s['plates'] = ['samadhi-sthal']
    if _s['id'] == 'chapter-concrete':
        _s['plates'] = ['supplied-1994', 'supplied-until-1996']
    if _s['id'] == 'chapter-rupee':
        _s['plates'] = ['supplied-rupee']
    if _s['id'] == 'chapter-opening':
        _s['plates'] = ['supplied-opening']
    if _s['id'] == 'chapter-early':
        _s['plates'] = ['supplied-2005', 'kalam-2007', 'sakshi-2008', 'supplied-2009',
                        'reflections-2010']
    if _s['id'] == 'chapter-first':
        _s['plates'] = ['supplied-june-1996', 'noc-1996']
        _s['text'] = [BY_ID['first-school-1996']['summary'],
                     'On 15 July 1996, Tamil Nadu raised no objection to CBSE affiliation, '
                     'on one condition: Tamil should be taught as a second language.']
    if _s['id'] == 'chapter-later':
        _s['plates'] = ['supplied-isa', 'vision-2012', 'supplied-poland', 'supplied-2019']
        _s['notes'].insert(_s['notes'].index('report-2019'), 'ranking-2019')
SCENES.append({
    'id': 'chapter-recent', 'index': '2025', 'year': '2024 &ndash; 2026',
    'head': 'The next generation.',
    'text': [BY_ID['report-2025']['summary'], BY_ID['ib-2026']['summary']],
    'records': ['report-2025', 'ib-2026'],
    'plates': ['report-2025'],
    'notes': ['vigyan-goshti-2024', 'results-2025', 'solar-2025', 'ncc-2025',
              'yoga-2025', 'mun-2025', 'report-2025', 'cbse-2026', 'ib-2026'],
})
for _s in SCENES:
    for _id in _s["records"] + _s.get("notes", []):
        assert _id in BY_ID, f"{_s['id']} names an unknown event {_id}"
    for _x in _s.get("plates", []):
        assert _x in BY_EXHIBIT and BY_EXHIBIT[_x]["id"] in _s["records"] + _s.get("notes", []),             f"{_s['id']} shows {_x}, which is not the exhibit of a record it tells"

# The portrait appears once in the typography expansion. Other exhibits each
# have one chapter owner; archive entries link to these photographs instead
# of reproducing them. A repeated assignment fails the source build.
EXPANSION_EXHIBIT = "gurudev"
_cinematic_exhibits = [EXPANSION_EXHIBIT] + [x for s in SCENES for x in s.get("plates", [])]
assert len(_cinematic_exhibits) == len(set(_cinematic_exhibits)), "a History photograph must have one presentation"
CINEMATIC_EXHIBITS = set(_cinematic_exhibits)


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


# ---- the journey ---------------------------------------------------------------

def record_link(event_id, label="Read the record"):
    e = BY_ID[event_id]
    return (f'<a class="hj-more" href="#record-{e["id"]}" data-hx-record="{e["id"]}">{label}'
            f'<span class="sr-only">: {plain(e["title"])}</span></a>')


def plate_html(name, eager=False):
    """One exhibit as a figure: an image and its record's own caption.

    The caption is the record's alone. It is never prefixed with the record's
    date: the portrait of Gurudev, for one, is not of the year it is shown with.

    With the 3D journey running, the image is drawn in the scene instead and
    the figure keeps only its caption, set beside the plate; everywhere else
    it is simply the photograph, in the text's column."""
    e = BY_EXHIBIT[name]
    return (f'<figure class="hj-fig" data-hj-plate="{name}" style="--ar:{ratio(name)}">'
            + img_html(name, e["alt"], "(max-width: 999px) 88vw, 640px", eager=eager)
            + f'<figcaption class="hj-cap">{e["caption"]}</figcaption></figure>')


def campus_html(name, cls, eager=False):
    w, h, alt, caption = CAMPUS[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="hj-fig {cls}" data-hj-plate="{name}" style="--ar:{w / h:.4f}">'
            f'<img src="assets/img/{name}.jpg" width="{w}" height="{h}" alt="{attr(alt)}" '
            f'{load} decoding="async">'
            f'<figcaption class="hj-cap">{caption}</figcaption></figure>')


def expansion_html():
    e = BY_EXHIBIT[EXPANSION_EXHIBIT]
    return ('<figure class="hj-expansion__image">'
            + img_html(EXPANSION_EXHIBIT, e["alt"], "(max-width: 767px) 88vw, 80vw")
            + f'<figcaption>{e["caption"]}</figcaption></figure>')


def index_html():
    items = "".join(f'<li><a href="#{s["id"]}" data-hj-go="{s["id"]}" aria-label="{plain(s["year"] + ": " + s["head"])}">{s["index"] or "Opening class"}</a></li>'
                    for s in SCENES)
    return (f'<nav class="hj-index" aria-label="Moments in the history"><ol>{items}'
            f'<li><a href="#chapter-now" data-hj-go="chapter-now">Now</a></li></ol></nav>')


def scenes_html():
    out = []
    for n, s in enumerate(SCENES):
        big = f'<p class="hj-big" aria-hidden="true">{s["big"]}</p>' if s.get("big") else ""
        paras = "".join(f'<p class="hj-copy">{t}</p>' for t in s["text"])
        facts = ""
        if s.get("facts"):
            facts = ('<dl class="hj-facts">' + "".join(
                f'<div><dt>{label}</dt><dd>{figure}</dd></div>' for figure, label in s["facts"])
                + '</dl>')
        notes = ""
        if s.get("notes"):
            notes = ('<ol class="hj-notes">' + "".join(
                f'<li><a href="#record-{i}" data-hx-record="{i}">'
                f'<span class="hj-notes__when">{BY_ID[i]["when"]}</span>'
                f'<span class="hj-notes__what">{BY_ID[i]["summary"]}</span></a></li>'
                for i in s["notes"]) + '</ol>')
        links = "".join(f'<a class="hj-more" href="{href}">{label}</a>'
                        for label, href in s.get("links", []))
        more = record_link(s["records"][0])
        plates = "".join(plate_html(x, eager=(n == 0)) for x in s.get("plates", []))
        context_sources = [CONTEXT_EXHIBITS[x]["source"] for x in s.get("plates", [])
                           if x in CONTEXT_EXHIBITS and "source" in CONTEXT_EXHIBITS[x]]
        source = BY_ID[s["records"][0]]["source"]
        if context_sources:
            source += '; ' + '; '.join(dict.fromkeys(context_sources))
        quiet = " hj-scene--quiet" if s.get("quiet") else ""
        out.append(
            f'<section class="hj-scene{quiet}" id="{s["id"]}" data-hj-scene aria-labelledby="{s["id"]}-h">'
            f'<div class="hj-text" tabindex="-1">'
            f'<p class="hj-year">{s["year"]}</p>{big}'
            f'<h2 class="hj-head" id="{s["id"]}-h">{s["head"]}</h2>'
            f'{paras}{facts}{notes}'
            f'<p class="hj-actions">{more}{links}</p>'
            f'<p class="hj-source">{source}</p>'
            f'</div>'
            + ('<div class="hj-medallion" aria-hidden="true"><span>&#8377;1</span></div><p class="hj-illustration">Illustrative medallion</p>' if s['id'] == 'chapter-rupee' else '')
            + (f'<div class="hj-plates">{plates}</div>' if plates else "")
            + '</section>')
    return "\n".join(out)


def now_html():
    return campus_html("forest-air", "hj-fig--air")


def full_html():
    return campus_html("campus-band", "hj-fig--full")


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
            if ex in CINEMATIC_EXHIBITS:
                full = (f'<div class="hx-rec__exhibit"><p>{e["caption"]}</p>'
                        f'<a href="{IMG}/{ex}-lg.jpg" target="_blank" rel="noopener">View the archival image</a></div>')
            else:
                full = (f'<figure class="hx-rec__figure">'
                        f'<a class="hx-rec__full" href="{IMG}/{ex}-lg.jpg" target="_blank" rel="noopener">'
                        + img_html(ex, e["alt"], "(max-width: 900px) 92vw, 560px", cls="hx-rec__img")
                        + f'<span class="sr-only"> (open the full image)</span></a>'
                        f'<figcaption>{e["caption"]}</figcaption></figure>')
        else:
            full = ""
        disclosure = len(e['body']) > 420
        detail_start = '<details class="hx-disclosure"><summary>Expand this account</summary>' if disclosure else ''
        detail_end = '</details>' if disclosure else ''
        out.append(
            f'<li class="hx-item" data-hx-period="{e["period"]}" data-hx-decade="{decade(e)}">'
            f'<article class="hx-rec" id="record-{e["id"]}" aria-labelledby="record-{e["id"]}-t">'
            f'<button type="button" class="hx-card" data-hx-open="{e["id"]}" aria-haspopup="dialog">'
            f'<span class="hx-card__when">{e["when"]}</span>'
            f'<span class="hx-card__title" id="record-{e["id"]}-t">{e["title"]}</span>'
            f'<span class="hx-card__summary">{e["summary"]}</span><span class="hx-card__open">Read record</span></button>'
            f'{detail_start}<div class="hx-rec__detail">'
            f'<p class="hx-rec__meta"><span>{e["when"]}</span> &middot; {periods[e["period"]]}</p>'
            f'<h3 class="hx-rec__title">{e["title"]}</h3>'
            f'{full}<p class="hx-rec__body">{e["body"]}</p>'
            f'<p class="hx-rec__source"><span>Source</span> {e["source"]}</p>'
            f'</div>{detail_end}</article></li>')
    return "\n".join(out)


def decade(event):
    import re
    year = int(re.search(r'(?:19|20)\d{2}', html.unescape(event['when'])).group())
    return str(year // 10 * 10)


def decade_options():
    return ''.join(f'<option value="{d}">{d}s</option>' for d in sorted({decade(e) for e in EVENTS}))


def expand(content):
    return (content.replace("{{HISTORY_INDEX}}", index_html())
                   .replace("{{HISTORY_EXPANSION}}", expansion_html())
                   .replace("{{HISTORY_SCENES}}", scenes_html())
                   .replace("{{HISTORY_NOW}}", now_html())
                   .replace("{{HISTORY_FULL}}", full_html())
                   .replace("{{HISTORY_FILTERS}}", filters_html())
                   .replace("{{HISTORY_DECADES}}", decade_options())
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
