{ 
  "dataset": {
    "name": "epsrc-gotw",
    "label": "EPSRC Grants on the Web", 
    "description": "<p>This dataset will eventually be a complete scrape of the <a href=\"http://www.epsrc.ac.uk/\">Engineering and Physical Sciences Research Council</a>'s <a href=\"http://gow.epsrc.ac.uk/\">Grants on the Web</a>, providing information on public money granted to scientists for work in fields ranging from mathematics to materials science, and from information technology to structural engineering.</p> <p>Currently, it contains EPSRC past grants data (i.e. grants that have completed) from 1985 through to 2010. At last count, this included nearly 36,000 grants, totalling over £6B of funding.</p> <p>The dataset includes not only basic information about grants and the institutions and departments to which they were granted, but also industrial sector and research area classifications, as well as information on co-investigators and related grants.</p> <p>Please also note that the license terms of this data are  unclear, and as such this dataset should not currently be considered \"open data\".</p>",
    "currency": "GBP",
    "entry_custom_html": "<h3>This grant elsewhere on the web:</h3><ul><li><a href=\"http://gow.epsrc.ac.uk/ViewGrant.aspx?GrantRef=${entry['grant_reference']['label']}\">${entry['grant_reference']['label']} on <abbr title=\"Engineering and Physical Sciences Research Council\">EPSRC</abbr> Grants on the Web</a></li><li><a href=\"http://www.google.co.uk/search?q=&quot;${entry['grant_reference']['label']}&quot;\">Search for ${entry['grant_reference']['label']} on Google</a></li></ul>",
    "unique_keys": ["grant_reference.label"]                                                                                                                    
  },
  "mapping": {
    "from": {
      "type": "entity",
      "fields": [
        {"constant": "EPSRC", "datatype": "constant", "name": "label"},
        {"constant": "The UK's Engineering and Physical Sciences Research Council", "datatype": "constant", "name": "description"}
      ],
      "description": "Body awarding the grant",
      "label": "Spender"
    },
    "to": {
      "type": "entity",
      "fields": [
        {"column": "recipient_id", "datatype": "id", "name": "name"},
        {"column": "recipient_name", "datatype": "string", "name": "label"},
        {"constant": "true", "datatype": "constant", "name": "epsrc-principal-investigator"}
      ],
      "description": "The recipient of the grant.",
      "label": "Recipient"
    },
    "grant_reference": {
      "label": "Grant reference",
      "description": "Reference number assigned by EPSRC that uniquely identifies this grant.",
      "fields": [
        { "column": "grant_reference", "datatype": "string", "name": "label" }
      ],
      "type": "classifier",
      "taxonomy": "epsrc-gotw:epsrc-internal:grant-reference"
    },
    "amount": {
      "column": "amount",
      "label": "",
      "description": "",
      "datatype": "float",
      "type": "value"
    },
    "grant_title": {
      "column": "grant_title",
      "label": "Grant title",
      "description": "",
      "datatype": "string",
      "type": "value"   
    },
    "time": {
      "column": "start_date",
      "label": "Start date",
      "description": "",
      "datatype": "date",
      "type": "value"
    },
    "time_end": {
      "column": "end_date",
      "label": "End date",
      "description": "",
      "datatype": "date",
      "type": "value"
    },
    "grant_scheme": {
      "type": "classifier",
      "fields": [
        {"column": "grant_scheme", "datatype": "string", "name": "label"}
      ],
      "label": "Grant award scheme",
      "description": "The EPSRC scheme under which the grant was awarded.",
      "taxonomy": "epsrc-gotw:epsrc-internal:scheme"
    },
    "grant_abstract": {
      "column": "grant_abstract",
      "label": "Grant abstract",
      "description": "",
      "datatype": "string",
      "type": "value"   
    },
    "grant_final_report_summary": {
      "column": "grant_final_report_summary",
      "label": "Grant final report summary",
      "description": "",
      "datatype": "string",
      "type": "value"   
    },
    "department": {
      "type": "classifier",
      "fields": [
        {"column": "department_id", "datatype": "id", "name": "name"},
        {"column": "department_name", "datatype": "string", "name": "label"}
      ],
      "label": "Recipient department",
      "description": "The department receiving the grant within the recipient institution.",
      "taxonomy": "epsrc-gotw:recipient:department"
    },
    "institution": {
      "type": "classifier",
      "fields": [
        {"column": "institution_id", "datatype": "id", "name": "name"},
        {"column": "institution_name", "datatype": "string", "name": "label"}
      ],
      "label": "Recipient institution",
      "description": "The higher education institution receiving the grant.",
      "taxonomy": "epsrc-gotw:recipient:institution"
    }
  },
  "views": [
    {
      "entity": "dataset",
      "label": "By institution",
      "name": "default",
      "dimension": "dataset",
      "breakdown": "institution",
      "filters": {"name": "epsrc-gotw"}           
    },
    {
      "entity": "classifier",
      "label": "By department",
      "name": "default",
      "dimension": "institution",
      "breakdown": "department",
      "filters": {"taxonomy": "epsrc-gotw:recipient:institution"}           
    },   
    {
      "entity": "classifier",
      "label": "By recipient",
      "name": "default",
      "dimension": "department",
      "breakdown": "to",
      "filters": {"taxonomy": "epsrc-gotw:recipient:department"}           
    },
    {
      "entity": "entity",
      "label": "By grant",
      "name": "default",
      "dimension": "to",
      "breakdown": "grant_reference",
      "filters": {"epsrc-principal-investigator": "true"}           
    }, 
    {
      "entity": "dataset",
      "label": "By award scheme",
      "name": "scheme",
      "dimension": "dataset",
      "breakdown": "grant_scheme",
      "filters": {"name": "epsrc-gotw"}           
    }
  ]                       
}
