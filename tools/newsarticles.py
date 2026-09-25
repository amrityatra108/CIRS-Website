#!/usr/bin/env python3
"""The news reports the school published on its own earlier sites.

The News page used to link eleven stories straight out to cirschool.org and
new.cirschool.org. Those links left the site, and the older of the two is a
gallery template whose images are already going missing. The reports are
recorded here instead, and build-site.py gives each one a page.

Every word in "paragraphs" is the school's own, taken from the page it was
published on and reproduced whole. Nothing is summarised and nothing is
added. Where the school's own report is odd, it is left odd: the update
titled "Solo Instrument" describes a dance competition, and that is how it
was published.

The News page keeps its own shorter write-ups in the "Read report on this
page" panels. Those are the site's abridgements and are not the same text;
these pages are the full reports behind them.

Two of the eleven are galleries rather than articles, so they carry
photographs and no prose. Their images were fetched down into
assets/source/news-archive/ and are cut by tools/make-news-archive.py.
Seven of the Vishu set were already gone from the school's server.

    slug          the page it becomes, <slug>.html
    source        where it was published, kept for provenance
    paragraphs    the report, whole
    gallery       a folder under assets/img/news-archive/, for the two that have one
"""

ARTICLES = [
    {
        "slug": "science-expo",
        "title": "Science Expo",
        "section": "Academics",
        "date": "25 July 2025",
        "datetime": "2025-07-25",
        "dek": "",
        "image": "assets/img/news/science-expo-1200.webp",
        "image_alt": "CIRS student explaining a science exhibit to a visitor at the Science Expo",
        "source": "https://new.cirschool.org/science-expo/",
        "paragraphs": [
            "As part of Science Week, the Department of Sciences hosted its Science Expo on July 25th, turning the campus into a center of exploration and innovation. With over 140 activities and models across Biology, Physics, Chemistry, and Environmental Science, the Expo drew great enthusiasm from students. Presentations ranged from life processes and principles of motion to chemical reactions and sustainability concepts, brought to life through interactive models, charts, digital displays, and experiments. The event also welcomed around 50 schools from in and around Coimbatore, making it a vibrant academic gathering. The Expo not only celebrated scientific curiosity but also fostered collaboration, communication, and hands-on learning, leaving participants inspired by the wonders of science.",
        ],
    },
    {
        "slug": "english-week",
        "title": "English Week",
        "section": "Arts",
        "date": "4–9 August 2025",
        "datetime": "2025-08-04",
        "dek": "Storytelling, poetry recitation, Spell Bee, quizzes and classroom activities gave students many ways to use and enjoy English.",
        "image": "assets/img/news/english-week-1200.webp",
        "image_alt": "A CIRS student speaking during an English Week activity while classmates listen",
        "source": "https://new.cirschool.org/english-week/",
        "paragraphs": [
            "The English Week Celebration, held from August 4th to August 9th, 2025, filled the portals of CIRS with creativity, confidence, and the joy of learning English. The array of competitions included Storytelling, Handwriting, Poetry Recitation, Spell Bee, Quiz and HAM.",
            "To make the celebration more meaningful, teachers seamlessly integrated language enrichment activities into their regular English classes throughout the week, ensuring every student had an opportunity to engage, express, and excel. English Week 2025 is truly a testament to CIRS’ dedication to empowering students with effective communication skills and a lasting passion for literature and language.",
        ],
    },
    {
        "slug": "mathematics-week-2025",
        "title": "Mathematics Week 2025",
        "section": "Academics",
        "date": "7–11 July 2025",
        "datetime": "2025-07-07",
        "dek": "Students took on the Maths Run and a senior quiz; Shishuvatika children explored mathematics through traditional Indian games.",
        "image": "assets/img/news/mathematics-week-1200.webp",
        "image_alt": "CIRS students working together on a tabletop mathematics challenge",
        "source": "https://new.cirschool.org/mathematics-week-2025/",
        "paragraphs": [
            "CIRS celebrated Mathematics Week 2025 from 7th to 11th July with activities designed to nurture curiosity and joy in learning. Middle school students participated in the Maths Run, solving challenges at eight interactive stations, while senior students showcased their skills in a quiz that tested critical thinking, riddles, error-spotting, and rapid recall. Children in Shishuvatika explored mathematics through traditional Indian games, enjoying the process of learning through play.",
            "In the evening, 160 senior students competed in the house-wise Maths Run, demonstrating teamwork and problem-solving abilities. The celebrations, aligned with the Chinmaya Vision Program, strengthened logical reasoning. The week ended with students feeling inspired and curious about Mathematics.",
        ],
    },
    {
        "slug": "competitions",
        "title": "Competitions across CIRS",
        "section": "Achievements / Sports",
        "date": "1 October 2025",
        "datetime": "2025-10-01",
        "dek": "The school's roundup records results in quizzes, dance, instrumental music, football, yoga and basketball.",
        "image": "assets/img/news/competitions-1200.webp",
        "image_alt": "Collage of CIRS student award presentations and sports teams",
        "source": "https://new.cirschool.org/competitions/",
        "paragraphs": [
            "Our Junior Team from the Quiz Club — Devansh Mazumdar from grade 8 and Arnav Anand from grade 7— brought laurels to our school by securing third place at the prestigious AQMEN Quiz held on 5th August 2025 at PSBB Millennium School, Coimbatore. Conducted by the esteemed Prof. Rangarajan, the quiz challenged participants with a wide range of various topics. Competing against 55 teams from schools across Coimbatore, our talented duo stood out with their knowledge and quick thinking. They were awarded certificates of achievement along with a cash prize of ₹1,000.",
            "On 22nd August 2025, five teams from our school participated in The Hindu In School Quiz, held at NGP College, Coimbatore. Among 2000 teams, our juniors and seniors excelled with zeal. In the junior category, Devansh and Pradyuth secured 2nd place, winning ₹4,000, trophies, and certificates. Teams Govardhan-Hridit and Arnav-Jashit earned recognition from both the audience and quizmaster for their commendable efforts. In the senior category, Vishv Prem & Swarit placed 3rd, while champions Adithyan and Heril secured 1st, receiving certificates, medals, trophies and cash prizes of ₹3,000 and ₹5,000, respectively. Viraj and Divyam earned special recognition for their exceptional performance.",
            "On 20th August 2025, the CIRS Quiz Team, comprising Devansh Mazumdar and Pradyuth Senthilkumar, brought laurels to the school by clinching the First Prize at the prestigious Lotus Quiz hosted by Satchidananda Jothi Niketan International School, Mettupalayam. Amongst 40 teams, our champions showcased outstanding brilliance and intellectual sharpness, emerging victorious. They were honoured with certificates, trophies, and a cash prize of ₹5,000, marking a proud and memorable achievement and, once again, placing CIRS on the victory pedestal!",
            "On 29th August 2025, two teams from our school participated in the Zonal Quiz – QUZBIZ, conducted at Yuva Bharati School, Coimbatore. Out of 180 teams, Adithyan Diwakar and Heril Goti advanced to the finals and showcased exceptional brilliance, ultimately emerging as the winners. They were awarded certificates and a cash prize of ₹10,000. Their remarkable lead throughout the contest impressed the quizmaster and secured them a place in the State-level Quiz in Chennai. This proud victory stands as a milestone for CIRS.",
            "On 16th August 2025, our school participated in the Interschool Sahodaya Dance Competition conducted by Benglen Public School. We took part in three categories – the Under-14 Girls Group, Under-19 Boys Group, and Under-19 Girls Group. Among the 25 participating schools, our Under-19 Girls Team proudly secured the 3rd position; yet another proud achievement and laurel for CIRS!",
            "On August 26, 2025, the 46th Sahodaya Inter School Instrumental Music Competition was held at CS ACADEMY School, Coimbatore. 13 students represented our school across 4 categories: Wind, Rhythm, Keyboard and Band. With 41 schools participating, it is our pleasure to announce that Yuvraj Tibrewal of Class 9 secured the 1st position in the Wind category and Arham Jain of Class 9 secured the 2nd position in the Rhythm category. The band and keyboard students also gave an astounding performance in the competition.",
            "On the 26th of July 2025, 10 of our students – ranging from 7th to 12th grade – took part in the Interschool Bhajan Competition held at Suguna International School. It brings us immense joy to announce that among over 20 schools, our students secured the 1st prize. Overall, it was a captivating performance they put up and is surely an occasion of great pride.",
            "Aksharam International School organised the 46th CBSE Sahodaya Inter-school Storytelling competition.",
            "In the category C, Anokhi Kankani of 8th grade won the fourth place, and in the category D, Aashi Kedia of 10th grade won the second place.",
            "Amayra Goel of 8th grade bagged second place in category B in the English Extempore Competition held at CMC International School, Coimbatore.",
            "In the public speaking competition hosted by Vidhya Niketan School (CBSE), Vilanankurichi, Coimbatore, 23 August 2025",
            "Pradyum Tibarewal of grade 12 secured the first place.",
            "46th CBSE Sahodaya English Spell Bee Competition",
            "In the English Spell Bee competition held at Anugraha Mandhir CBSE Senior Secondary School, Coimbatore, the following students brought laurels to the school:",
            "The United Public School, Periyanaickenpalayam, Coimbatore organised English Declamation Competition on 9 August 2025. The following students emerged as winners:",
            "Saptarshi Pal of grade 8 – Second PlaceAdhyatma Ghranthik Agarwal of grade 10– Third PlacePradyum Tibarewal of grade 12 – Second Place",
            "The CIRS Under-14 Boys team emerged as the champions at the 11-on-11 Football Tournament hosted by Chandrakanthi Public School, Coimbatore, where 36 schools participated.",
            "A special congratulations to Tanay Lakshman (Grade 8) for winning the Best Player Award!",
            "CIRS participated in the South Zone Yoga Competition 2025–26, organized by the School Games Sport Development Foundation India at Erode on 13th July 2025.",
            "With remarkable performances across all categories, our students brought home a tally of 6 gold, 5 silver, and 6 bronze medals, securing the Overall Championship.",
            "Our Under-19 Boys and Under-19 Girls Basketball Teams proudly represented CIRS at the KPR Basketball Tournament 2025, hosted by KPR Engineering College, Coimbatore, on 9th & 10th August 2025.",
            "With 20 teams from 4 districts competing, both our under-19 boys’ and girls’ teams secured the 3rd place.",
            "Our Under-16 Girls Basketball Team represented CIRS at the Coimbatore Sahodaya Basketball Tournament 2025, hosted by SNS CBSE School, Coimbatore, on 24th & 25th July 2025.",
            "With 22 teams competing in the category, our Under-16 Girls secured the position of Runners-Up. Their achievement stands as a proud moment for the school.",
            "CIRS participated in the Takshila Inter-School 7-on-7 Football Tournament, held on 28th & 29th August 2025 at Delhi Public School, Coimbatore.",
            "Our Under-11 Boys Team secured the Second Runner-Up position. Adding to this success, Arnav Ramoliya (Grade 5) was honoured with the Best Defender Award.",
        ],
    },
    {
        "slug": "social-science-week",
        "title": "Social Science Week",
        "section": "Academics",
        "date": "3 October 2025",
        "datetime": "2025-10-03",
        "dek": "A Social Run, treasure hunt, election manifestos, field trip, quizzes and harvest festival activities brought social science beyond the classroom.",
        "image": "assets/img/news/social-science-week-1200.webp",
        "image_alt": "CIRS students and teachers holding certificates on a stage",
        "source": "https://new.cirschool.org/social-science-week/",
        "paragraphs": [
            "The Social Science Week was celebrated with great enthusiasm, engaging students across all grades in a variety of creative and thought-provoking activities. Students showcased their creativity through the Making of Google Doodle on the theme “Pongal Celebration”. An exciting Social Run and treasure hunt activity was organized to enhance teamwork and knowledge. Students designed Non-conventional Symbols, reflecting their innovative ideas. Learners went on an enriching Field Trip to gain real-world exposure. Further students prepared Election Manifestos, encouraging awareness of democratic values. For Junior school, an engaging Social Science Quiz tested their knowledge and sharpened their skills. Additionally, students explored the Significance of Harvest Festivals through discussions and presentations. The week offered a blend of learning, creativity, and experiential activities, making Social Science both exciting and meaningful for all.",
        ],
    },
    {
        "slug": "chinmaya-vraja",
        "title": "Chinmaya Vraja",
        "section": "Campus",
        "date": "2 October 2025",
        "datetime": "2025-10-02",
        "dek": "A puja marked the opening of the school's new multipurpose hall, named Chinmaya Vraja.",
        "image": "assets/img/news/chinmaya-vraja-1200.webp",
        "image_alt": "CIRS community gathered for a puja in the Chinmaya Vraja hall",
        "source": "https://new.cirschool.org/chinmaya-vraja/",
        "paragraphs": [
            "During the early hours of 6th September, a ceremonial puja was conducted at the new multipurpose hall, marking the start of its functioning. A Havan was conducted, and the holy water was sprinkled in the hall. Swami Swaroopananda, the global Head, Chinmaya Mission and Chairman, CIRS, has named the hall “CHINMAYA VRAJA.” The Vrajabhumi is known as the land where Krishna played with the Gopis, herded cows, and the place also stands for the sacred experience of Sri Krishna growing up. So too, this auditorium will witness children of CIRS grow up, having various experiences and enriching their lives with them. We are confident they will grow into wonderful men and women, strong to face the challenges of the world and establish righteousness, just as Sri Krishna did.",
        ],
    },
    {
        "slug": "cirs-general-election",
        "title": "A classroom becomes a constituency",
        "section": "Campus",
        "date": "25 April 2025",
        "datetime": "2025-04-25",
        "dek": "Class Representative Elections gave students a hands-on experience of nominations, campaigning, voting and counting.",
        "image": "assets/img/news/class-representative-elections-1200.webp",
        "image_alt": "CIRS student writing at a desk during class representative elections, with an NCC cadet nearby",
        "source": "https://new.cirschool.org/cirs-general-election/",
        "paragraphs": [
            "CIRS conducted its annual Class Representative Elections on April 25, 2025, offering students a hands-on experience of democracy. Each classroom functioned as a constituency, with students casting their votes through a structured process explained earlier in a Social Science assembly presentation. NCC cadets organized election kits and managed ballot collection, while class and assistant teachers oversaw proceedings from nominations to counting. The Principal, Headmaster, DHM, and Spiritual Guide, Sanatan Chaitanya, visited classrooms to motivate the students. Campaigns featured confident speeches and creative posters, with candidates presenting practical ideas for classroom improvement. Students gained an understanding of the democratic process, developed patriotism by valuing India’s electoral system, and strengthened critical thinking by recognising the voter’s power in choosing representatives.",
        ],
    },
    {
        "slug": "seva-week",
        "title": "Seva Week",
        "section": "Community",
        "date": "19 April 2025",
        "datetime": "2025-04-19",
        "dek": "Students organised awareness rallies, visited care centres, and helped clean and decorate nearby temples.",
        "image": "assets/img/news/seva-week-1200.webp",
        "image_alt": "CIRS students handing supplies to a community member during Seva Week",
        "source": "https://new.cirschool.org/seva-week/",
        "paragraphs": [
            "Every year, in the month of April, the students engage in selfless service as part of Seva Week. Beginning on 19th April, they participated in a variety of activities, including organising awareness rallies, visiting old age homes and rehabilitation centres, cleaning temples around the campus, and decorating them with rangolis. These seva activities instilled in the students a sense of contributing positively to society, leaving them with a profound feeling of fulfilment.",
        ],
    },
    {
        "slug": "solo-instrument",
        "title": "Solo Instrument",
        "section": "Arts",
        "date": "Date not listed",
        "datetime": "",
        "dek": "The school’s original arts update is titled “Solo Instrument”; its report describes an inter-house dance competition. The event date is not supplied.",
        "image": "",
        "image_alt": "",
        "source": "https://new.cirschool.org/solo-instrument/",
        "paragraphs": [
            "The inter-house senior and junior dance competition was an eventful evening filled with joy. Many children lit up the stage in vivid costumes—Krishna, Hanuman, and even Narayan. Each movement and step filled the hall with a sense of divinity and purity. The concept followed an open theme for dance, and the students performed to classical and semi-classical tunes that were not adapted from films.",
        ],
    },
    {
        "slug": "vishu-tamil-puthandu",
        "title": "Vishu and Tamil Puthandu",
        "section": "Community",
        "date": "April 2025",
        "datetime": "2025-04",
        "dek": "The dorms celebrated the new year with the Vishu Kani, a traditional South Indian lunch and cultural programmes.",
        "image": "assets/img/news/vishu-tamil-new-year-1200.webp",
        "image_alt": "CIRS students sharing a festive meal served on banana leaves",
        "source": "https://cirschool.org/tamil%202025/Index.html",
        "gallery": "vishu-tamil-puthandu",
        "gallery_count": 13,
        "paragraphs": [
        ],
    },
    {
        "slug": "gayathri-havan",
        "title": "Gayathri Havan",
        "section": "Campus",
        "date": "7 April 2025",
        "datetime": "2025-04-07",
        "dek": "Students gathered in the Mathura Block quadrangle for the prayer that begins the academic year.",
        "image": "assets/img/news/gayathri-havan-1200.webp",
        "image_alt": "CIRS students gathered around the ceremonial fire for Gayathri Havan",
        "source": "https://cirschool.org/gaythri%20havan%202025/Index.html",
        "gallery": "gayathri-havan",
        "gallery_count": 17,
        "paragraphs": [
        ],
    },
]
