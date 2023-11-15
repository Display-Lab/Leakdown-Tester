## Version of the Leakdown Tester
ldtVersion = "1.2.1"


## JSON content 'header' wrapper section for in-situ payload compilation:
payloadHeader = '''
{
  "@context": {
    "@vocab": "http://schema.org/",
    "slowmo": "http://example.com/slowmo#",
    "csvw": "http://www.w3.org/ns/csvw#",
    "dc": "http://purl.org/dc/terms/",
    "psdo": "http://purl.obolibrary.org/obo/",
    "slowmo:Measure": "http://example.com/slowmo#Measure",
    "slowmo:IsAboutPerformer": "http://example.com/slowmo#IsAboutPerformer",
    "slowmo:ColumnUse": "http://example.com/slowmo#ColumnUse",
    "slowmo:IsAboutTemplate": "http://example.com/slowmo#IsAboutTemplate",
    "slowmo:spek": "http://example.com/slowmo#spek",
    "slowmo:IsAboutCausalPathway": "http://example.com/slowmo#IsAboutCausalPathway",
    "slowmo:IsAboutOrganization": "http://example.com/slowmo#IsAboutOrganization",
    "slowmo:IsAboutMeasure": "http://example.com/slowmo#IsAboutMeasure",
    "slowmo:InputTable": "http://example.com/slowmo#InputTable",
    "slowmo:WithComparator": "http://example.com/slowmo#WithComparator",
    "has_part": "http://purl.obolibrary.org/obo/bfo#BFO_0000051",
    "has_disposition": "http://purl.obolibrary.org/obo/RO_0000091"
  },
  "Performance_data":[
    ["staff_number","measure","month","passed_count","flagged_count","denominator","peer_average_comparator","peer_90th_percentile_benchmark","peer_75th_percentile_benchmark","MPOG_goal"],
'''
## Direct ref performance data for individual tweaks
postwoman = '''
    [1, "BP01", "2022-12-01", 19, 0, 19, 83.0, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-01-01", 46, 0, 46, 83.0, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-02-01", 58, 0, 58, 83.3, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-03-01", 68, 0, 68, 83.6, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-04-01", 49, 0, 49, 84.7, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-05-01", 96, 0, 96, 84.5, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-06-01", 91, 0, 91, 84.8, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-07-01", 74, 0, 74, 84.6, 100.0, 100.0, 90.0],
    [1, "BP01", "2023-08-01", 41, 1, 42, 84.9, 100.0, 100.0, 90.0],
    [1, "BP02", "2022-12-01", 19, 0, 19, 83.0, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-01-01", 45, 1, 46, 83.0, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-02-01", 56, 3, 59, 83.3, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-03-01", 67, 1, 68, 83.6, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-04-01", 46, 1, 47, 84.7, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-05-01", 90, 4, 94, 84.5, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-06-01", 91, 1, 92, 84.8, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-07-01", 76, 0, 76, 84.6, 100.0, 100.0, 90.0],
    [1, "BP02", "2023-08-01", 41, 3, 44, 84.9, 100.0, 100.0, 90.0],
    [1, "GLU03", "2023-03-01", 2, 0, 2, 83.6, 100.0, 100.0, 90.0],
    [1, "GLU03", "2023-04-01", 0, 1, 1, 84.7, 100.0, 100.0, 90.0],
    [1, "GLU03", "2023-05-01", 3, 0, 3, 84.5, 100.0, 100.0, 90.0],
    [1, "GLU03", "2023-06-01", 1, 0, 1, 84.8, 100.0, 100.0, 90.0],
    [1, "GLU03", "2023-07-01", 1, 0, 1, 84.6, 100.0, 100.0, 90.0],
    [1, "GLU03", "2023-08-01", 2, 0, 2, 84.9, 100.0, 100.0, 90.0],
    [1, "GLU11", "2023-03-01", 1, 0, 1, 83.6, 100.0, 100.0, 90.0],
    [1, "GLU11", "2023-04-01", 0, 1, 1, 84.7, 100.0, 100.0, 90.0],
    [1, "GLU11", "2023-05-01", 1, 3, 4, 84.5, 100.0, 100.0, 90.0],
    [1, "GLU11", "2023-06-01", 1, 0, 1, 84.8, 100.0, 100.0, 90.0],
    [1, "GLU11", "2023-07-01", 1, 0, 1, 84.6, 100.0, 100.0, 90.0],
    [1, "GLU11", "2023-08-01", 2, 0, 2, 84.9, 100.0, 100.0, 90.0],
    [1, "NMB02", "2022-12-01", 7, 0, 7, 83.0, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-01-01", 14, 0, 14, 83.0, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-02-01", 27, 0, 27, 83.3, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-03-01", 12, 0, 12, 83.6, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-04-01", 10, 0, 10, 84.7, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-05-01", 17, 0, 17, 84.5, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-06-01", 23, 0, 23, 84.8, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-07-01", 16, 2, 18, 84.6, 100.0, 100.0, 90.0],
    [1, "NMB02", "2023-08-01", 5, 1, 6, 84.9, 100.0, 100.0, 90.0],
    [1, "PONV05", "2022-12-01", 10, 1, 11, 83.0, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-01-01", 20, 1, 21, 83.0, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-02-01", 13, 4, 17, 83.3, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-03-01", 9, 2, 11, 83.6, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-04-01", 4, 0, 4, 84.7, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-05-01", 2, 8, 10, 84.5, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-06-01", 7, 5, 12, 84.8, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-07-01", 4, 3, 7, 84.6, 100.0, 100.0, 90.0],
    [1, "PONV05", "2023-08-01", 3, 7, 10, 84.9, 100.0, 100.0, 90.0],
    [1, "PUL01", "2022-12-01", 9, 0, 9, 83.0, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-01-01", 18, 0, 18, 83.0, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-02-01", 22, 0, 22, 83.3, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-03-01", 11, 2, 13, 83.6, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-04-01", 4, 0, 4, 84.7, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-05-01", 12, 1, 13, 84.5, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-06-01", 19, 0, 19, 84.8, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-07-01", 10, 0, 10, 84.6, 100.0, 100.0, 90.0],
    [1, "PUL01", "2023-08-01", 7, 0, 7, 84.9, 100.0, 100.0, 90.0],
    [1, "SUS02", "2022-12-01", 8, 7, 15, 83.0, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-01-01", 22, 8, 30, 83.0, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-02-01", 27, 11, 38, 83.3, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-03-01", 34, 10, 44, 83.6, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-04-01", 22, 6, 28, 84.7, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-05-01", 45, 14, 59, 84.5, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-06-01", 61, 12, 73, 84.8, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-07-01", 38, 9, 47, 84.6, 100.0, 100.0, 90.0],
    [1, "SUS02", "2023-08-01", 21, 7, 28, 84.9, 100.0, 100.0, 90.0]
'''

