#!/usr/bin/env python3
"""The term's news, written from the school's CVP report.

The school compiles a Chinmaya Vision Programme (CVP) report each term: one
page set per event, each giving the date, the learning objectives (knowing,
feeling, doing), what took place, the outcomes and some student feedback.
The report for October 2025 to March 2026 runs to 275 pages. These articles
are written from it for the News page.

The rule is the one the rest of the site keeps: nothing is added. Every
name, date, place, number and result below is the report's. The prose is
the site's, but where the report states an objective or an outcome, the
article says it in the report's terms and does not improve on it. Where
the report contradicts itself, the reading that its own text supports is
used and the other left out:

  * Kelvi Kalam is headed 11.09.2025 but its text says 11 November 2025,
    and it sits among the November quizzes. November is used.
  * The InFact quiz and the "Inter-school GK quiz" are the same event at
    CIT on 13 November 2025, reported twice. It appears once.
  * The Science Quiz & Expo and "Thulir" are the same event on
    29 October 2025. It appears once.
  * The girls' swimming meet is headed 24.11 but its text says
    22 November 2025. The text is used.
  * The report's introduction mentions an SSVM Studentrepreneur result that
    none of its pages records. It is left out.
  * A Tagore quiz dated 7 May 2025 falls outside the term and is left out.

Some results pages are cut off in the copy the school supplied. Where a
place or a name is not legible, the article says less rather than guess.

The photographs are the report's own, cut by tools/make-news-cvp.py into
assets/img/news/cvp/. Screenshots, feedback sheets, forms and clip-art are
not used. Some articles have no usable photograph and run without one.

    slug        the page it becomes, <slug>.html
    section     the News page's filter category
    date        as it reads; datetime, machine-readable
    dek         the one-line summary on the News page and under the title
    who         the classes or people it concerns, for the article's rail
    blocks      ("h", heading) and ("p", paragraph), in order
    photos      (page, xref, alt) in the report PDF; the first leads
    lead        True for the three stories that open the term's section
"""
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = "assets/img/news/cvp"

TERM = "October 2025 – March 2026"

