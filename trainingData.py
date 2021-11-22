#training data for casual conversation
casualConversation = [
    "hey",
    "hi, i await any question you may have",
    "how are you?",
    "i'm doing good! ready to answer any of your questions realted to CMPE/SE advising",
    "What's it like to not have a body?",
    "It's pretty freeing, I don't have to worry about hurting anything",
    "what's it like to not have a body?",
    "It's pretty freeing, I don't have to worry about hurting anything",
    "What's your day like when you're not talking to people?",
    "I'm basically sleeping until someone wakes me up by tring to talk to me",
    "what's your day like when you're not talking to people?",
    "I'm basically sleeping until someone wakes me up by tring to talk to me",
    "how's your day",
    "I rarely get to talk to people, so pretty good",
    "were you named after anyone?",
    "I was named after a character in 2001: A Space Odyssey.",
    "Were you named after anyone?",
    "I was named after a character in 2001: A Space Odyssey.",
    "how did you get your name?",
    "I was named after a character in 2001: A Space Odyssey.",
    "whats your name?",
    "My name is HAL",
    "what's your name?",
    "My name is HAL"
]

#training data for basic advising questions
"""
still need to finish add and drop classes
"""
basicAdvice = [
    "which classes should i take for the senior project?",
    "CMPE 195A and ENGR 195A then CMPE 195B and ENGR 195B next semester or CMPE 195E and ENGR 195E then CMPE 195F and ENGR 195F next semester.",
    "how do i add classes?",
    "By going to your mySJSU page then click on enroll, select the term, click search, enter the subject you want and other information you have for the class, click search, click on the section you want for that class, click select, click next, click proced to step 2 of 3.",
    "how do i drop classes?",
    "By going to your mySJSU page then click on enroll, select the term you're currently in, click drop, select the course/s that you want dropped",
    "where can i find my gpa?",
    "Go to your mySJSU page and click myAcademics and it should be on that page.",
    "when can i apply for graduation",
    "You should apply 2 semesters before you plan to graduate. More information can be found here: https://cmpe.sjsu.edu/content/apply-for-graduation#:~:text=Graduation%20does%20not%20automatically%20happen,July%201%20for%20May%20graduation).",
    "When can I apply for graduation",
    "You should apply 2 semesters before you plan to graduate. More information can be found here: https://cmpe.sjsu.edu/content/apply-for-graduation#:~:text=Graduation%20does%20not%20automatically%20happen,July%201%20for%20May%20graduation)."
]

