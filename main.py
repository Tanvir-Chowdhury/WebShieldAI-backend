from fastapi import FastAPI, Depends, HTTPException
from db import create_table, get_db
from sqlalchemy.orm import Session
import models, schemas, services
import defacement_loop 
from defacement_control import toggle_defacement
from fastapi import Request
from models import SQLLog
from ml_model import predict_query
from fastapi.responses import Response


app = FastAPI(title="WebShieldAI API")

create_table()

# defacement_loop.run_deface_loop(app)

@app.post("/users/", response_model=schemas.GetUser)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.create_user(user, db)

@app.post("/websites/", response_model=schemas.GetWebsite)
async def create_website(website: schemas.WebsiteCreate, db: Session = Depends(get_db)):
    return services.create_website(website, db)


@app.post("/predict-sqli/")
async def predict_sql_query(input: schemas.SQLQuery, db: Session = Depends(get_db)):
    return services.process_sql_query(input, db)

@app.post("/predict-dom/")
async def predict_dom_log(input: schemas.DOMLog, db: Session = Depends(get_db)):
    return services.process_dom_log(input, db)

@app.post("/websites/{website_id}/toggle-defacement/")
async def toggle_defacement_route(website_id: int, enable: bool):
    return toggle_defacement(website_id, enable)

@app.post("/collect-sqli")
async def collect_sqli(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    website_id = data.get("website_id")
    query = data.get("query")

    prediction, confidence = predict_query(query)

    log = SQLLog(
        website_id=website_id,
        query=query,
        prediction=prediction,
        score=confidence
    )
    db.add(log)
    db.commit()

    return {"status": "ok", "prediction": prediction, "confidence": confidence}


@app.get("/cdn/webshield-agent.js")
def serve_agent(request: Request):
    website_id = request.query_params.get("wid", "0")

    js_code = f"""
(function () {{
  const WEBSITE_ID = {website_id};
  const API_URL = "http://localhost:8000/collect-sqli";

  function sendSQLQuery(value, callback) {{
    fetch(API_URL, {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{
        website_id: WEBSITE_ID,
        query: value
      }}),
    }})
    .then(res => res.json())
    .then(data => {{
      console.log("Sending SQL query:", value);
      console.log("Prediction:", data);
      if (data.prediction === "malicious") {{
        alert("SQL Injection attempt detected!");
      }}
      callback(null, data);  // ✅ Call the callback with result
    }})
    .catch(err => {{
      console.error("Error:", err);
      callback(err, null);  // ✅ Handle errors
    }});
  }}

  document.addEventListener("DOMContentLoaded", function () {{
    const inputs = document.getElementsByTagName("input");
    const submitButton = document.querySelector("button[type='submit'], input[type='submit']");

    if (submitButton) {{
      submitButton.addEventListener("click", function (e) {{
        e.preventDefault(); 

        const valuesToCheck = [];
        for (let i = 0; i < inputs.length; i++) {{
          const val = inputs[i].value.trim();
          
          if (val.endsWith("@gmail.com") || val.endsWith("@yahoo.com") || val.endsWith("@hotmail.com")) {{
            console.warn("Skipping email input:", val);
            continue;  
          }}
          if (val !== "") {{
            valuesToCheck.push(val);
          }}
        }}

        if (valuesToCheck.length === 0) {{
          e.target.form.submit();
          return;
        }}

        let completed = 0;
        let maliciousDetected = false;

        function checkAndSubmit() {{
          completed++;
          if (completed === valuesToCheck.length) {{
            if (!maliciousDetected) {{
              console.log("✅ All inputs are clean. Submitting form...");
              e.target.form.submit();  // ✅ Now form will submit
            }} else {{
              console.warn("🚫 Malicious input detected. Form blocked.");
            }}
          }}
        }}

        for (let i = 0; i < valuesToCheck.length; i++) {{
          sendSQLQuery(valuesToCheck[i], function(err, data) {{
            if (err || (data.prediction && data.prediction === "malicious")) {{
              maliciousDetected = true;
            }}
            checkAndSubmit();
          }});
        }}
      }});
    }}
  }});

  const queryString = window.location.search;
  DqueryString = decodeURIComponent(queryString.substring(1));
  if (queryString) {{
    sendSQLQuery(DqueryString, function(err, data) {{
      if (!err && data.prediction === "malicious") {{
          alert("Malicious query detected in URL. Redirecting to home page.");
          window.location.href = "/";
        }}
    }});
  }}

  console.log("WebShield Agent active for Website ID:", WEBSITE_ID);
}})();
"""



    return Response(content=js_code, media_type="application/javascript")


@app.get("/cdn/dom-agent.js")
def serve_dom_agent(request: Request):
    website_id = request.query_params.get("wid", "0")

    js_code = f"""
    (function () {{
      const WEBSITE_ID = {website_id};
      const API_URL = "http://localhost:29900/predict-dom";

      function summarizeMutations(mutationsList) {{
        const summary = new Set();
        mutationsList.forEach(mutation => {{
          let type = mutation.type;
          let tag = (mutation.target && mutation.target.tagName) || "UNKNOWN";
          summary.add(`${{type}}:${{tag}}`);
        }});
        return Array.from(summary).join("|");
      }}

      const observer = new MutationObserver((mutationsList) => {{
        const summary = summarizeMutations(mutationsList);

        fetch(API_URL, {{
          method: "POST",
          headers: {{
            "Content-Type": "application/json"
          }},
          body: JSON.stringify({{
            website_id: WEBSITE_ID,
            mutations: summary
          }})
        }})
        .then(res => res.json())
        .then(data => {{
          if (data.prediction === "manipulated") {{
            console.warn("Suspicious DOM manipulation detected!");
          }}
        }})
        .catch(err => console.error("DOM logging error:", err));
      }});

      observer.observe(document.body, {{
        attributes: true,
        childList: true,
        subtree: true,
        characterData: true
      }});

      console.log("DOM Agent running for Website ID:", WEBSITE_ID);
    }})();
    """

    return Response(content=js_code, media_type="application/javascript")
