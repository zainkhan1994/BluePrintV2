import type { RawNode } from './types';

export const initialData: RawNode[] = [
  {
    "id": 1,
    "name": "P - Personal",
    "description": "Life, Home, ID, Contacts, Events",
    "type": "folder",
    "parentId": null
  },
  {
    "id": 500,
    "name": "H - Health",
    "description": "Medical, mental, and personal wellness information",
    "type": "folder",
    "parentId": null
  },
  {
    "id": 600,
    "name": "W - Work",
    "description": "Professional work history, employers, projects, and portfolio",
    "type": "folder",
    "parentId": null
  },
  {
    "id": 700,
    "name": "P - Projects",
    "description": "Personal and professional development projects",
    "type": "folder",
    "parentId": null
  },
  {
    "id": 501,
    "name": "Medical_Records",
    "description": "Doctors, conditions, symptoms, and test history",
    "type": "folder",
    "parentId": 500
  },
  {
    "id": 502,
    "name": "Doctors_and_Providers",
    "description": "Contacts, specialties, visit notes",
    "type": "folder",
    "parentId": 501
  },
  {
    "id": 503,
    "name": "Conditions_and_Symptoms",
    "description": "Diagnoses, recurring issues, notes",
    "type": "folder",
    "parentId": 501
  },
  {
    "id": 504,
    "name": "Lab_Results_and_Tests",
    "description": "Reports and uploads from labs",
    "type": "folder",
    "parentId": 501
  },
  {
    "id": 505,
    "name": "LabCorp",
    "description": "LabCorp test results",
    "type": "file",
    "parentId": 504
  },
  {
    "id": 506,
    "name": "Quest_Diagnostics",
    "description": "Quest Diagnostics test results",
    "type": "file",
    "parentId": 504
  },
  {
    "id": 507,
    "name": "Other_Labs",
    "description": "Other laboratory test results",
    "type": "file",
    "parentId": 504
  },
  {
    "id": 508,
    "name": "Timeline_and_Notes",
    "description": "Chronological medical events and reflections",
    "type": "folder",
    "parentId": 501
  },
  {
    "id": 509,
    "name": "Medications_and_Supplements",
    "description": "Current, past, and scheduled intake",
    "type": "folder",
    "parentId": 500
  },
  {
    "id": 510,
    "name": "Active_Medications",
    "description": "Currently prescribed medications",
    "type": "file",
    "parentId": 509
  },
  {
    "id": 511,
    "name": "Past_Treatments",
    "description": "Previous medications and treatments",
    "type": "file",
    "parentId": 509
  },
  {
    "id": 512,
    "name": "Supplements",
    "description": "Vitamins and dietary supplements",
    "type": "file",
    "parentId": 509
  },
  {
    "id": 513,
    "name": "Dosage_and_Schedule",
    "description": "Medication schedules and dosages",
    "type": "file",
    "parentId": 509
  },
  {
    "id": 514,
    "name": "Insurance_and_Coverage",
    "description": "Policies, claims, and provider networks",
    "type": "folder",
    "parentId": 500
  },
  {
    "id": 515,
    "name": "Health_Insurance_Policies",
    "description": "Health insurance policy information",
    "type": "file",
    "parentId": 514
  },
  {
    "id": 516,
    "name": "Claims_and_EOBs",
    "description": "Insurance claims and explanation of benefits",
    "type": "file",
    "parentId": 514
  },
  {
    "id": 517,
    "name": "Provider_Network_Info",
    "description": "In-network provider information",
    "type": "file",
    "parentId": 514
  },
  {
    "id": 518,
    "name": "Mental_Health",
    "description": "Therapy, emotional tracking, and self-reflection",
    "type": "folder",
    "parentId": 500
  },
  {
    "id": 519,
    "name": "Therapy_Notes",
    "description": "Therapy session notes and insights",
    "type": "file",
    "parentId": 518
  },
  {
    "id": 520,
    "name": "Mood_Tracking",
    "description": "Emotional and mood tracking data",
    "type": "file",
    "parentId": 518
  },
  {
    "id": 521,
    "name": "Reflections",
    "description": "Personal reflections and journaling",
    "type": "file",
    "parentId": 518
  },
  {
    "id": 522,
    "name": "Health_Apps",
    "description": "Linked apps and digital health platforms",
    "type": "folder",
    "parentId": 500
  },
  {
    "id": 523,
    "name": "MyChart",
    "description": "MyChart health portal",
    "type": "file",
    "parentId": 522
  },
  {
    "id": 524,
    "name": "Healow",
    "description": "Healow health app",
    "type": "file",
    "parentId": 522
  },
  {
    "id": 525,
    "name": "PT_Solutions",
    "description": "PT Solutions physical therapy",
    "type": "file",
    "parentId": 522
  },
  {
    "id": 526,
    "name": "BetterSleep",
    "description": "BetterSleep app",
    "type": "file",
    "parentId": 522
  },
  {
    "id": 527,
    "name": "Life_Time",
    "description": "Life Time fitness",
    "type": "file",
    "parentId": 522
  },
  {
    "id": 601,
    "name": "Work_Timeline",
    "description": "Chronological work history and career progression",
    "type": "folder",
    "parentId": 600
  },
  {
    "id": 602,
    "name": "Employers",
    "description": "All employers and organizations worked with",
    "type": "folder",
    "parentId": 600
  },
  {
    "id": 603,
    "name": "R-Cubed",
    "description": "R-Cubed employment and projects",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 6031,
    "name": "Pay_Stubs_Benefits",
    "description": "Pay stubs, benefits, and employment documents",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6032,
    "name": "Business_Documents",
    "description": "Company documents, branding, and official records",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6033,
    "name": "Cleverly_Dashboard_Data",
    "description": "Cleverly dashboard exports and analytics",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6034,
    "name": "LinkedIn_Social_Media",
    "description": "LinkedIn analytics and social media data",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6035,
    "name": "Meeting_Calendar_Data",
    "description": "Meeting schedules, calendar exports, and Jim's calendar",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6036,
    "name": "Microsoft_Teams_OneDrive",
    "description": "Teams chats and OneDrive media files",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6037,
    "name": "Sales_Pipeline_Data",
    "description": "Sales pipeline, territory lists, and qualification guidelines",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6038,
    "name": "Business_Development",
    "description": "Business development strategies and planning documents",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6039,
    "name": "Marketing_GTM",
    "description": "Marketing materials, GTM assets, and Oracle overviews",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6040,
    "name": "Partner_Contact_Data",
    "description": "Partner contacts, collaboration accounts, and client success",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6041,
    "name": "Lead_Generation_Data",
    "description": "Lead generation, Apollo data, and suggested contacts",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 6042,
    "name": "Website_Planning",
    "description": "Website requirements, search history, and Zoom recordings",
    "type": "folder",
    "parentId": 603
  },
  {
    "id": 604,
    "name": "Red_River_Development",
    "description": "Red River Development employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 605,
    "name": "Trulo_Homes",
    "description": "Trulo Homes employment across multiple locations",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 606,
    "name": "Trulo_Homes_Bentoville",
    "description": "Trulo Homes - Bentoville location",
    "type": "folder",
    "parentId": 605
  },
  {
    "id": 607,
    "name": "Trulo_Homes_Jenks",
    "description": "Trulo Homes - Jenks location",
    "type": "folder",
    "parentId": 605
  },
  {
    "id": 608,
    "name": "Trulo_Homes_Whitestone",
    "description": "Trulo Homes - Whitestone location",
    "type": "folder",
    "parentId": 605
  },
  {
    "id": 609,
    "name": "Trulo_Homes_Kansas_City",
    "description": "Trulo Homes - Kansas City location",
    "type": "folder",
    "parentId": 605
  },
  {
    "id": 610,
    "name": "Rose_Rock_Development",
    "description": "Rose Rock Development employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 611,
    "name": "Reunion",
    "description": "Reunion project",
    "type": "folder",
    "parentId": 610
  },
  {
    "id": 612,
    "name": "Palace",
    "description": "Palace project",
    "type": "folder",
    "parentId": 610
  },
  {
    "id": 613,
    "name": "Adams",
    "description": "Adams project",
    "type": "folder",
    "parentId": 610
  },
  {
    "id": 614,
    "name": "Vandever",
    "description": "Vandever project",
    "type": "folder",
    "parentId": 610
  },
  {
    "id": 615,
    "name": "Minaret_Foundation",
    "description": "Minaret Foundation employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 616,
    "name": "Ashford_Communities",
    "description": "Ashford Communities employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 617,
    "name": "US_Census_Bureau",
    "description": "US Census Bureau employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 618,
    "name": "Gulf_Coast_Regional_Blood_Center",
    "description": "Gulf Coast Regional Blood Center employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 619,
    "name": "ISGH",
    "description": "Islamic Society of Greater Houston employment",
    "type": "folder",
    "parentId": 602
  },
  {
    "id": 620,
    "name": "Maryam_Islamic_Center",
    "description": "Maryam Islamic Center employment",
    "type": "folder",
    "parentId": 619
  },
  {
    "id": 621,
    "name": "Work_Projects",
    "description": "Professional projects and deliverables",
    "type": "folder",
    "parentId": 600
  },
  {
    "id": 622,
    "name": "Tools",
    "description": "Work-related tools and software",
    "type": "folder",
    "parentId": 600
  },
  {
    "id": 623,
    "name": "Work_Portfolio",
    "description": "Professional portfolio and achievements",
    "type": "folder",
    "parentId": 600
  },
  {
    "id": 701,
    "name": "SFA",
    "description": "SFA project documentation and resources",
    "type": "folder",
    "parentId": 700
  },
  {
    "id": 702,
    "name": "SpaceApps",
    "description": "NASA Space Apps Challenge projects",
    "type": "folder",
    "parentId": 700
  },
  {
    "id": 703,
    "name": "NASA_JSC",
    "description": "NASA Johnson Space Center projects",
    "type": "folder",
    "parentId": 700
  },
  {
    "id": 704,
    "name": "Hackathons",
    "description": "Hackathon projects and competitions",
    "type": "folder",
    "parentId": 700
  },
  {
    "id": 705,
    "name": "Xain_Dev",
    "description": "Xain development projects and personal coding",
    "type": "folder",
    "parentId": 700
  },
  {
    "id": 2,
    "name": "Important_Documents",
    "description": "Core records and IDs",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 3,
    "name": "Identity_Records",
    "description": "Official identification documents",
    "type": "folder",
    "parentId": 2
  },
  {
    "id": 4,
    "name": "Passport",
    "description": "",
    "type": "file",
    "parentId": 3
  },
  {
    "id": 5,
    "name": "Drivers_License",
    "description": "",
    "type": "file",
    "parentId": 3
  },
  {
    "id": 6,
    "name": "Social_Security_Card",
    "description": "",
    "type": "file",
    "parentId": 3
  },
  {
    "id": 7,
    "name": "Birth_Certificate",
    "description": "",
    "type": "file",
    "parentId": 3
  },
  {
    "id": 8,
    "name": "Voter_Registration",
    "description": "",
    "type": "file",
    "parentId": 3
  },
  {
    "id": 9,
    "name": "Medical_Records_Personal",
    "description": "Health summaries and insurance info",
    "type": "folder",
    "parentId": 2
  },
  {
    "id": 10,
    "name": "Immunization_Records",
    "description": "",
    "type": "file",
    "parentId": 9
  },
  {
    "id": 11,
    "name": "Health_Insurance_Cards",
    "description": "",
    "type": "file",
    "parentId": 9
  },
  {
    "id": 12,
    "name": "Primary_Care_Notes",
    "description": "",
    "type": "file",
    "parentId": 9
  },
  {
    "id": 13,
    "name": "Legal_Documents",
    "description": "Contracts, agreements, authorizations",
    "type": "folder",
    "parentId": 2
  },
  {
    "id": 14,
    "name": "Lease_Agreements",
    "description": "",
    "type": "file",
    "parentId": 13
  },
  {
    "id": 15,
    "name": "Power_of_Attorney",
    "description": "",
    "type": "file",
    "parentId": 13
  },
  {
    "id": 16,
    "name": "Wills_Trusts",
    "description": "",
    "type": "file",
    "parentId": 13
  },
  {
    "id": 17,
    "name": "NDAs_Employment_Contracts",
    "description": "",
    "type": "file",
    "parentId": 13
  },
  {
    "id": 18,
    "name": "Tax_Records",
    "description": "Annual filings and statements",
    "type": "folder",
    "parentId": 2
  },
  {
    "id": 19,
    "name": "W2_Forms",
    "description": "",
    "type": "file",
    "parentId": 18
  },
  {
    "id": 20,
    "name": "1099_Forms",
    "description": "",
    "type": "file",
    "parentId": 18
  },
  {
    "id": 21,
    "name": "IRS_Returns",
    "description": "",
    "type": "file",
    "parentId": 18
  },
  {
    "id": 22,
    "name": "Insurance",
    "description": "Coverage documents",
    "type": "folder",
    "parentId": 2
  },
  {
    "id": 23,
    "name": "Auto_Insurance",
    "description": "",
    "type": "file",
    "parentId": 22
  },
  {
    "id": 24,
    "name": "Health_Insurance",
    "description": "",
    "type": "file",
    "parentId": 22
  },
  {
    "id": 25,
    "name": "Life_Insurance",
    "description": "",
    "type": "file",
    "parentId": 22
  },
  {
    "id": 26,
    "name": "Renters_or_Homeowners",
    "description": "",
    "type": "file",
    "parentId": 22
  },
  {
    "id": 27,
    "name": "Contacts_Network",
    "description": "Personal and professional connections",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 28,
    "name": "Family",
    "description": "Family member profiles",
    "type": "folder",
    "parentId": 27
  },
  {
    "id": 29,
    "name": "Immediate",
    "description": "Immediate family members",
    "type": "folder",
    "parentId": 28
  },
  {
    "id": 30,
    "name": "Extended",
    "description": "Extended family members",
    "type": "folder",
    "parentId": 28
  },
  {
    "id": 31,
    "name": "Mom",
    "description": "Mother's profile",
    "type": "file",
    "parentId": 29
  },
  {
    "id": 32,
    "name": "Mom_Notes",
    "description": "Notes about Mom",
    "type": "file",
    "parentId": 31
  },
  {
    "id": 33,
    "name": "Mom_Photos",
    "description": "Photos of Mom",
    "type": "file",
    "parentId": 31
  },
  {
    "id": 34,
    "name": "Dad",
    "description": "Father's profile",
    "type": "file",
    "parentId": 29
  },
  {
    "id": 35,
    "name": "Dad_Notes",
    "description": "Notes about Dad",
    "type": "file",
    "parentId": 34
  },
  {
    "id": 36,
    "name": "Dad_Photos",
    "description": "Photos of Dad",
    "type": "file",
    "parentId": 34
  },
  {
    "id": 37,
    "name": "Stepmom",
    "description": "Stepmother's profile",
    "type": "file",
    "parentId": 29
  },
  {
    "id": 38,
    "name": "Stepmom_Notes",
    "description": "Notes about Stepmom",
    "type": "file",
    "parentId": 37
  },
  {
    "id": 39,
    "name": "Stepmom_Photos",
    "description": "Photos of Stepmom",
    "type": "file",
    "parentId": 37
  },
  {
    "id": 40,
    "name": "Sister",
    "description": "Sister's profile",
    "type": "file",
    "parentId": 29
  },
  {
    "id": 41,
    "name": "Sister_Notes",
    "description": "Notes about Sister",
    "type": "file",
    "parentId": 40
  },
  {
    "id": 42,
    "name": "Sister_Photos",
    "description": "Photos of Sister",
    "type": "file",
    "parentId": 40
  },
  {
    "id": 43,
    "name": "Brother",
    "description": "Brother's profile",
    "type": "file",
    "parentId": 29
  },
  {
    "id": 44,
    "name": "Brother_Notes",
    "description": "Notes about Brother",
    "type": "file",
    "parentId": 43
  },
  {
    "id": 45,
    "name": "Brother_Photos",
    "description": "Photos of Brother",
    "type": "file",
    "parentId": 43
  },
  {
    "id": 46,
    "name": "Sister_2",
    "description": "Second sister's profile",
    "type": "file",
    "parentId": 29
  },
  {
    "id": 47,
    "name": "Sister_2_Notes",
    "description": "Notes about Sister 2",
    "type": "file",
    "parentId": 46
  },
  {
    "id": 48,
    "name": "Sister_2_Photos",
    "description": "Photos of Sister 2",
    "type": "file",
    "parentId": 46
  },
  {
    "id": 49,
    "name": "Sister_in_Law",
    "description": "Sister-in-law's profile",
    "type": "file",
    "parentId": 30
  },
  {
    "id": 50,
    "name": "Sister_in_Law_Notes",
    "description": "Notes about Sister-in-law",
    "type": "file",
    "parentId": 49
  },
  {
    "id": 51,
    "name": "Sister_in_Law_Photos",
    "description": "Photos of Sister-in-law",
    "type": "file",
    "parentId": 49
  },
  {
    "id": 52,
    "name": "Brother_in_Law",
    "description": "Brother-in-law's profile",
    "type": "file",
    "parentId": 30
  },
  {
    "id": 53,
    "name": "Brother_in_Law_Notes",
    "description": "Notes about Brother-in-law",
    "type": "file",
    "parentId": 52
  },
  {
    "id": 54,
    "name": "Brother_in_Law_Photos",
    "description": "Photos of Brother-in-law",
    "type": "file",
    "parentId": 52
  },
  {
    "id": 55,
    "name": "Nephew",
    "description": "Nephew's profile (Brother + Sister-in-law's child)",
    "type": "file",
    "parentId": 30
  },
  {
    "id": 56,
    "name": "Nephew_Notes",
    "description": "Notes about Nephew",
    "type": "file",
    "parentId": 55
  },
  {
    "id": 57,
    "name": "Nephew_Photos",
    "description": "Photos of Nephew",
    "type": "file",
    "parentId": 55
  },
  {
    "id": 58,
    "name": "Niece_1",
    "description": "First niece's profile",
    "type": "file",
    "parentId": 30
  },
  {
    "id": 59,
    "name": "Niece_1_Notes",
    "description": "Notes about Niece 1",
    "type": "file",
    "parentId": 58
  },
  {
    "id": 60,
    "name": "Niece_1_Photos",
    "description": "Photos of Niece 1",
    "type": "file",
    "parentId": 58
  },
  {
    "id": 61,
    "name": "Niece_2",
    "description": "Second niece's profile",
    "type": "file",
    "parentId": 30
  },
  {
    "id": 62,
    "name": "Niece_2_Notes",
    "description": "Notes about Niece 2",
    "type": "file",
    "parentId": 61
  },
  {
    "id": 63,
    "name": "Niece_2_Photos",
    "description": "Photos of Niece 2",
    "type": "file",
    "parentId": 61
  },
  {
    "id": 64,
    "name": "Nephew_2",
    "description": "Second nephew's profile (Sister + Brother-in-law's children)",
    "type": "file",
    "parentId": 30
  },
  {
    "id": 65,
    "name": "Nephew_2_Notes",
    "description": "Notes about Nephew 2",
    "type": "file",
    "parentId": 64
  },
  {
    "id": 66,
    "name": "Nephew_2_Photos",
    "description": "Photos of Nephew 2",
    "type": "file",
    "parentId": 64
  },
  {
    "id": 67,
    "name": "Attributes",
    "description": "Relationship metadata",
    "type": "folder",
    "parentId": 28
  },
  {
    "id": 68,
    "name": "Connection_Type",
    "description": "",
    "type": "file",
    "parentId": 67
  },
  {
    "id": 69,
    "name": "Residence_Status",
    "description": "",
    "type": "file",
    "parentId": 67
  },
  {
    "id": 70,
    "name": "Contact_Frequency",
    "description": "",
    "type": "file",
    "parentId": 67
  },
  {
    "id": 71,
    "name": "Support_Role",
    "description": "",
    "type": "file",
    "parentId": 67
  },
  {
    "id": 72,
    "name": "Shared_Responsibilities",
    "description": "",
    "type": "file",
    "parentId": 67
  },
  {
    "id": 73,
    "name": "Groups",
    "description": "Relationship clusters auto-generated by assistant",
    "type": "folder",
    "parentId": 28
  },
  {
    "id": 74,
    "name": "Parents (Mom, Dad, Stepmom)",
    "description": "",
    "type": "file",
    "parentId": 73
  },
  {
    "id": 75,
    "name": "Siblings (Sister, Brother, Sister_2)",
    "description": "",
    "type": "file",
    "parentId": 73
  },
  {
    "id": 76,
    "name": "In_Laws (Sister_in_Law, Brother_in_Law)",
    "description": "",
    "type": "file",
    "parentId": 73
  },
  {
    "id": 77,
    "name": "Kids (All nieces and nephews)",
    "description": "",
    "type": "file",
    "parentId": 73
  },
  {
    "id": 78,
    "name": "Extended (Uncles, aunts, cousins – optional future expansion)",
    "description": "",
    "type": "file",
    "parentId": 73
  },
  {
    "id": 79,
    "name": "Friends",
    "description": "Personal friendships and social connections",
    "type": "folder",
    "parentId": 27
  },
  {
    "id": 80,
    "name": "Childhood",
    "description": "Friends from childhood",
    "type": "folder",
    "parentId": 79
  },
  {
    "id": 81,
    "name": "High_School",
    "description": "High school friends",
    "type": "folder",
    "parentId": 79
  },
  {
    "id": 82,
    "name": "College",
    "description": "College friends",
    "type": "folder",
    "parentId": 79
  },
  {
    "id": 83,
    "name": "Events",
    "description": "Friends from events (SpaceApps, NASA, etc.)",
    "type": "folder",
    "parentId": 79
  },
  {
    "id": 84,
    "name": "Religious_Community",
    "description": "Muslim Network and religious community",
    "type": "folder",
    "parentId": 79
  },
  {
    "id": 85,
    "name": "Current_Acquaintances",
    "description": "Current social acquaintances",
    "type": "folder",
    "parentId": 79
  },
  {
    "id": 86,
    "name": "Professional_Network",
    "description": "Professional connections and colleagues",
    "type": "folder",
    "parentId": 27
  },
  {
    "id": 87,
    "name": "Mentors",
    "description": "Professional mentors and advisors",
    "type": "folder",
    "parentId": 86
  },
  {
    "id": 88,
    "name": "Collaborators",
    "description": "Professional collaborators and partners",
    "type": "folder",
    "parentId": 86
  },
  {
    "id": 89,
    "name": "Clients",
    "description": "Professional clients and business contacts",
    "type": "folder",
    "parentId": 86
  },
  {
    "id": 90,
    "name": "Applications",
    "description": "Mobile and desktop applications",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 91,
    "name": "Social_Community",
    "description": "Social media and community apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 92,
    "name": "Direct_Messaging",
    "description": "Direct messaging applications",
    "type": "folder",
    "parentId": 91
  },
  {
    "id": 93,
    "name": "iMessage",
    "description": "Apple iMessage",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 94,
    "name": "FaceTime",
    "description": "Apple FaceTime",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 95,
    "name": "TextMe",
    "description": "TextMe messaging app",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 96,
    "name": "TextFree",
    "description": "TextFree messaging app",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 97,
    "name": "WhatsApp",
    "description": "WhatsApp messaging",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 98,
    "name": "Facebook_Messenger",
    "description": "Facebook Messenger",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 99,
    "name": "Discord",
    "description": "Discord chat platform",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 100,
    "name": "Slack",
    "description": "Slack workspace communication",
    "type": "file",
    "parentId": 92
  },
  {
    "id": 101,
    "name": "Communities_Groups",
    "description": "Community and group platforms",
    "type": "folder",
    "parentId": 91
  },
  {
    "id": 102,
    "name": "Skool",
    "description": "Skool community platform",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 103,
    "name": "Mighty",
    "description": "Mighty community platform",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 104,
    "name": "Reddit",
    "description": "Reddit social platform",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 105,
    "name": "Meetup",
    "description": "Meetup event platform",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 106,
    "name": "Eventbrite",
    "description": "Eventbrite event platform",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 107,
    "name": "LinkedIn_Events",
    "description": "LinkedIn Events",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 108,
    "name": "Meta_Events",
    "description": "Meta Events",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 109,
    "name": "Faves",
    "description": "Faves community app",
    "type": "file",
    "parentId": 101
  },
  {
    "id": 110,
    "name": "Social_Media",
    "description": "Social media platforms",
    "type": "folder",
    "parentId": 91
  },
  {
    "id": 111,
    "name": "Instagram",
    "description": "Instagram social platform",
    "type": "file",
    "parentId": 110
  },
  {
    "id": 112,
    "name": "TikTok",
    "description": "TikTok video platform",
    "type": "file",
    "parentId": 110
  },
  {
    "id": 113,
    "name": "Snapchat",
    "description": "Snapchat messaging",
    "type": "file",
    "parentId": 110
  },
  {
    "id": 114,
    "name": "Facebook",
    "description": "Facebook social platform",
    "type": "file",
    "parentId": 110
  },
  {
    "id": 115,
    "name": "YouTube",
    "description": "YouTube video platform",
    "type": "file",
    "parentId": 110
  },
  {
    "id": 116,
    "name": "Threads",
    "description": "Threads social platform",
    "type": "file",
    "parentId": 110
  },
  {
    "id": 117,
    "name": "Productivity_Organization",
    "description": "Productivity and organization apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 118,
    "name": "Planning_Notes",
    "description": "Planning and note-taking apps",
    "type": "folder",
    "parentId": 117
  },
  {
    "id": 119,
    "name": "Notion",
    "description": "Notion workspace",
    "type": "file",
    "parentId": 118
  },
  {
    "id": 120,
    "name": "Obsidian",
    "description": "Obsidian note-taking",
    "type": "file",
    "parentId": 118
  },
  {
    "id": 121,
    "name": "Apple_Notes",
    "description": "Apple Notes app",
    "type": "file",
    "parentId": 118
  },
  {
    "id": 122,
    "name": "Google_Tasks",
    "description": "Google Tasks",
    "type": "file",
    "parentId": 118
  },
  {
    "id": 123,
    "name": "Reminders",
    "description": "Apple Reminders",
    "type": "file",
    "parentId": 118
  },
  {
    "id": 124,
    "name": "Calendar",
    "description": "Calendar applications",
    "type": "file",
    "parentId": 118
  },
  {
    "id": 125,
    "name": "Project_Management",
    "description": "Project management and collaboration",
    "type": "folder",
    "parentId": 117
  },
  {
    "id": 126,
    "name": "Asana",
    "description": "Asana project management",
    "type": "file",
    "parentId": 125
  },
  {
    "id": 127,
    "name": "Miro",
    "description": "Miro collaboration platform",
    "type": "file",
    "parentId": 125
  },
  {
    "id": 128,
    "name": "GitHub",
    "description": "GitHub development platform",
    "type": "file",
    "parentId": 125
  },
  {
    "id": 129,
    "name": "Google_Cloud",
    "description": "Google Cloud platform",
    "type": "file",
    "parentId": 125
  },
  {
    "id": 130,
    "name": "Automation_Tools",
    "description": "Automation and productivity tools",
    "type": "folder",
    "parentId": 117
  },
  {
    "id": 131,
    "name": "IFTTT",
    "description": "IFTTT automation",
    "type": "file",
    "parentId": 130
  },
  {
    "id": 132,
    "name": "Shortcuts",
    "description": "Apple Shortcuts",
    "type": "file",
    "parentId": 130
  },
  {
    "id": 133,
    "name": "Scriptable",
    "description": "Scriptable automation",
    "type": "file",
    "parentId": 130
  },
  {
    "id": 134,
    "name": "Pythonista",
    "description": "Pythonista Python IDE",
    "type": "file",
    "parentId": 130
  },
  {
    "id": 135,
    "name": "Fireflies",
    "description": "Fireflies AI meeting assistant",
    "type": "file",
    "parentId": 130
  },
  {
    "id": 136,
    "name": "Finance_Payments",
    "description": "Finance and payment apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 137,
    "name": "Cash_App",
    "description": "Cash App payments",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 138,
    "name": "Venmo",
    "description": "Venmo payments",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 139,
    "name": "PayPal",
    "description": "PayPal payments",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 140,
    "name": "Rocket_Money",
    "description": "Rocket Money finance",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 141,
    "name": "Acorns",
    "description": "Acorns investment",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 142,
    "name": "Wells_Fargo",
    "description": "Wells Fargo banking",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 143,
    "name": "Bank_of_America",
    "description": "Bank of America banking",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 144,
    "name": "Western_Union",
    "description": "Western Union transfers",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 145,
    "name": "Zelle",
    "description": "Zelle payments",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 146,
    "name": "Plaid",
    "description": "Plaid financial data",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 147,
    "name": "SquareUp",
    "description": "Square payment processing",
    "type": "file",
    "parentId": 136
  },
  {
    "id": 148,
    "name": "Shopping_Rewards",
    "description": "Shopping and rewards apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 149,
    "name": "Retail",
    "description": "Retail shopping apps",
    "type": "folder",
    "parentId": 148
  },
  {
    "id": 150,
    "name": "Amazon",
    "description": "Amazon shopping",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 151,
    "name": "Walmart",
    "description": "Walmart shopping",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 152,
    "name": "Target",
    "description": "Target shopping",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 153,
    "name": "Lowes",
    "description": "Lowe's home improvement",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 154,
    "name": "Home_Depot",
    "description": "Home Depot",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 155,
    "name": "Office_Depot",
    "description": "Office Depot",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 156,
    "name": "eBay",
    "description": "eBay marketplace",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 157,
    "name": "Temu",
    "description": "Temu shopping",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 158,
    "name": "Etsy",
    "description": "Etsy marketplace",
    "type": "file",
    "parentId": 149
  },
  {
    "id": 159,
    "name": "Food_Coffee",
    "description": "Food and coffee apps",
    "type": "folder",
    "parentId": 148
  },
  {
    "id": 160,
    "name": "Chick_fil_A",
    "description": "Chick-fil-A app",
    "type": "file",
    "parentId": 159
  },
  {
    "id": 161,
    "name": "Dutch_Bros",
    "description": "Dutch Bros coffee",
    "type": "file",
    "parentId": 159
  },
  {
    "id": 162,
    "name": "Starbucks",
    "description": "Starbucks coffee",
    "type": "file",
    "parentId": 159
  },
  {
    "id": 163,
    "name": "DoorDash",
    "description": "DoorDash food delivery",
    "type": "file",
    "parentId": 159
  },
  {
    "id": 164,
    "name": "Uber_Eats",
    "description": "Uber Eats delivery",
    "type": "file",
    "parentId": 159
  },
  {
    "id": 165,
    "name": "Shipping_Tracking",
    "description": "Shipping and tracking apps",
    "type": "folder",
    "parentId": 148
  },
  {
    "id": 166,
    "name": "UPS",
    "description": "UPS shipping",
    "type": "file",
    "parentId": 165
  },
  {
    "id": 167,
    "name": "FedEx",
    "description": "FedEx shipping",
    "type": "file",
    "parentId": 165
  },
  {
    "id": 168,
    "name": "USPS_Mobile",
    "description": "USPS Mobile",
    "type": "file",
    "parentId": 165
  },
  {
    "id": 169,
    "name": "Navigation_Travel",
    "description": "Navigation and travel apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 170,
    "name": "Maps_Transport",
    "description": "Maps and transportation",
    "type": "folder",
    "parentId": 169
  },
  {
    "id": 171,
    "name": "Google_Maps",
    "description": "Google Maps",
    "type": "file",
    "parentId": 170
  },
  {
    "id": 172,
    "name": "Apple_Maps",
    "description": "Apple Maps",
    "type": "file",
    "parentId": 170
  },
  {
    "id": 173,
    "name": "Yandex_Maps",
    "description": "Yandex Maps",
    "type": "file",
    "parentId": 170
  },
  {
    "id": 174,
    "name": "ParkMobile",
    "description": "ParkMobile parking",
    "type": "file",
    "parentId": 170
  },
  {
    "id": 175,
    "name": "Uber",
    "description": "Uber rideshare",
    "type": "file",
    "parentId": 170
  },
  {
    "id": 176,
    "name": "Lyft",
    "description": "Lyft rideshare",
    "type": "file",
    "parentId": 170
  },
  {
    "id": 177,
    "name": "Housing_Weather",
    "description": "Housing and weather apps",
    "type": "folder",
    "parentId": 169
  },
  {
    "id": 178,
    "name": "Apartments_App",
    "description": "Apartments.com app",
    "type": "file",
    "parentId": 177
  },
  {
    "id": 179,
    "name": "Weather",
    "description": "Weather applications",
    "type": "file",
    "parentId": 177
  },
  {
    "id": 180,
    "name": "Health_Fitness",
    "description": "Health and fitness apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 181,
    "name": "MyChart_App",
    "description": "MyChart health portal",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 182,
    "name": "BetterSleep_App",
    "description": "BetterSleep app",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 183,
    "name": "PT_Solutions_App",
    "description": "PT Solutions",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 184,
    "name": "Noji",
    "description": "Noji health app",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 185,
    "name": "Healow_App",
    "description": "Healow health app",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 186,
    "name": "Life_Time_App",
    "description": "Life Time fitness",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 187,
    "name": "Weight_Gurus",
    "description": "Weight Gurus",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 188,
    "name": "Go_Kinetic",
    "description": "Go Kinetic fitness",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 189,
    "name": "Elevate",
    "description": "Elevate brain training",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 190,
    "name": "Think_Dirty",
    "description": "Think Dirty product scanner",
    "type": "file",
    "parentId": 180
  },
  {
    "id": 191,
    "name": "Learning_Self_Improvement",
    "description": "Learning and self-improvement apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 192,
    "name": "Duolingo",
    "description": "Duolingo language learning",
    "type": "file",
    "parentId": 191
  },
  {
    "id": 193,
    "name": "Mimo",
    "description": "Mimo coding app",
    "type": "file",
    "parentId": 191
  },
  {
    "id": 194,
    "name": "Brilliant",
    "description": "Brilliant learning platform",
    "type": "file",
    "parentId": 191
  },
  {
    "id": 195,
    "name": "Quizgecko",
    "description": "Quizgecko quiz platform",
    "type": "file",
    "parentId": 191
  },
  {
    "id": 196,
    "name": "Information_Reading",
    "description": "Information and reading apps",
    "type": "file",
    "parentId": 191
  },
  {
    "id": 197,
    "name": "Entertainment_Media",
    "description": "Entertainment and media apps",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 198,
    "name": "Streaming",
    "description": "Streaming services",
    "type": "folder",
    "parentId": 197
  },
  {
    "id": 199,
    "name": "Netflix",
    "description": "Netflix streaming",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 200,
    "name": "Hulu",
    "description": "Hulu streaming",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 201,
    "name": "Max",
    "description": "Max streaming",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 202,
    "name": "Prime_Video",
    "description": "Prime Video streaming",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 203,
    "name": "Disney_Plus",
    "description": "Disney Plus streaming",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 204,
    "name": "Crunchyroll",
    "description": "Crunchyroll anime",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 205,
    "name": "YouTube_App",
    "description": "YouTube streaming",
    "type": "file",
    "parentId": 198
  },
  {
    "id": 206,
    "name": "Devices_Control",
    "description": "Device control apps",
    "type": "folder",
    "parentId": 197
  },
  {
    "id": 207,
    "name": "VIZIO",
    "description": "VIZIO TV control",
    "type": "file",
    "parentId": 206
  },
  {
    "id": 208,
    "name": "Apple_TV_Remote",
    "description": "Apple TV Remote",
    "type": "file",
    "parentId": 206
  },
  {
    "id": 209,
    "name": "AI_Knowledge_Tools",
    "description": "AI and knowledge tools",
    "type": "folder",
    "parentId": 90
  },
  {
    "id": 210,
    "name": "ChatGPT",
    "description": "ChatGPT AI assistant",
    "type": "file",
    "parentId": 209
  },
  {
    "id": 211,
    "name": "Claude",
    "description": "Claude AI assistant",
    "type": "file",
    "parentId": 209
  },
  {
    "id": 212,
    "name": "Perplexity",
    "description": "Perplexity AI search",
    "type": "file",
    "parentId": 209
  },
  {
    "id": 213,
    "name": "Rewind",
    "description": "Rewind AI recorder",
    "type": "file",
    "parentId": 209
  },
  {
    "id": 214,
    "name": "Financial",
    "description": "Personal financial management",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 215,
    "name": "Accounts_Banking",
    "description": "Banking and credit card accounts",
    "type": "folder",
    "parentId": 214
  },
  {
    "id": 216,
    "name": "Bank_of_America_Fin",
    "description": "Bank of America accounts",
    "type": "folder",
    "parentId": 215
  },
  {
    "id": 221,
    "name": "Assets_Inventory",
    "description": "Personal assets and inventory",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 222,
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "type": "folder",
    "parentId": 221
  },
  {
    "id": 223,
    "name": "MacBook",
    "description": "MacBook computer",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 224,
    "name": "iPhone15",
    "description": "iPhone 15",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 225,
    "name": "Apple_Watch",
    "description": "Apple Watch",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 226,
    "name": "LG_34_Monitor",
    "description": "LG 34-inch monitor",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 227,
    "name": "ZMUIPNG_Hub",
    "description": "ZMUIPNG hub",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 228,
    "name": "Tile",
    "description": "Tile tracking device",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 229,
    "name": "iXpand",
    "description": "iXpand device",
    "type": "file",
    "parentId": 222
  },
  {
    "id": 230,
    "name": "Home_Storage",
    "description": "Home storage and furniture",
    "type": "folder",
    "parentId": 221
  },
  {
    "id": 231,
    "name": "Furniture",
    "description": "Home furniture",
    "type": "file",
    "parentId": 230
  },
  {
    "id": 232,
    "name": "Decor",
    "description": "Home decorations",
    "type": "file",
    "parentId": 230
  },
  {
    "id": 233,
    "name": "Event_Decor",
    "description": "Event decorations",
    "type": "file",
    "parentId": 230
  },
  {
    "id": 234,
    "name": "Home_Tools",
    "description": "Home tools",
    "type": "file",
    "parentId": 230
  },
  {
    "id": 235,
    "name": "Christmas_Items",
    "description": "Christmas decorations and items",
    "type": "file",
    "parentId": 230
  },
  {
    "id": 236,
    "name": "Sell_List",
    "description": "Items to sell",
    "type": "folder",
    "parentId": 221
  },
  {
    "id": 237,
    "name": "AirPods",
    "description": "AirPods for sale",
    "type": "file",
    "parentId": 236
  },
  {
    "id": 238,
    "name": "Dyson_Vacuum",
    "description": "Dyson vacuum for sale",
    "type": "file",
    "parentId": 236
  },
  {
    "id": 239,
    "name": "Mirrors",
    "description": "Mirrors for sale",
    "type": "file",
    "parentId": 236
  },
  {
    "id": 240,
    "name": "Lights",
    "description": "Lights for sale",
    "type": "file",
    "parentId": 236
  },
  {
    "id": 241,
    "name": "Hats",
    "description": "Hats for sale",
    "type": "file",
    "parentId": 236
  },
  {
    "id": 242,
    "name": "Shoes",
    "description": "Shoes for sale",
    "type": "file",
    "parentId": 236
  },
  {
    "id": 243,
    "name": "Timeline",
    "description": "Life events and timeline",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 244,
    "name": "Event_Summaries",
    "description": "Major life event summaries",
    "type": "folder",
    "parentId": 243
  },
  {
    "id": 245,
    "name": "Move_NYC_Baltimore_2018",
    "description": "Move from NYC to Baltimore 2018",
    "type": "file",
    "parentId": 244
  },
  {
    "id": 246,
    "name": "Job_BloodCenter_2019",
    "description": "Blood Center job 2019",
    "type": "file",
    "parentId": 244
  },
  {
    "id": 247,
    "name": "Eid_2021",
    "description": "Eid celebration 2021",
    "type": "file",
    "parentId": 244
  },
  {
    "id": 248,
    "name": "Car_Accident_2023",
    "description": "Car accident 2023",
    "type": "file",
    "parentId": 244
  },
  {
    "id": 249,
    "name": "Travel",
    "description": "Travel records and accounts",
    "type": "folder",
    "parentId": 243
  },
  {
    "id": 250,
    "name": "Emirates",
    "description": "Emirates airline",
    "type": "file",
    "parentId": 249
  },
  {
    "id": 251,
    "name": "Delta",
    "description": "Delta airline",
    "type": "file",
    "parentId": 249
  },
  {
    "id": 252,
    "name": "United",
    "description": "United airline",
    "type": "file",
    "parentId": 249
  },
  {
    "id": 253,
    "name": "Airbnb",
    "description": "Airbnb bookings",
    "type": "file",
    "parentId": 249
  },
  {
    "id": 254,
    "name": "Incidents",
    "description": "Incident reports",
    "type": "folder",
    "parentId": 243
  },
  {
    "id": 255,
    "name": "Car_Accident_Aqsa_2022",
    "description": "Car accident with Aqsa 2022",
    "type": "file",
    "parentId": 254
  },
  {
    "id": 256,
    "name": "Daily_Life_Digital_Presence",
    "description": "Digital accounts and daily life",
    "type": "folder",
    "parentId": 1
  },
  {
    "id": 257,
    "name": "Routines_Preferences",
    "description": "Daily routines and preferences",
    "type": "folder",
    "parentId": 256
  },
  {
    "id": 258,
    "name": "Notes_Routines",
    "description": "Routine and preference notes",
    "type": "file",
    "parentId": 257
  },
  {
    "id": 259,
    "name": "Email_Accounts",
    "description": "Email account management",
    "type": "folder",
    "parentId": 256
  },
  {
    "id": 260,
    "name": "Apple_IDs",
    "description": "Apple ID accounts",
    "type": "folder",
    "parentId": 259
  },
  {
    "id": 261,
    "name": "Zainkhan5@yahoo.com",
    "description": "Primary Yahoo email",
    "type": "file",
    "parentId": 260
  },
  {
    "id": 262,
    "name": "Other_IDs",
    "description": "Other Apple IDs",
    "type": "file",
    "parentId": 260
  },
  {
    "id": 263,
    "name": "Gmail",
    "description": "Gmail account",
    "type": "file",
    "parentId": 259
  },
  {
    "id": 264,
    "name": "Outlook",
    "description": "Outlook account",
    "type": "file",
    "parentId": 259
  },
  {
    "id": 265,
    "name": "Yahoo",
    "description": "Yahoo email account",
    "type": "file",
    "parentId": 259
  },
  {
    "id": 266,
    "name": "Social_Media_Accts",
    "description": "Social media accounts",
    "type": "folder",
    "parentId": 256
  },
  {
    "id": 267,
    "name": "Instagram_Acct",
    "description": "Instagram account",
    "type": "folder",
    "parentId": 266
  },
  {
    "id": 268,
    "name": "Credentials_Insta",
    "description": "Instagram credentials",
    "type": "file",
    "parentId": 267
  },
  {
    "id": 269,
    "name": "TikTok_Acct",
    "description": "TikTok account",
    "type": "folder",
    "parentId": 266
  },
  {
    "id": 270,
    "name": "Credentials_TikTok",
    "description": "TikTok credentials",
    "type": "file",
    "parentId": 269
  },
  {
    "id": 271,
    "name": "Facebook_Acct",
    "description": "Facebook account",
    "type": "file",
    "parentId": 266
  },
  {
    "id": 272,
    "name": "LinkedIn_Acct",
    "description": "LinkedIn account",
    "type": "file",
    "parentId": 266
  },
  {
    "id": 273,
    "name": "Snapchat_Acct",
    "description": "Snapchat account",
    "type": "file",
    "parentId": 266
  },
  {
    "id": 274,
    "name": "Shopping_Accts",
    "description": "Shopping accounts",
    "type": "folder",
    "parentId": 256
  },
  {
    "id": 275,
    "name": "Amazon_Acct",
    "description": "Amazon account",
    "type": "file",
    "parentId": 274
  },
  {
    "id": 276,
    "name": "Walmart_Acct",
    "description": "Walmart account",
    "type": "file",
    "parentId": 274
  },
  {
    "id": 277,
    "name": "Target_Acct",
    "description": "Target account",
    "type": "file",
    "parentId": 274
  },
  {
    "id": 278,
    "name": "BestBuy",
    "description": "Best Buy account",
    "type": "file",
    "parentId": 274
  },
  {
    "id": 279,
    "name": "Costco",
    "description": "Costco account",
    "type": "file",
    "parentId": 274
  },
  {
    "id": 280,
    "name": "Entertainment_Subs",
    "description": "Entertainment subscriptions",
    "type": "folder",
    "parentId": 256
  },
  {
    "id": 281,
    "name": "AMC",
    "description": "AMC Theaters",
    "type": "file",
    "parentId": 280
  },
  {
    "id": 282,
    "name": "Netflix_Sub",
    "description": "Netflix subscription",
    "type": "file",
    "parentId": 280
  },
  {
    "id": 283,
    "name": "Hulu_Sub",
    "description": "Hulu subscription",
    "type": "file",
    "parentId": 280
  },
  {
    "id": 284,
    "name": "Crunchyroll_Sub",
    "description": "Crunchyroll subscription",
    "type": "file",
    "parentId": 280
  },
  {
    "id": 285,
    "name": "Disney_Sub",
    "description": "Disney Plus subscription",
    "type": "file",
    "parentId": 280
  },
  {
    "id": 286,
    "name": "HBO_Max_Sub",
    "description": "HBO Max subscription",
    "type": "file",
    "parentId": 280
  },
  {
    "id": 800,
    "name": "Checking",
    "description": "Bank of America checking account details",
    "type": "folder",
    "parentId": 216
  },
  {
    "id": 801,
    "name": "Account Number – •••6820",
    "description": "",
    "type": "file",
    "parentId": 800
  },
  {
    "id": 802,
    "name": "Routing Numbers",
    "description": "Bank of America routing numbers",
    "type": "folder",
    "parentId": 800
  },
  {
    "id": 803,
    "name": "Electronic Transfers – 111000025",
    "description": "",
    "type": "file",
    "parentId": 802
  },
  {
    "id": 804,
    "name": "Checks – 113000023",
    "description": "",
    "type": "file",
    "parentId": 802
  },
  {
    "id": 805,
    "name": "Wire Transfers – 026009593",
    "description": "",
    "type": "file",
    "parentId": 802
  },
  {
    "id": 806,
    "name": "Status – Active",
    "description": "",
    "type": "file",
    "parentId": 800
  },
  {
    "id": 807,
    "name": "Credit Cards",
    "description": "Bank of America credit card details",
    "type": "folder",
    "parentId": 216
  },
  {
    "id": 808,
    "name": "Visa •••2328",
    "description": "",
    "type": "file",
    "parentId": 807
  },
  {
    "id": 809,
    "name": "Limit – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 807
  },
  {
    "id": 810,
    "name": "Balance – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 807
  },
  {
    "id": 811,
    "name": "Payment Due Date – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 807
  },
  {
    "id": 812,
    "name": "Notes",
    "description": "Notes for Bank of America",
    "type": "folder",
    "parentId": 216
  },
  {
    "id": 813,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 812
  },
  {
    "id": 814,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 812
  },
  {
    "id": 815,
    "name": "Credit One Bank",
    "description": "Credit One Bank account details",
    "type": "folder",
    "parentId": 215
  },
  {
    "id": 816,
    "name": "Credit Cards",
    "description": "Credit One Bank credit cards",
    "type": "folder",
    "parentId": 815
  },
  {
    "id": 817,
    "name": "Amex •••2913",
    "description": "",
    "type": "file",
    "parentId": 816
  },
  {
    "id": 818,
    "name": "Amex •••9974",
    "description": "",
    "type": "file",
    "parentId": 816
  },
  {
    "id": 819,
    "name": "Limit – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 816
  },
  {
    "id": 820,
    "name": "Balance – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 816
  },
  {
    "id": 821,
    "name": "Payment Due Date – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 816
  },
  {
    "id": 822,
    "name": "Notes",
    "description": "Notes for Credit One Bank",
    "type": "folder",
    "parentId": 815
  },
  {
    "id": 823,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 822
  },
  {
    "id": 824,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 822
  },
  {
    "id": 825,
    "name": "Wells Fargo",
    "description": "Wells Fargo account details",
    "type": "folder",
    "parentId": 215
  },
  {
    "id": 826,
    "name": "Credit Cards",
    "description": "Wells Fargo credit cards",
    "type": "folder",
    "parentId": 825
  },
  {
    "id": 827,
    "name": "Home Furnishings •••8058",
    "description": "",
    "type": "file",
    "parentId": 826
  },
  {
    "id": 828,
    "name": "Limit – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 826
  },
  {
    "id": 829,
    "name": "Balance – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 826
  },
  {
    "id": 830,
    "name": "Payment Due Date – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 826
  },
  {
    "id": 831,
    "name": "Notes",
    "description": "Notes for Wells Fargo",
    "type": "folder",
    "parentId": 825
  },
  {
    "id": 832,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 831
  },
  {
    "id": 833,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 831
  },
  {
    "id": 834,
    "name": "Indigo Platinum",
    "description": "Indigo Platinum account details",
    "type": "folder",
    "parentId": 215
  },
  {
    "id": 835,
    "name": "Credit Cards",
    "description": "Indigo Platinum credit cards",
    "type": "folder",
    "parentId": 834
  },
  {
    "id": 836,
    "name": "Indigo Platinum Card •••6612",
    "description": "",
    "type": "file",
    "parentId": 835
  },
  {
    "id": 837,
    "name": "Limit – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 835
  },
  {
    "id": 838,
    "name": "Balance – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 835
  },
  {
    "id": 839,
    "name": "Payment Due Date – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 835
  },
  {
    "id": 840,
    "name": "Notes",
    "description": "Notes for Indigo Platinum",
    "type": "folder",
    "parentId": 834
  },
  {
    "id": 841,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 840
  },
  {
    "id": 842,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 840
  },
  {
    "id": 843,
    "name": "Investments",
    "description": "Investment accounts and platforms",
    "type": "folder",
    "parentId": 214
  },
  {
    "id": 844,
    "name": "Robinhood",
    "description": "Robinhood account details",
    "type": "folder",
    "parentId": 843
  },
  {
    "id": 845,
    "name": "Checking",
    "description": "Robinhood checking account",
    "type": "folder",
    "parentId": 844
  },
  {
    "id": 846,
    "name": "Account •••1070",
    "description": "",
    "type": "file",
    "parentId": 845
  },
  {
    "id": 847,
    "name": "Routing Number – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 845
  },
  {
    "id": 848,
    "name": "Status – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 845
  },
  {
    "id": 849,
    "name": "Brokerage",
    "description": "Robinhood brokerage account",
    "type": "folder",
    "parentId": 844
  },
  {
    "id": 850,
    "name": "Investment Account •••1802",
    "description": "",
    "type": "file",
    "parentId": 849
  },
  {
    "id": 851,
    "name": "Portfolio Value – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 849
  },
  {
    "id": 852,
    "name": "Holdings – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 849
  },
  {
    "id": 853,
    "name": "Connected Bank – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 849
  },
  {
    "id": 854,
    "name": "Notes",
    "description": "Notes for Robinhood",
    "type": "folder",
    "parentId": 844
  },
  {
    "id": 855,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 854
  },
  {
    "id": 856,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 854
  },
  {
    "id": 857,
    "name": "Acorns",
    "description": "Acorns investment account",
    "type": "folder",
    "parentId": 843
  },
  {
    "id": 858,
    "name": "Investment",
    "description": "Acorns investment details",
    "type": "folder",
    "parentId": 857
  },
  {
    "id": 859,
    "name": "Account Type – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 858
  },
  {
    "id": 860,
    "name": "Balance – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 858
  },
  {
    "id": 861,
    "name": "Goal – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 858
  },
  {
    "id": 862,
    "name": "Recurring Amount – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 858
  },
  {
    "id": 863,
    "name": "Notes",
    "description": "Notes for Acorns",
    "type": "folder",
    "parentId": 857
  },
  {
    "id": 864,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 863
  },
  {
    "id": 865,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 863
  },
  {
    "id": 866,
    "name": "Apple Credit",
    "description": "Apple Credit account details",
    "type": "folder",
    "parentId": 215
  },
  {
    "id": 867,
    "name": "Credit Cards",
    "description": "Apple credit cards",
    "type": "folder",
    "parentId": 866
  },
  {
    "id": 868,
    "name": "Apple Card – Linked to Apple Account",
    "description": "",
    "type": "file",
    "parentId": 867
  },
  {
    "id": 869,
    "name": "Limit – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 867
  },
  {
    "id": 870,
    "name": "Balance – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 867
  },
  {
    "id": 871,
    "name": "Payment Due Date – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 867
  },
  {
    "id": 872,
    "name": "Notes",
    "description": "Notes for Apple Credit",
    "type": "folder",
    "parentId": 866
  },
  {
    "id": 873,
    "name": "Login Info – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 872
  },
  {
    "id": 874,
    "name": "Last Statement – [placeholder]",
    "description": "",
    "type": "file",
    "parentId": 872
  }
];