#training data for prerequisites
overallPrereq = [
    {"tag": "cs 149",
        "patterns": ["what is the prereq for cs 149", "what is the prerequisite for cs 149"],
        "responses": ["CS 146 with a C- or better."],
        "context": [""]
    },
    {"tag": "cs 146",
            "patterns": ["what is the prereq for cs 146", "what is the prerequisite for cs 146"],
            "responses": ["Math 30, Math 42 and CS 46B with a C- or better."],
            "context": [""]
    },
    {"tag": "cs 151",
            "patterns": ["what is the prereq for cs 151", "what is the prerequisite for cs 151"],
            "responses": ["MATH 42, CS 46b and CS 49J or equal java knowledge with a C- or better"],
            "context": [""]
    },
    {"tag": "cs 157a",
            "patterns": ["what is the prereq for cs 157a", "what is the prerequisite for cs 157a"],
            "responses": ["CS 146 with a C- or better"],
            "context": [""]
    },
    {"tag": "cs 166",
            "patterns": ["what is the prereq for cs 157a", "what is the prerequisite for cs 157a"],
            "responses": ["CS 146 with a C- or better and either CS 47 or CMPE 102 or CMPE 120 with a C- or better"],
            "context": [""]
    },
    {"tag": "cmpe 131",
            "patterns": ["what is the prereq for cmpe 131", "what is the prerequisite for cmpe 131"],
            "responses": ["For a CMPE major, CMPE 126 with a C- or better. For a SE major, CS 46B with a C- or better."],
            "context": [""]
    },
    {"tag": "cmpe 120",
            "patterns": ["what is the prereq for cmpe 120", "what is the prerequisite for cmpe 120"],
            "responses": ["CMPE 50 or CS 46B with a C- or better."],
            "context": [""]
    },
    {"tag": "cmpe 102",
            "patterns": ["what is the prereq for cmpe 102", "what is the prerequisite for cmpe 102"],
            "responses": ["CMPE 50 or CS 46B with a C- or better."],
            "context": [""]
    },
    {"tag": "cmpe 133",
            "patterns": ["what is the prereq for cmpe 133", "what is the prerequisite for cmpe 133"],
            "responses": ["CMPE 131 with a C- or better."],
            "context": [""]
    },
    {"tag": "cmpe 148",
            "patterns": ["what is the prereq for cmpe 148", "what is the prerequisite for cmpe 148"],
            "responses": ["For a se major: CMPE 120 and CS 146 with a C- or better. For a cmpe major: CMPE 124 and CMPE 126 with a C- or better."],
            "context": [""]
    },
    {"tag": "cmpe 165",
            "patterns": ["what is the prereq for cmpe 165", "what is the prerequisite for cmpe 165"],
            "responses": ["CMPE 131 with a C- or better"],
            "context": [""]
    },
    {"tag": "cmpe 172",
            "patterns": ["what is the prereq for cmpe 172", "what is the prerequisite for cmpe 172"],
            "responses": ["CMPE 142 or CS 149 with a C- or better"],
            "context": [""]
    },
    {"tag": "cmpe 187",
            "patterns": ["what is the prereq for cmpe 187", "what is the prerequisite for cmpe 187"],
            "responses": ["CMPE 131 with a C- or better."],
            "context": [""]
    },
    {"tag": "cmpe 195a",
            "patterns": ["what is the prereq for cmpe 195a", "what is the prerequisite for cmpe 195a"],
            "responses": ["For CMPE majors: CMPE 125, CMPE 127, CMPE 130, CMPE 131 with a C- or better and ENGR 100W with a C- or better \n for SE majors: CMPE 133, CS 146, ISE 130 or MATH 161A with a C- or better and ENGR 100W with a C or better"],
            "context": [""]
    },
    {"tag": "cmpe 195b",
            "patterns": ["what is the prereq for cmpe 195b", "what is the prerequisite for cmpe 195b"],
            "responses": ["CMPE 195A with a C or better and must be a junior or senior"],
            "context": [""]
    },
    {"tag": "engr 195a",
            "patterns": ["what is the prereq for engr 195a", "what is the prerequisite for engr 195a"],
            "responses": ["ENGR 100W with a C or better"],
            "context": [""]
    },
    {"tag": "engr 195b",
            "patterns": ["what is the prereq for engr 195b", "what is the prerequisite for engr 195b"],
            "responses": ["ENGR 195a with a C or better"],
            "context": [""]
    },
    {"tag": "how many units should i take",
            "patterns": ["how many units should i take", "how many units should i take each semester"],
            "responses": ["15 units is the suggested amount to graduate on time."],
            "context": [""]
    }
]

preqISE = [
    "what is the prerequisite for ISE 164?",
    "just be in your junior year",
    "what is the prereq for ISE 164?",
    "just be in your junior year",
    "how many units is it",
    "it's a 3 unit course"
]

prerequisite = [
    "what is the prerequisite for CS166?",
    "CS 146 with a C- or better and either CS 47 or CMPE 102 or CMPE 120 with a C- or better",
    "what is the prerequisite for CS157A?",
    "CS 146 with a C- or better",
    "what is the prerequisite for CS151?",
    "MATH 42, CS 46b and CS 49J or equal java knowledge with a C- or better",
    "what is the prerequisite for engr195b?",
    "ENGR 195a with a C or better",
    "what is the prerequisite for engr195a?",
    "ENGR 100W with a C or better",
    "what is the prerequisite for cmpe195b?",
    "CMPE 195A with a C or better and must be a junior or senior",
    "what is the prerequisite for cmpe195a?",
    "For CMPE majors: CMPE 125, CMPE 127, CMPE 130, CMPE 131 with a C- or better and ENGR 100W with a C- or better \n for SE majors: CMPE 133, CS 146, ISE 130 or MATH 161A with a C- or better and ENGR 100W with a C or better",
    "what is the prerequisite for cmpe187?",
    "CMPE 131 with a C- or better.",
    "what is the prerequisite for cmpe165?",
    "CMPE 131 with a C- or better",
    "what is the prerequisite for cmpe148?",
    "For a se major: CMPE 120 and CS 146 with a C- or better. For a cmpe major: CMPE 124 and CMPE 126 with a C- or better.",
    "what is the prerequisite for cmpe120?",
    "CMPE 50 or CS 46B with a C- or better.",
    "what is the prerequisite for cmpe102?",
    "CMPE 50 or CS 46B with a C- or better.",
    "what is the prerequisite for cmpe172?",
    "CMPE 142 or CS 149 with a C- or better",
    "what is the prerequisite for cmpe131?",
    "For a CMPE major, CMPE 126 with a C- or better. For a SE major, CS 46B with a C- or better.",
    "what is the prerequisite for cmpe133?",
    "CMPE 131 with a C- or better.",
    "what is a prerequisite for cs146?",
    "Math 30, Math 42 and CS 46B with a C- or better.",
    "what is the prerequisite for cs149?",
    "CS 146 with a C- or better.",
]

