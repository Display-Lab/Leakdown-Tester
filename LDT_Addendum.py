## Version of the Leakdown Tester
ldtVersion = "1.0.1"


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
    [7,"GLU01","2023-01-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-02-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-03-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-04-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-05-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-06-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-07-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-08-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-09-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-10-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-11-01",45,55,100,45,45,50,1],
    [7,"GLU01","2023-12-01",45,55,100,45,45,50,1]
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
        {"acceptable_by": "goal loss", "measure": "NMB03Peds"}
    ],
    7: [
        {"acceptable_by": "social better", "measure": "SUS04"},
        {"acceptable_by": "improving", "measure": "BP03"},
        {"acceptable_by": "worsening", "measure": "SUS02"},
        {"acceptable_by": "goal loss", "measure": "NMB03Peds"},
        {"acceptable_by": "goal gain", "measure": "TOC01"}
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