## JSON content 'footer' wrapper section for in-situ payload compilation:
payloadFooter = '''
  ],
  "History":{
  },
  "Preferences":{
    "Utilities": {
    "Message_Format": 
      {
        "1": "0.0",
        "2": "0.1",
        "16": "7.5",
        "24": "9.4",
        "18": "11.3",
        "11": "13.2",
        "22": "15.1" ,
        "14": "22.6" ,
        "21": "62.3" ,
        "5":"0.2",
        "15":"4.0",
        "4":"0.9"
      },
    "Display_Format":
      {
        "short_sentence_with_no_chart": "0.0",
        "bar": "37.0",
        "line": "0.0"
      }
  }
}
}
'''


## Dictionary of vignette-determined persona, measure, and causal pathway pairings:
vignAccPairs = {
    1: [
        {"acceptable_by": "social loss", "measure": "PONV05"},
        {"acceptable_by": "social better", "measure": "SUS04"},
        {"acceptable_by": "goal approach", "measure": "GLU03"}
    ],
    2: [
        {"acceptable_by": "social loss", "measure": "PONV05"},
        {"acceptable_by": "social approach", "measure": "TOC02"}
    ],
    3: [
        {"acceptable_by": "social gain", "measure": "PUL01"},
        {"acceptable_by": "goal approach", "measure": "GLU03"}
    ],
    4: [
        {"acceptable_by": "social worse", "measure": "GLU01"},
        {"acceptable_by": "social approach", "measure": "TOC02"},
        {"acceptable_by": "improving", "measure": "BP03"}
    ],
    5: [
        {"acceptable_by": "social worse", "measure": "GLU01"},
        {"acceptable_by": "goal gain", "measure": "TOC01"}
    ],
    6: [
        {"acceptable_by": "social gain", "measure": "PUL01"},
        {"acceptable_by": "worsening", "measure": "SUS02"},
        {"acceptable_by": "goal loss", "measure": "NMB03"}
    ],
    7: [
        {"acceptable_by": "social better", "measure": "SUS04"},
        {"acceptable_by": "improving", "measure": "BP03"},
        {"acceptable_by": "worsening", "measure": "SUS02"},
        {"acceptable_by": "goal loss", "measure": "NMB03"},
        {"acceptable_by": "goal gain", "measure": "TOC01"}
    ]
}

pilotPairs = {
    1: [
        {"acceptable_by": "social worse", "measure": "PONV05"}, # to 75th
        {"acceptable_by": "social better", "measure": "SUS04"}, # to 90th
        {"acceptable_by": "social worse", "measure": "GLU03"}   # to 50th
    ],
    2: [
        {"acceptable_by": "social worse", "measure": "PONV05"}, # to 50th
        {"acceptable_by": "social worse", "measure": "TOC02"}   # to 75th
    ],
    3: [
        {"acceptable_by": "social better", "measure": "PUL01"}, # to 75th
        {"acceptable_by": "social worse", "measure": "GLU03"}   # to 75th
    ],
    4: [
        {"acceptable_by": "social worse", "measure": "GLU01"},  # to 90th
        {"acceptable_by": "social worse", "measure": "TOC02"},  # to 90th
        {"acceptable_by": "social better", "measure": "BP03"}   # to 75th
    ],
    5: [
        {"acceptable_by": "social worse", "measure": "GLU01"},  # to 50th
        {"acceptable_by": "social better", "measure": "TOC01"}  # to 75th
    ],
    6: [
        {"acceptable_by": "social better", "measure": "PUL01"}, # to 90th
        {"acceptable_by": "social better", "measure": "SUS02"}, # to 75th
        {"acceptable_by": "social worse", "measure": "NMB03"}   # to 50th
    ],
    7: [
        {"acceptable_by": "social better", "measure": "SUS04"}, # to 50th
        {"acceptable_by": "social better", "measure": "BP03"},  # to 75th
        {"acceptable_by": "social worse", "measure": "SUS02"},  # to 50th
        {"acceptable_by": "social worse", "measure": "NMB03"},  # to 50th
        {"acceptable_by": "social worse", "measure": "TOC01"}   # to 90th
    ]
}

## Repo Testing dictionaries:
hitlistIM = ["alice", "bob", "chikondi", "deepa", "eugene", "fahad", "gaile"]

hitlistCP = ["goal_approach",
"goal_gain",
"goal_loss",
"improving",
"social_approach",
"social_better",
"social_gain",
"social_loss",
"social_worse",
"worsening"
]