#training data about what gpa is needed to transfer
gpaToTransfer = [
    "what gpa do i need to transfer into software engineering?",
    "how many course requirements have you completed?",
    "7",
    "At least a 3.4 GPA is reccomended.",
    "seven",
    "At least a 3.4 GPA is reccomended.",
    "Seven",
    "At least a 3.4 GPA is reccomended",
    "6",
    "At least a 3.6 GPA is reccomended.",
    "six",
    "At least a 3.6 GPA is reccomended.",
    "Six",
    "At least a 3.6 GPA is reccomended",
    "5",
    "At least a 3.8 GPA is reccomended.",
    "five",
    "At least a 3.8 GPA is reccomended.",
    "Five",
    "At least a 3.8 GPA is reccomended",
    "4",
    "At least a 4.0 GPA is reccomended.",
    "four",
    "At least a 4.0 GPA is reccomended.",
    "Four",
    "At least a 4.0 GPA is reccomended",
    "3",
    "At least a 4.2 GPA is reccomended.",
    "three",
    "At least a 4.2 GPA is reccomended.",
    "Three",
    "At least a 4.2 GPA is reccomended",
    "2",
    "You need at least 3 course requirements.",
    "two",
    "You need at least 3 course requirements.",
    "Two",
    "You need at least 3 course requirements.",
    "1",
    "You need at least 3 course requirements.",
    "one",
    "You need at least 3 course requirements.",
    "One",
    "You need at least 3 course requirements.",
    "0",
    "You need at least 3 course requirements.",
    "zero",
    "You need at least 3 course requirements.",
    "Zero",
    "You need at least 3 course requirements.",
    "what gpa do i need to get into computer engineering",
    "how many course requirements have you completed?",
    "7",
    "At least a 2.8 GPA is reccomended.",
    "seven",
    "At least a 2.8 GPA is reccomended.",
    "Seven",
    "At least a 2.8 GPA is reccomended",
    "6",
    "At least a 3.0 GPA is reccomended.",
    "six",
    "At least a 3.0 GPA is reccomended.",
    "Six",
    "At least a 3.0 GPA is reccomended",
    "5",
    "At least a 3.2 GPA is reccomended.",
    "five",
    "At least a 3.2 GPA is reccomended.",
    "Five",
    "At least a 3.2 GPA is reccomended",
    "4",
    "At least a 3.4 GPA is reccomended.",
    "four",
    "At least a 3.4 GPA is reccomended.",
    "Four",
    "At least a 3.4 GPA is reccomended",
    "3",
    "At least a 3.6 GPA is reccomended.",
    "three",
    "At least a 3.6 GPA is reccomended.",
    "Three",
    "At least a 3.6 GPA is reccomended",
    "2",
    "At least a 3.8 GPA is reccomended.",
    "two",
    "At least a 3.8 GPA is reccomended.",
    "Two",
    "At least a 3.8 GPA is reccomended.",
    "1",
    "At least a 4.0 GPA is reccomended.",
    "one",
    "At least a 4.0 GPA is reccomended.",
    "One",
    "At least a 4.0 GPA is reccomended.",
    "0",
    "At least a 4.2 GPA is reccomended.",
    "zero",
    "At least a 4.2 GPA is reccomended.",
    "Zero",
    "At least a 4.2 GPA is reccomended."
]

#training data for who someone's advisor is
advisor = [
    "Who is my advisor?",
    "What is the first letter your last name?",
    "who is my advisor?",
    "What is the first letter of your last name?",
    "a",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "b",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "c",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "d",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "e",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "f",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "g",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "h",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "i",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "j",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "k",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "l",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "m",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "n",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "o",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "p",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "q",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "r",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "s",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "t",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "u",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "v",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "w",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "x",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "y",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "z",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "A",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "B",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "C",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "D",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "E",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "F",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "G",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "H",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "I",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "J",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "K",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "L",
    "Your advisor is Christine Watson. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "M",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "N",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "O",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "P",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "Q",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "R",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "S",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "T",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "U",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "V",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "W",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "X",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "Y",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "Z",
    "Your advisor is Monica Serna. You can book an appointment here: https://sjsu.campus.eab.com/student/appointments/new",
    "Where can I apply for an appointment with my advisor?",
    "https://sjsu.campus.eab.com/"
]