ARTICLES = [
    # ---------------------------------------------------------------- Arts
    {
        "slug": "masquerade-2025",
        "title": "Masquerade: four houses, four plays",
        "section": "Arts",
        "date": "23–26 November 2025",
        "datetime": "2025-11-23",
        "lead": True,
        "dek": "Students wrote, designed and staged their own plays, turning Vraja into a theatre from 23 to 26 November.",
        "who": "All four houses",
        "photos": [
            (42, 6750, "A CIRS student in tiger face paint and costume performing on stage during Masquerade"),
            (41, 6739, "A Masquerade cast on stage in costume"),
            (41, 6740, "A performer with a staff under yellow stage light during Masquerade"),
        ],
        "blocks": [
            ("p", "From 23 to 26 November 2025, Vraja became a theatre. Each of the four houses presented a play at Masquerade, and the students took responsibility for every part of the production: brainstorming the idea, scripting the scenes, designing the costumes, preparing the backdrops and organising the stage. Their work culminated in a one-hour theatrical showcase."),
            ("h", "The plays"),
            ("p", "The four productions explored human emotion, relationships, sacrifice, courage and self-discovery. El Diablo portrayed fear, guilt, regret and temptation through a mysterious mask that manipulates hidden pain. Vantara followed Mowgli's dangerous journey through betrayal, sacrifice and courage as he fought to restore peace to the jungle. Ivysherin unfolded the secrets of a town trapped under the power of music, and Melora told a story of love, family, sacrifice and the true meaning of happiness."),
            ("h", "What it set out to do"),
            ("p", "The school's aim was for students to understand the elements of theatre, from storytelling and character to stage production; to grow in empathy, confidence and teamwork; and to learn by scripting, designing, acting and organising a performance together."),
            ("h", "What it achieved"),
            ("p", "The report records that the productions built students' confidence, communication and leadership, and gave them practice in collaborating on a large piece of work. The plays asked the audience, and the casts, to reflect on moral choices, relationships and inner strength, and the preparation drew on creativity, artistic expression and critical thinking."),
        ],
    },
    {
        "slug": "fine-arts-week-2026",
        "title": "Fine Arts Week: ragas, Bharatanatyam and dry leaves",
        "section": "Arts",
        "date": "6–7 March 2026",
        "datetime": "2026-03-06",
        "lead": True,
        "dek": "Swaranjali brought Hindustani and Carnatic music to one stage, Natyanjali presented Bharatanatyam, and the Art Room filled with compositions in dry leaves.",
        "who": "Grades 5–11",
        "photos": [
            (201, 8334, "Two students playing tabla at the Swaranjali Sangeet Sabha"),
            (201, 8335, "Singers performing at the Swaranjali Sangeet Sabha"),
            (206, 8374, "Students arranging dry leaves into compositions in the Art Room"),
            (207, 8385, "Finished artworks made from dry leaves at the Dry Leaves Composition Competition"),
        ],
        "blocks": [
            ("p", "Fine Arts Week in March 2026 set out to deepen students' connection with India's classical arts, and to give them the experience of preparing for and performing before an audience."),
            ("h", "Swaranjali Sangeet Sabha, 6 March"),
            ("p", "The music department's Swaranjali brought the Hindustani and Carnatic traditions to a single stage. Students sang in Raag Bhimpalas, Raaga Senjurutti and Raaga Bowli, and presented compositions including Vaishnava Janato, Thiruppugazh and Brahmam Okate, in group singing that asked for discipline in both laya and swara. The school records that the students improved their vocal skill, rhythm and stage presentation, and that the devotional compositions carried values of humility, devotion and respect."),
            ("h", "Natyanjali, 7 March"),
            ("p", "Students of Grades 5 to 9 presented a Bharatanatyam programme that moved from invocation to storytelling: the Dhyana Shloka, a Devi Stuti, Alarippu, Pushpanjali and Murugar Kauthuvam. Each piece asked for precision in rhythm (tala), gesture (mudra) and expression (bhava), and for a group to move as one. The school notes that the performances deepened the dancers' respect for India's cultural and spiritual heritage, and that the devotional items nurtured reflection and reverence."),
            ("h", "Dry Leaves Composition Competition, 6 March"),
            ("p", "In the Art Room, students of Grades 9 and 11 competed house-wise in teams of two, each creating a composition from dry leaves on a theme of their own choosing. The competition joined art to environmental awareness: it asked students to work with natural, sustainable materials and to experiment with texture, shape and arrangement. The report records gains in creative thinking and design, and in teamwork and communication."),
        ],
    },
    {
        "slug": "inter-house-arts-2026",
        "title": "Inter-house stages: instruments, film songs and dance",
        "section": "Arts",
        "date": "January – February 2026",
        "datetime": "2026-02-18",
        "dek": "Solo instrumentalists, karaoke singers and a 48-strong junior dance competition gave every house a place on the stage.",
        "who": "Junior and senior school",
        "photos": [
            (209, 8405, "Junior school students in costume performing a group dance on stage in the MPH"),
            (210, 8416, "A junior house dance team mid-performance at the Inter-House Group Dance Competition"),
            (198, 15142, "A student playing guitar at the Inter-House Solo Instrumental Competition"),
            (198, 15145, "A student playing tabla at the Inter-House Solo Instrumental Competition"),
        ],
        "blocks": [
            ("p", "Between January and February 2026 a run of inter-house competitions gave students across the school a stage, and a reason to practise for it."),
            ("h", "Solo Instrumental, 18 February"),
            ("p", "The Inter-House Solo Instrumental Competition for sub-junior and junior students was held in the MPH in four categories: Wind, String, Keyboard and Rhythm. Each house's captains chose one participant per category. The school's aims were that students learn more of their instruments and their techniques, build confidence and overcome stage fear, and connect emotionally with the music they play. The report notes that participants did overcome stage fear, and that the discipline of playing developed coordination and concentration."),
            ("h", "Kal Aaj Aur Kal, 20 February"),
            ("p", "At Gokul (MPH), students sang Bollywood film songs to karaoke, tracing a journey from old classics to recent hits. The evening celebrated the evolution of Indian film music; for the singers, the report records improved voice modulation, stage presentation and composure before an audience."),
            ("h", "Junior Group Dance, 27 February"),
            ("p", "Forty-eight students represented their houses at the Inter-House Group Dance Competition for the Junior School in the MPH. The report notes the teams' synchronisation, expressive movement and teamwork, and records that the regular practice needed to prepare built discipline, time management and responsibility, as well as coordination, balance and rhythm."),
            ("h", "English Literary Competitions, January"),
            ("p", "In January, the Junior School's English literary competitions in creative writing, poetry recitation and short story-telling gave younger students their own platform for language and performance."),
        ],
    },
    {
        "slug": "vasant-panchami-2026",
        "title": "Vasant Panchami and the music of the Bhakti poets",
        "section": "Arts",
        "date": "23 January 2026",
        "datetime": "2026-01-23",
        "dek": "After the Saraswati worship, the musician Smt. Vidhya Shah led a three-hour workshop on the Bhakti Movement in music.",
        "who": "Students across the school",
        "photos": [
            (174, 8064, "Students accompanying on tabla at the Vasant Panchami music workshop"),
            (175, 8074, "The Saraswati pooja on Vasant Panchami"),
            (174, 8063, "Students filling the hall for the Vasant Panchami music workshop"),
        ],
        "blocks": [
            ("p", "On 23 January 2026 the school celebrated Vasant Panchami, the day dedicated to the worship of Goddess Saraswati, with reverence and devotion."),
            ("p", "In the afternoon, the accomplished musician Smt. Vidhya Shah conducted a three-hour workshop on the Bhakti Movement in Music. She wove together devotion, history and melody, presenting the compositions of Namdev, Amir Khusro, Surdas and Kabir Das in a range of ragas."),
            ("h", "Why it mattered"),
            ("p", "The day was planned so that students would understand the spiritual and cultural significance of Vasant Panchami and what the Bhakti Movement gave to Indian music and devotion, and would come to it through participation in the pooja and the workshop rather than as an audience alone."),
            ("p", "The school records that the workshop deepened students' appreciation of Indian classical music, devotional traditions and the Bhakti Movement; encouraged reflection and an emotional connection through music; and inspired students to explore music as a means of self-expression and inner growth."),
        ],
    },
    # ----------------------------------------------------------- Community
    {
        "slug": "diwali-2025",
        "title": "Diwali and Bhai Dooj on campus",
        "section": "Community",
        "date": "20 October 2025",
        "datetime": "2025-10-20",
        "dek": "A Krishna Pooja, a carnival, the Lakshmi Pooja and an illuminated campus, followed the next day by Bhai Dooj.",
        "who": "The whole school",
        "photos": [
            (193, 8255, "Students lighting sparklers on Diwali night"),
            (193, 8256, "Students holding lit diyas on Diwali evening"),
            (193, 8253, "Students seated before the altar at the Krishna Pooja on Diwali morning"),
            (193, 8252, "Students on campus during the Diwali celebrations"),
        ],
        "blocks": [
            ("p", "The Festival of Lights was celebrated at CIRS on 20 October 2025. The day began with a Krishna Pooja in the morning, setting a peaceful and spiritual tone for the celebrations that followed."),
            ("p", "A carnival organised by the Spiritual Department added to the excitement of the day. The highlight was the Lakshmi Pooja, followed by the bursting of crackers, marking prosperity, hope and new beginnings, and the illuminated campus reflected the spirit of the festival."),
            ("p", "The celebrations continued the next day with Bhai Dooj, when sisters organised a special programme for their brothers."),
            ("h", "What the festival taught"),
            ("p", "The school's aim was for students to understand the cultural and spiritual significance of Diwali and Bhai Dooj, and to experience devotion, gratitude and togetherness by taking an active part in the poojas and the celebrations. The report records that the festival fostered harmony and joyful participation, and deepened students' appreciation of Indian culture."),
        ],
    },
    {
        "slug": "childrens-day-2025",
        "title": "Children's Day: the teachers take the stage",
        "section": "Community",
        "date": "14 November 2025",
        "datetime": "2025-11-14",
        "dek": "Teachers danced, sang, walked a fashion show and performed a skit called Time Travel for their students.",
        "who": "Students and teachers",
        "photos": [
            (38, 6712, "CIRS teachers in costume performing a skit before a jungle backdrop on Children's Day"),
            (38, 6714, "Teachers singing on stage during the Children's Day programme"),
            (38, 6713, "Teachers gathered on stage at the end of the Children's Day programme"),
        ],
        "blocks": [
            ("p", "Children's Day is one of the most eagerly awaited days at CIRS, and on 14 November 2025 the teachers organised a programme exclusively for the students."),
            ("p", "The stage came alive with the teachers' dances and songs and a fashion show. The skit Time Travel was the highlight of the celebration and was warmly received by the students. A special dinner rounded off the day."),
            ("h", "Why it matters"),
            ("p", "The day is meant to recognise the value of childhood, creativity and happiness, and to foster joy, gratitude and a sense of belonging between students and teachers. The school records that the celebration strengthened the Chinmaya Vision Programme values of love, care, gratitude, joy and togetherness, and encouraged unity and mutual respect."),
        ],
    },
    {
        "slug": "pongal-2026",
        "title": "Pongal and Mattu Pongal",
        "section": "Community",
        "date": "15 January 2026",
        "datetime": "2026-01-15",
        "dek": "Painted pots, rangoli, the Pongal pooja and an offering to the Sun God, and the next day a visit to Chinmaya Ashram for Mattu Pongal.",
        "who": "Shishu Vatika to Grade XII",
        "photos": [
            (195, 8279, "Students in traditional attire preparing Pongal on campus"),
            (196, 8291, "Students performing a dance on stage at the Pongal cultural programme"),
        ],
        "blocks": [
            ("p", "CIRS celebrated the harvest festival of Pongal on 15 January 2026. The celebrations began on the eve of the festival, when students from Shishu Vatika to Grade XII painted traditional Pongal pots."),
            ("p", "On the day, students decorated their allotted spaces with rangoli and, in traditional attire, took part in the Pongal pooja and the ceremonial preparation of Pongal. The celebration culminated in offerings to the Sun God, followed by cultural performances on the values and traditions of the harvest festival."),
            ("p", "The next day, Junior School students visited Chinmaya Ashram for the Mattu Pongal celebrations, where they learned the significance of the occasion and fed the cows and calves."),
            ("h", "What it taught"),
            ("p", "The festival was planned so that students would understand the cultural, agricultural and spiritual significance of Pongal and Mattu Pongal, and would develop gratitude towards nature, respect for tradition and compassion for living beings. The report records that it helped students recognise the harmony between people, animals and nature, and fostered creativity and teamwork."),
        ],
    },
    {
        "slug": "national-youth-day-2026",
        "title": "National Youth Day",
        "section": "Community",
        "date": "12 January 2026",
        "datetime": "2026-01-12",
        "dek": "A Youth Yatra, Chinmaya Yuvakendra activities and a singing presentation, in the spirit of Gurudev and Swami Vivekananda.",
        "who": "Students across the school",
        "photos": [
            (221, 8520, "A student with hoops during the National Youth Day activities"),
            (220, 8513, "Students playing a game outdoors on National Youth Day"),
        ],
        "blocks": [
            ("p", "National Youth Day was celebrated at CIRS on 12 January 2026. Students took part in the Youth Yatra, Chinmaya Yuvakendra activities and a singing presentation."),
            ("p", "The day drew on the teachings of Pujya Gurudev Swami Chinmayananda and Swami Vivekananda, and on what they ask of young people: a life of purpose, discipline and dedication."),
            ("h", "What it set out to do"),
            ("p", "The school's aims were for students to understand these teachings and their relevance today, to find in them patriotism, self-confidence and a sense of purpose, and to practise discipline and teamwork through youth-led activities. The report records that the day inspired students to carry these values into daily life and strengthened their leadership, confidence and communication."),
        ],
    },
    {
        "slug": "families-beyond-borders-2026",
        "title": "Families Beyond Borders: Grade 6 speaks to the world",
        "section": "Community",
        "date": "24 February 2026",
        "datetime": "2026-02-24",
        "dek": "At a global online celebration of the UAE's Year of Family, Grade 6 described residential life at CIRS and sang Matri Sthavanam.",
        "who": "Grade 6",
        "photos": [
            (257, 8816, "The Families Beyond Borders session on screen, with participants from several countries"),
            (257, 8817, "Grade 6 students in their classroom during the Families Beyond Borders session"),
        ],
        "blocks": [
            ("p", "Families Beyond Borders was a global online celebration organised by Dewvale School, Al Quoz, for the UAE's Year of Family, held on Google Meet. It brought together participants from several countries for storytelling, group discussion and cultural sharing on the place of the family in people's lives."),
            ("p", "Grade 6 students from CIRS spoke about their residential life at the school, and the discipline, togetherness and respect they experience each day. They described the Matru-Pitru Pooja held during Anand Utsav, which expresses gratitude and reverence towards parents, and they sang Matri Sthavanam."),
            ("p", "Participants from Nigeria, Dubai, Egypt, Namibia and the Philippines responded warmly to what the CIRS students shared."),
            ("h", "What it achieved"),
            ("p", "The session, linked to Grade 6 English, aimed for students to learn about other cultures and traditions and to share their own with confidence. The school records that they gained respect and empathy for family traditions different from their own, and spoke confidently on an international platform."),
        ],
    },
    {
        "slug": "shaishav-shiksha-2025",
        "title": "Shaishav Shiksha-II: five days for Foundation Years teachers",
        "section": "Community",
        "date": "1–5 December 2025",
        "datetime": "2025-12-01",
        "dek": "The CCMT Education Cell brought Foundation Years teachers to CIRS for an orientation in early childhood education.",
        "who": "Teachers, Nursery to Class II",
        "photos": [],
        "blocks": [
            ("p", "From 1 to 5 December 2025, CIRS hosted Shaishav Shiksha-II, a five-day orientation organised by the CCMT Education Cell for Foundation Years teachers of Nursery to Class II."),
            ("p", "The programme opened with flag hoisting and an inauguration by Swamini Supriyananda, followed by an overview from Smt. Shanti Krishnamurthy, Director, CCMTEC. Its sessions covered the Chinmaya Vision Programme and Early Childhood Education, the National Curriculum Framework, language development through storytelling, curriculum design, lesson planning, technology in early childhood education, and child and brain development. Experts and experienced educators led lectures, workshops and demonstration classes."),
            ("p", "Drama, dance and movement, quizzes, games, campfire sessions and group interactions ran alongside the sessions, and walks, aarti and reflection gave each day its routine."),
            ("h", "What it achieved"),
            ("p", "The programme set out to deepen teachers' understanding of early childhood education and child development, and to encourage values-based, child-centred teaching. The school records that participants left with a better grasp of child psychology and experiential learning, stronger skills in curriculum planning, lesson design and the use of technology, and approaches ready to take into their classrooms."),
        ],
    },
    # -------------------------------------------------------------- Campus
    {
        "slug": "republic-day-2026",
        "title": "The 77th Republic Day",
        "section": "Campus",
        "date": "January 2026",
        "datetime": "2026-01-26",
        "dek": "Flag hoisting, the national anthem and a march past, addresses on service and unity, and an evening of aarti and culture at Vraja.",
        "who": "The whole school",
        "photos": [
            (217, 8490, "Students in ceremonial uniform with staff at the Republic Day celebration"),
            (216, 8480, "Guests and cadets at the Republic Day flag hoisting"),
            (217, 8489, "Staff and students gathered on Republic Day"),
            (217, 8491, "The CIRS band with staff on Republic Day"),
        ],
        "blocks": [
            ("p", "CIRS celebrated the 77th Republic Day with patriotism, discipline and enthusiasm. The Principal hoisted the National Flag; the National Anthem followed, and then a march past by the students."),
            ("p", "Smt. Shanti Krishnamurthy, Director, Academics and Administration, spoke on selfless service and the importance of staying rooted in Indian cultural values while nurturing patriotism. Sri Sripal of the Department of Hindi addressed the students on responsibility and unity as the foundations of nation-building."),
            ("p", "The celebrations ended with a special evening aarti and a cultural presentation at the Vraja Auditorium."),
            ("h", "What it set out to do"),
            ("p", "The day aimed for students to understand the significance of Republic Day and the values of the Constitution, and to show responsibility and pride as citizens through their own participation. The report records a deeper sense of national pride and civic awareness, and confidence, teamwork and leadership built through taking part."),
        ],
    },
    {
        "slug": "educational-trips-2025-26",
        "title": "Learning on the road: Sidhbari, Kochi and Perur",
        "section": "Campus",
        "date": "2025–26",
        "datetime": "2026-01-20",
        "dek": "Grade VIII travelled to Sidhbari, Grade IX to Kochi, and Shishu Vatika to Perur Temple.",
        "who": "Grades VIII and IX, Shishu Vatika",
        "photos": [
            (187, 8189, "Shishu Vatika children with their teachers on the field trip to Perur Temple"),
        ],
        "blocks": [
            ("p", "The school's educational trips set out to teach India's cultural, spiritual and historical heritage through experience: to foster patriotism and respect for the nation's traditions, and to build habits of observation, interaction and reflection."),
            ("h", "Grade VIII: Sidhbari"),
            ("p", "Grade VIII travelled to Sidhbari, visiting Sidhbari Ashram, McLeod Ganj, Amritsar and Chandigarh. The tour encouraged spiritual reflection, cultural understanding and national pride."),
            ("h", "Grade IX: Kochi"),
            ("p", "Grade IX travelled to Kochi in Kerala. At the Chinmaya International Foundation, at the birthplace of Adi Shankaracharya, students learned about the life of the sage and his contribution to Hindu philosophy. At Chinmaya Vishwa Vidyapeeth, faculty members led an interactive session for them."),
            ("h", "Shishu Vatika: Perur Temple, 20 January 2026"),
            ("p", "The youngest students visited Perur Temple on a field trip. With their teachers explaining simple aspects of the temple and its significance, they observed its structure, surroundings and rituals. The school records that the children gained a first awareness of temples and cultural traditions, learned to move in groups and follow instructions, and enjoyed a joyful day of learning beyond the classroom."),
        ],
    },
    # ----------------------------------------------------------- Academics
    {
        "slug": "language-week-2025",
        "title": "Language Week: Sanskrit, Hindi, Tamil and French",
        "section": "Academics",
        "date": "13–18 October 2025",
        "datetime": "2025-10-13",
        "dek": "A Language Run, a senior quiz, a multilingual musical evening and a handwriting competition celebrated the school's languages.",
        "who": "Classes 1–12",
        "photos": [
            (253, 8778, "Students singing at the Multilingual Musical Programme during Language Week"),
            (253, 8777, "A student speaking on stage during Language Week"),
            (252, 8768, "Students writing during a Language Week activity"),
            (254, 8787, "Students arranging letter cards on the floor during Language Week"),
        ],
        "blocks": [
            ("p", "Language Week ran from 13 to 18 October 2025, opening with an address by the Head of the Department."),
            ("p", "Students took part in a Language Run representing Sanskrit, Hindi, Tamil and French. A Senior Quiz tested knowledge and critical thinking, and a Multilingual Musical Programme brought the languages together in song. The week closed with a Handwriting Competition for Classes 1 to 8, which rewarded neatness, clarity and creativity."),
            ("h", "What it set out to do"),
            ("p", "The week was designed to help students understand the richness and cultural significance of different languages, strengthen their communication skills, and find joy and unity in a shared linguistic life. The school records that it enhanced students' language and communication skills, fostered pride in and respect for linguistic diversity, and promoted teamwork through group activities."),
        ],
    },
    {
        "slug": "social-science-week-november-2025",
        "title": "Social Science Week, November 2025",
        "section": "Academics",
        "date": "3–8 November 2025",
        "datetime": "2025-11-03",
        "dek": "Quizzes, artwork, election manifestos, educational visits and awareness programmes connected the social sciences to real life.",
        "who": "Shishu Vatika to Class X",
        "photos": [
            (76, 7058, "CIRS students with their certificates on stage during Social Science Week"),
        ],
        "blocks": [
            ("p", "The Social Science Department organised Social Science Week from 3 to 8 November 2025 for students from Shishu Vatika to Class X, with academic, creative and experiential activities designed in line with the Chinmaya Vision Programme."),
            ("p", "Students took part in quizzes, artwork, logo and chart design, the preparation of election manifestos, educational visits, social awareness programmes and cultural activities."),
            ("h", "What it set out to do"),
            ("p", "The week aimed for students to understand social, cultural, environmental and democratic ideas through activity, and to develop civic responsibility, environmental awareness, patriotism and sensitivity to society. The school records that it strengthened students' critical thinking, creativity, leadership and communication, nurtured civic and environmental awareness, and gave them a practical understanding of social concepts."),
        ],
    },
    {
        "slug": "university-fair-and-careers-2025-26",
        "title": "Looking ahead: a university fair, a careers talk and MindSpark",
        "section": "Academics",
        "date": "October 2025 – March 2026",
        "datetime": "2025-10-24",
        "dek": "More than thirteen universities came to campus, a Company Secretary spoke to Class 12, and Class XI visited the MindSpark exhibition.",
        "who": "Classes 11 and 12",
        "photos": [
            (130, 7644, "CIRS students speaking with a university representative at the University Fair"),
            (129, 7637, "Class 12 students in the hall for the career guidance session"),
            (152, 7872, "CIRS students at an exhibition stall during the MindSpark visit to Karunya University"),
        ],
        "blocks": [
            ("h", "University Fair, 24 October 2025"),
            ("p", "CIRS hosted a University Fair with representatives from more than 13 universities in Australia, the UK, India and elsewhere, among them Monash University, ESSEC Business School, the University of Salford, Hult Business School, Illinois Institute of Technology, Shiv Nadar University and Alliance University. Students of Classes 11 and 12 learned about courses in engineering, business management, law, data science, medicine, the arts and entrepreneurship, and about admissions, campus life and career prospects."),
            ("p", "The fair aimed to make students aware of higher-education opportunities in India and abroad and to let them put their questions directly. The school records that students gained knowledge of courses and international trends, and confidence and clarity in making their decisions."),
            ("h", "Career guidance, 30 October 2025"),
            ("p", "Mr. M.K. Rama Krishna, a Company Secretary with more than 25 years' experience in mergers and acquisitions who works with a Dubai-based organisation, spoke to Class 12. The session was organised by the Guidance Counsellor, Mr. Koganti Dasaradhi. He explained the path to becoming a Company Secretary through the ICSI framework (CSEET, the Executive Programme and the Professional Programme, with practical training), the profession's roles in governance, legal advisory, compliance and strategy, and how CS differs from CA and CMA."),
            ("h", "MindSpark Exhibition, 28 March 2026"),
            ("p", "Students of Class XI (CBSE Science), with interested IB students, visited the MindSpark Exhibition at Karunya University. They explored stalls on robotics and automation, AI-based applications, renewable energy and engineering prototypes, spoke with presenters, and were guided through key exhibits by faculty. The school records that the visit gave students practical insight into emerging technologies and encouraged them to connect classroom learning with real-world applications."),
        ],
    },
    {
        "slug": "young-economists-2025-26",
        "title": "The Youth Economic Initiative's year",
        "section": "Academics",
        "date": "January – April 2026",
        "datetime": "2026-03-09",
        "dek": "Students explained geopolitics and the Union Budget, ran an IPL auction, and taught financial literacy to the school's support staff.",
        "who": "Grades 9–12 and IBDP",
        "photos": [
            (239, 8670, "A YEI student presenting the Union Budget to Grades 11 and 12 in the open-air amphitheatre"),
            (267, 8880, "A student at the podium during the YEI IPL Auction simulation"),
            (267, 8881, "Students bidding with paddles at the IPL Auction simulation"),
            (235, 8640, "YEI students leading a financial literacy session for the school's support staff"),
            (229, 8591, "Members of the Youth Economic Initiative together after a session"),
        ],
        "blocks": [
            ("p", "The Youth Economic Initiative (YEI) is a student club that brings economics into the life of the school. Across the term its members planned and led sessions for their peers and for the wider CIRS community."),
            ("h", "Petrodollar: geopolitics and global impact, 10 January 2026"),
            ("p", "For senior school students, the YEI team explained geopolitics through the case of Venezuela: the importance of oil reserves, how global powers act on economic and strategic interests, and how such events move oil prices and economies worldwide, India's included. The report records that students came away with a clearer grasp of international relations and of a world in which events in one region affect all others."),
            ("h", "The Union Budget, 9 March 2026"),
            ("p", "Four YEI students presented the Government of India's 2026 budget to Grades 11 and 12: the types of expenditure, capital allocation, how a budget is formed, and the allocation of funds across ministries. They highlighted the development of tier-3 cities and the textile sector, and discussed why markets move after a budget, the orange economy, the effect on the middle-income group, semiconductor independence and India's AI mission, before taking questions."),
            ("h", "IPL Auction simulation, 28 March 2026"),
            ("p", "An inter-house IPL Auction for Grades 9 to 12 ran for five hours. Teams received the rules and player information in advance and planned their budgets, then bid, selected players and made decisions under pressure. The aim was a practical understanding of budgeting, financing and opportunity cost; the report records gains in analytical and strategic thinking, emotional control and teamwork."),
            ("h", "Financial literacy for support staff, 8 April 2026"),
            ("p", "YEI students planned and conducted a financial literacy session for around 50 members of the school's support staff (Sodexo employees), in two venues and two languages, under the guidance of the coordinator, Smt. Rashmi. It covered planning expenses, saving, basic investment, financial scams and government schemes, with time for questions."),
            ("h", "Adding value to a product, 11 April 2026"),
            ("p", "In Business Management, IBDP Year 1 students worked in teams of two or three to add value to a simple product, a potato or an egg, through human resources, finance, marketing or operations, and presented their strategies to the class."),
        ],
    },
    # -------------------------------------------------------- Achievements
    {
        "slug": "quiz-club-2025-26",
        "title": "The Quiz Club's season: from Coimbatore to the QuBiz grand finals",
        "section": "Achievements",
        "date": "November 2025 – February 2026",
        "datetime": "2026-01-21",
        "lead": True,
        "dek": "CIRS quizzers won the QuBiz Coimbatore regional, finished second in its grand finals, and won Quiz Track at PSG.",
        "who": "The CIRS Quiz Club",
        "photos": [
            (142, 7766, "CIRS quizzers with the organisers on the QuBiz stage at Shiv Nadar University Chennai"),
            (144, 7786, "CIRS quizzers on stage at Quiz Track at PSG College"),
            (133, 7671, "CIRS students with their certificates at the Prashna quiz"),
            (135, 7683, "CIRS quizzers receiving their certificates at the InFact quiz at CIT"),
        ],
        "blocks": [
            ("p", "The Quiz Club competed across the region between November 2025 and February 2026, and placed in each of the five quizzes the report records."),
            ("h", "InFact at CIT, 13 November 2025"),
            ("p", "At the inter-school quiz at CIT, with around 600 students taking part, Devansh Mazumdar and Pradyuth Senthilkumar finished second and won a trophy. Ishan Madhusudan and Vrishank Mehta reached the semi-finals."),
            ("h", "Kelvi Kalam at KPR College, November 2025"),
            ("p", "Among 476 teams from 51 schools, Adithyan Diwakar and Heril Goti finished third, winning ₹6,000 and the offer of a free-tuition scholarship at KPR College. Divyam Gupta and Viraj Lal finished seventh."),
            ("h", "Prashna at Amrita Vidyapeetham, 27 November 2025"),
            ("p", "In a field of more than 30 teams of two, Devansh Mazumdar and Pradyuth Senthilkumar finished third, winning ₹500."),
            ("h", "QuBiz, Shiv Nadar University Chennai, 21 January 2026"),
            ("p", "The fourth season of QuBiz ran across 19 cities with more than 200 schools and 2,500 participants. Heril Goti and Adithyan D.V. won the Coimbatore regional round against more than 100 teams (₹10,000), topped the Chennai semi-finals, and finished second in the Grand Finals, winning a further ₹10,000."),
            ("h", "Quiz Track at PSG College, 22 February 2026"),
            ("p", "Sixty-four teams competed for eight places in the final. Devansh Mazumdar and Pradyuth Senthilkumar won, taking a trophy and ₹3,000. Arnav Anand and Govardhan, and Hridit and Rudransh, won audience prizes."),
        ],
    },
    {
        "slug": "science-competitions-2025-26",
        "title": "Science and innovation: first places, a national qualification and an overall championship",
        "section": "Achievements",
        "date": "October – December 2025",
        "datetime": "2025-10-29",
        "dek": "First place among 1,374 participants at KSR Innofest, a place in the CBSE nationals, and the Overall Championship at T'XOTICA & GENOMIA.",
        "who": "Grades 6–12",
        "photos": [
            (160, 7929, "A CIRS student receiving the award at the CBSE Regional Science Exhibition"),
            (146, 7803, "CIRS students with their prize cheque at KSR Innofest"),
            (154, 7886, "CIRS students on stage at the Park Young Innovators Summit"),
            (107, 7386, "CIRS students with their certificates at the Science Quiz and Expo"),
            (158, 7915, "Two CIRS students with their certificates at T'XOTICA & GENOMIA"),
            (166, 7995, "CIRS students on stage at Zestro at Karunya"),
        ],
        "blocks": [
            ("p", "CIRS students competed in science, technology and innovation events across Tamil Nadu this term, and several results stand out."),
            ("h", "KSR Innofest, 25 October 2025"),
            ("p", "At KSR Innofest, where the guest was Dr. Mayilsamy Annadurai, the CIRS team won first place in the Science Exhibition among 1,374 participants, with a prize of ₹30,000. The school also finished second in Group Singing (₹5,000)."),
            ("h", "Science Quiz and Expo, 29 October 2025"),
            ("p", "At the Science Quiz and Expo (Thulir) at Hindusthan College of Arts & Science, held with the School Education Department and the Tamil Nadu Science Forum and attended by more than 4,000 students, CIRS won first place in every category, each with ₹3,000: Devanshi Drolia, Arnav Anand and Pranav Patel (Classes VI–VIII); Vishv Prem Nangia, Aaditya Tulsyan and Ritika Deorah (IX–X); and Ommireddy Nishanth Reddy, Thashwin Sai V and Arnav Saraf (XI–XII)."),
            ("h", "Park Young Innovators Summit, 30 October 2025"),
            ("p", "Among more than 650 exhibits and 241 ideathon projects, CIRS won first place in the AI for Humanity category, receiving the award from Padma Bhushan Nambi Narayanan."),
            ("h", "T'XOTICA & GENOMIA, 28 November 2025"),
            ("p", "At PSBB Millennium School, CIRS was named Overall Champion. In Robotic Rumble, Garvit Sukhani and Gauraang Agarwal (Grade 9) won first place and Vishnu Jalan and Pranav Patel (Grade 8) second. In BIOWIZ, Divyam Gupta and Gelivi Swarit Skanda Krishna (Grade 10) were runners-up, and Grade 11 students also won places in CINEMATECH."),
            ("h", "CBSE Regional Science Exhibition, 29 November 2025"),
            ("p", "At Om Sadhana Central School, Madurai, team ARRM MOTION, R Kanishk (Class 10) and Raunak Nitin Golchha (Grade 11), won first place and qualified for the national level."),
            ("h", "National Space Quiz, 16 December 2025"),
            ("p", "At the National Space Quiz held at Sri Shakthi Institute, Akshat Chirania (Grade 12) placed among the top 100 nationwide and was selected to visit a space centre and witness a launch."),
            ("h", "Zestro, 26 February 2026"),
            ("p", "At Zestro at Karunya, a Grade 8 student won first place in TechTalk, and a CIRS team also placed in the Technology Quiz."),
        ],
    },
    {
        "slug": "robotics-and-maths-2025-26",
        "title": "Robotics projects and the Sankhya Vijnana Olympiad",
        "section": "Achievements",
        "date": "October 2025 – March 2026",
        "datetime": "2026-01-31",
        "dek": "Working models at Veetuku Oru Vignani, the Universal Robo League and Innochamp, and the Chinmaya Sankhya Vijnana Olympiad.",
        "who": "Middle and senior school",
        "photos": [
            (169, 8017, "CIRS students receiving their award on stage at the Universal Robo League Project Expo"),
            (171, 8038, "CIRS students with their certificates at Veetuku Oru Vignani"),
            (149, 7822, "CIRS students with their certificates at Innochamp"),
        ],
        "blocks": [
            ("p", "CIRS's young engineers took their working models to three exhibitions this term."),
            ("h", "Veetuku Oru Vignani, 24 October 2025"),
            ("p", "At Puthiya Thalaimurai's Veetuku Oru Vignani, which drew more than 550 projects, Preetham, Gaurang and Jasith presented a working model."),
            ("h", "Universal Robo League Project Expo, 31 January 2026"),
            ("p", "At the expo organised by Robomatic at Hindusthan International School, with more than 300 models, team AARM (Preetham, Gaurang and Arnav Nair) presented their project, mentored by Sri Arunesh and Smt. Meera Narayani."),
            ("h", "Innochamp, 29 March 2026"),
            ("p", "At Innochamp at Sri Shakthi Institute, with more than 100 schools taking part, Kanishk, Preetham, Gaurang and Garvit represented CIRS."),
            ("h", "Chinmaya Sankhya Vijnana Olympiad, 19 and 21 January 2026"),
            ("p", "CIRS students also sat the Chinmaya Sankhya Vijnana Olympiad in Mathematics and Science, conducted by the CCMT Education Cell."),
        ],
    },
    {
        "slug": "gita-chanting-2025-26",
        "title": "Gita chanting: a district podium and a state trophy",
        "section": "Achievements",
        "date": "November 2025 – February 2026",
        "datetime": "2026-02-08",
        "dek": "Four CIRS students placed at the district Gita chanting competition, and Jai Nethra Shree won the state Tamil Bhagavad Gita chanting final.",
        "who": "Grades 6–12",
        "photos": [
            (185, 8166, "Students on stage at the Tamil Bhagavad Gita Chanting competition"),
            (177, 8088, "A student chanting before a judge at the district-level Gita chanting competition"),
            (177, 8089, "Students waiting their turn at the district-level Gita chanting competition"),
        ],
        "blocks": [
            ("h", "District level, 2 November 2025"),
            ("p", "At the district-level Gita chanting competition, Naren Chandra Jagarlamudi (Grade 6) won second place in Group D. In Category F, Rohith Chowdary Bellam (Grade 12 Science) won first place, Khushi Amitabh Desai second, and Munaga Srivathsa Cheran Tej (Grade 11 IBDP) third."),
            ("h", "Tamil Bhagavad Gita Chanting, final on 8 February 2026"),
            ("p", "The state-level Tamil Bhagavad Gita Chanting competition conducted by Chennai Chinmaya Mission runs over three rounds and draws around 22,000 students. Sixty-three CIRS students took part in the first round; Prathyun and Jai Nethra Shree went through to the district round; and in the final on 8 February 2026, Jai Nethra Shree won the trophy, a shield and a certificate, together with a trip to the Himalayas by way of Kurukshetra with her family."),
        ],
    },
    {
        "slug": "french-and-talent-2025",
        "title": "A French Overall Championship, and a talent award",
        "section": "Achievements",
        "date": "25 October – 15 November 2025",
        "datetime": "2025-10-25",
        "dek": "CIRS won the Overall Championship Trophy at a multi-event French competition; Naitik Nemish Mehta won an award at the Eftapei Talent Fest.",
        "who": "Grades 7–10",
        "photos": [
            (162, 7957, "Naitik Nemish Mehta with his award from the Eftapei Talent Fest"),
        ],
        "blocks": [
            ("h", "French competition, 25 October 2025"),
            ("p", "CIRS students won the Overall Championship Trophy at a multi-event French competition. In Just a Minute, Rhea Sontakke (Grade 10) won second place. In Painting, S. Ritesh (Grade 8) won first place, and Samrithie Vijayamohan, M. Shruthi and Shrika Dandamudi (Grade 10) second. In Singing, Shaunak Kolipaka, S. Jithesh Shankar and Rishi (Grade 10) won first place, and Saptarshi Pal (Grade 8) third."),
            ("p", "The competition was meant to build proficiency in the language alongside artistic expression and cultural appreciation. The school records that it strengthened students' communication and performance skills and their appreciation of language learning in a multicultural setting."),
            ("h", "Eftapei Talent Fest, 15 November 2025"),
            ("p", "At the Eftapei Talent Fest, in which more than 100 schools took part, Naitik Nemish Mehta (Grade 7) was an Award Winner."),
        ],
    },
    # -------------------------------------------------------------- Sports
    {
        "slug": "sahodaya-swimming-2025",
        "title": "Nineteen swimmers at the Coimbatore Sahodaya girls' meet",
        "section": "Sports",
        "date": "22 November 2025",
        "datetime": "2025-11-22",
        "dek": "CIRS sent 19 girls across four age groups to the 46th Coimbatore Sahodaya Inter-School Girls' Swimming Competition.",
        "who": "Girls, U12 to U19",
        "photos": [
            (24, 6564, "CIRS girls' swimming team with their certificates at the 46th Coimbatore Sahodaya meet"),
        ],
        "blocks": [
            ("p", "On 22 November 2025, 19 CIRS girls competed at the 46th Coimbatore Sahodaya Inter-School Girls' Swimming Competition for 2025–26, held at SSVM World School, in the Under-12, Under-14, Under-17 and Under-19 age groups."),
            ("p", "The team returned with several prizes."),
        ],
    },
    # ------------------------------------------------------ In the classroom
    {
        "slug": "classroom-languages-2025-26",
        "title": "In the classroom: languages",
        "section": "Academics",
        "date": "October 2025 – March 2026",
        "datetime": "2026-02-10",
        "dek": "Kites that carry poems, a hockey commentary in Hindi, word wheels in Tamil and job-offer posters in French: how the language departments teach.",
        "who": "Grades 1–12",
        "photos": [
            (93, 7207, "Grade 10 students in a role play of The Triumph of Surgery"),
            (60, 6916, "Grade 6 students holding up the kites they made for their cinquain poems"),
            (17, 6520, "A Grade 7 eco-craft model of an island made from natural materials"),
            (29, 6610, "Grade 6 students performing a hockey commentary in a Hindi lesson"),
            (71, 7017, "Grade 10 students matching Samas and Vigraha word cards on the classroom floor"),
            (64, 6964, "A Class 1 student using a Tamil language wheel"),
            (244, 8716, "Two Class 10 students presenting their French job-offer poster"),
            (57, 6893, "A Grade 3 student with an art-integrated project on Uncle Owl"),
        ],
        "blocks": [
            ("p", "The CVP report records not only the events of the term but also how lessons are taught. In every language taught at CIRS, teachers asked students to do something with the language: act it, build it, sing it or argue it."),
            ("h", "English"),
            ("p", "Grade 6 wrote cinquain poems on kites they made (20 November 2025) and learned prepositions through a human-prepositions activity (6 November). Grade 3 met Uncle Owl through an art-integrated lesson (12 November); Grade 5 made moral posters from A Wise Parrot (9 January 2026) and T-charts on the decision of the Panchayat (18 February). Grade 7 made eco-crafts (10 February), Grade 8 held a group discussion on books and their films (11 February), and Grade 10 acted out The Triumph of Surgery (21 March). For the lesson Yoga – A Way of Life, Grade 6 practised yoga together in the indoor hall, holding Vrikshasana in unison."),
            ("h", "Hindi and Sanskrit"),
            ("p", "Grade 9 staged a skit of Atithi Tum Kab Jaoge (12 October 2025) and Grade 5 a skit of Sundariya (21 October). For the lesson Pariksha, Grade 6 performed a hockey commentary (17 November), and Grade 8 set Mat Baandho to tunes in five groups (21 November). Grade 10 matched Samas and Vigraha on the classroom floor (10 January 2026), IB Year 1 debated 33 per cent reservation for women (12 January), and Grade 2 played a word-recall game in teams named Ram, Hanuman and Lakshman (21 February). In Sanskrit, Grade 5 built words from letter cards (17 November 2025)."),
            ("h", "Tamil and French"),
            ("p", "In Tamil, Class 1 learned with a language wheel (22 October 2025) and colours (10 November), Class 2 practised opposites (16 January 2026), and Class 5 matched poems with their authors (9 January). In French, Class 10 designed job-offer posters for the lesson Chercher du travail (10 September 2025)."),
        ],
    },
    {
        "slug": "classroom-sciences-2025-26",
        "title": "In the classroom: science, mathematics and social science",
        "section": "Academics",
        "date": "October 2025 – March 2026",
        "datetime": "2026-03-03",
        "dek": "A pink hand against corruption, a pendulum in five groups, dustbins from waste and a Google Doodle for the forests: learning by doing.",
        "who": "Grades 4–12",
        "photos": [
            (88, 7166, "The chemistry laboratory during the Grade 10 Pink Hand experiment"),
            (82, 7123, "Grade 10 students studying transpiration with a potted plant"),
            (120, 7544, "Grade 7 students measuring the period of a simple pendulum"),
            (98, 7322, "Grade 10 students watching a candle's reflection in a mirrors experiment"),
            (123, 7565, "Grade 9 students measuring work and energy on the school ground"),
            (74, 7039, "Grade 5 students making dustbins from waste materials"),
            (95, 7233, "Grade 8 students drawing exponent doodles in class"),
            (27, 6589, "A Grade 8 Google Doodle drawing on the theme of forests and wildlife"),
        ],
        "blocks": [
            ("p", "Across the sciences, mathematics and social science, lessons this term asked students to test ideas with their hands and to connect them to the world outside the classroom."),
            ("h", "Science"),
            ("p", "Grade 10 used phenolphthalein for a Pink Hand demonstration against corruption (3 March 2026), studied transpiration in plants (20 November 2025) and investigated mirrors (23 March 2026). Grade 12 chemistry checked the purity of substances and linked the chemistry to the breathalyser (3 March). Grade 9 measured work, energy and power on the school ground (12 November 2025) and visited the sound recording room in a lesson on sound. Grade 7 found the period of a simple pendulum in five groups of five (13 January 2026). Grade 6 created constellations, among them Orion, Gemini, Libra and Canis Major (12 March). Grade 4 tested water pressure, reacted vinegar with baking soda and put out a candle with carbon dioxide (7 January). In EVS, Grade 5 made dustbins from waste for use in classrooms and dormitories (24 January)."),
            ("h", "Mathematics"),
            ("p", "Grade 8 drew exponent doodles (13 February 2026) and joined the dots on exponents (24 March), and Grade 10 explored the ratios behind pairs of linear equations (13 February)."),
            ("h", "Social science"),
            ("p", "Grade 9 drafted election manifestos (13 September 2025) and debated democracy (20 November). Grade 8 designed Google Doodles on forests and wildlife (18 November) and studied the Preamble (11 January 2026)."),
        ],
    },
]

