## Version of the Leakdown Tester
ldtVersion = "1.3.0"


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
    [6,"NMB03","2023-01-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-02-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-03-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-04-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-05-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-06-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-07-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-08-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-09-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-10-01",90,10,100,90,92,96,90],
    [6,"NMB03","2023-11-01",100,0,100,90,92,96,90],
    [6,"NMB03","2023-12-01",1,1,2,90,92,96,90]
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