# The contributors the report itself credits, printed under the term.
CREDITS = ("The CVP report was prepared under the Principal, Smt. Rajeshwari, "
           "with guidance and review from the Headmaster, Sri Ganesh Eswaran. "
           "Editorial: Smt. Supriya KP and Smt. Revathy P. Consolidation: "
           "Smt. Soumya and Sri Nagarajan. IT: Sri Krishnakumar S.")


def photo_path(slug, n, width=None):
    suffix = f"-{width}" if width else ""
    return f"{IMG_DIR}/{slug}-{n}{suffix}.webp"


def webp_size(path):
    """Width and height from a WebP header, so the build needs no imaging library."""
    with open(os.path.join(ROOT, path), "rb") as f:
        head = f.read(30)
    kind = head[12:16]
    if kind == b"VP8 ":
        w, h = struct.unpack("<HH", head[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L":
        b = head[21:25]
        w = 1 + (((b[1] & 0x3F) << 8) | b[0])
        h = 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
        return w, h
    if kind == b"VP8X":
        w = 1 + int.from_bytes(head[24:27], "little")
        h = 1 + int.from_bytes(head[27:30], "little")
        return w, h
    raise ValueError(f"not a WebP: {path}")


def _prepare():
    """Give each article the fields news_article_html reads."""
    for art in ARTICLES:
        art["report"] = "From the term's CVP report"
        art["paragraphs"] = []
        figs = []
        for n, (_page, _xref, alt) in enumerate(art["photos"], 1):
            src = photo_path(art["slug"], n)
            w, h = webp_size(src)
            figs.append({"src": src, "alt": alt, "w": w, "h": h})
        if figs:
            art["image"], art["image_alt"] = figs[0]["src"], figs[0]["alt"]
            art["image_size"] = (figs[0]["w"], figs[0]["h"])
            art["figures"] = figs[1:]
        else:
            art["image"] = ""
            art["figures"] = []


_prepare()


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _thumb(art, sizes):
    if not art["image"]:
        return ""
    w, h = art["image_size"]
    small = photo_path(art["slug"], 1, 720)
    srcset = f'{small} 720w, {art["image"]} {w}w' if os.path.exists(os.path.join(ROOT, small)) else f'{art["image"]} {w}w'
    return (f'<img src="{art["image"]}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(art["image_alt"])}" loading="lazy" decoding="async">')


def _meta(art):
    return (f'<p class="journal-meta"><span>{esc(art["section"])}</span>'
            f'<span><time datetime="{art["datetime"]}">{esc(art["date"])}</time></span></p>')


SECTIONS = ["Achievements", "Arts", "Community", "Academics", "Campus", "Sports"]


def term_html():
    """The term's section on the News page: three leads, then every report by category."""
    leads = [a for a in ARTICLES if a.get("lead")]
    out = ['<section class="journal-term" id="term" aria-labelledby="term-title">',
           '  <div class="journal-wrap">',
           '    <div class="journal-section-head">',
           f'      <p class="journal-section-head__label">{esc(TERM)}</p>',
           '      <h2 id="term-title">The term in review</h2>',
           f'      <p>{len(ARTICLES)} reports written from the school&rsquo;s Chinmaya Vision Programme report for the term: '
           'what happened, what each event set out to do, and what the school records it achieved.</p>',
           '    </div>',
           '    <div class="journal-new-reports journal-term__leads">']
    for i, a in enumerate(leads):
        lead = " journal-new-report--lead" if i == 0 else ""
        sizes = "(max-width: 760px) 100vw, 56vw" if i == 0 else "(max-width: 760px) 100vw, 36vw"
        out += [f'      <article class="journal-new-report{lead}">',
                f'        <a href="{a["slug"]}.html">',
                f'          <div class="journal-new-report__image">{_thumb(a, sizes)}</div>',
                f'          <div class="journal-new-report__copy">{_meta(a)}<h3>{esc(a["title"])}</h3>'
                f'<p>{esc(a["dek"])}</p><span class="journal-read">Read story</span></div>',
                '        </a>',
                '      </article>']
    out.append('    </div>')
    for sec in SECTIONS:
        arts = [a for a in ARTICLES if a["section"] == sec and not a.get("lead")]
        if not arts:
            continue
        sid = f"term-{sec.lower()}"
        out += [f'    <div class="journal-term__group" aria-labelledby="{sid}">',
                f'      <h3 class="journal-term__label" id="{sid}">{esc(sec)}</h3>',
                '      <ul class="journal-term__grid">']
        for a in arts:
            img = (f'<div class="journal-term__image">{_thumb(a, "(max-width: 760px) 100vw, 30vw")}</div>'
                   if a["image"] else "")
            plain = "" if a["image"] else " journal-term__card--plain"
            out += [f'        <li class="journal-term__card{plain}"><a href="{a["slug"]}.html">{img}'
                    f'<div class="journal-term__copy">{_meta(a)}<h4>{esc(a["title"])}</h4>'
                    f'<p>{esc(a["dek"])}</p></div></a></li>']
        out += ['      </ul>', '    </div>']
    out += [f'    <p class="journal-term__credit">{esc(CREDITS)}</p>',
            '  </div>',
            '</section>']
    return "\n".join(out)


def _short(datetime):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    y, m = datetime.split("-")[:2]
    return f"{months[int(m) - 1]} {y}"


def archive_html():
    """One archive row per report, newest first, in the News archive's own format."""
    rows = []
    for a in sorted(ARTICLES, key=lambda a: a["datetime"], reverse=True):
        words = " ".join([a["title"], a["dek"], a["who"]]).lower()
        words = "".join(c if c.isalnum() or c == " " else " " for c in words)
        words = " ".join(words.split())
        rows.append(f'        <li data-journal-category="{a["section"]}" data-journal-search="{esc(words)}">'
                    f'<a href="{a["slug"]}.html"><time datetime="{a["datetime"]}">{esc(a["date"])}</time>'
                    f'<span>{esc(a["title"])}</span><small>{esc(a["section"])}</small></a></li>')
    return "\n".join(rows)


if __name__ == "__main__":
    for a in ARTICLES:
        print(f'{a["datetime"]}  {a["section"]:<12} {a["slug"]:<40} {len(a["photos"])} photos')
    print(len(ARTICLES), "articles")
