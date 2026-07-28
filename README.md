# ParaQuake

**Real USGS earthquake data, transparent geospatial trigger logic, and an AI-generated underwriting brief — an educational parametric NatCat demo, not an actuarial model.**

[GitHub repo](https://github.com/9117KET/paraquake) &nbsp;·&nbsp; Live demo: *deploy pending, see below* &nbsp;·&nbsp; Built by [Kinlo Ephriam Tangiri](https://www.kinloephraim.com/)

---

## What this is

Parametric (index-based) natural catastrophe insurance pays out based on a measured physical
parameter (e.g. earthquake magnitude and location) crossing a pre-agreed threshold, rather than
on a claims adjuster assessing actual damage. Real products like CCRIF SPC's sovereign
earthquake cover (which paid Haiti within days of the January 2010 quake) and the World
Bank/IBRD's Mexico FONDEN earthquake cat bonds work this way, using a "cat-in-a-circle" design:
if a big enough earthquake strikes close enough to an insured site, it pays out automatically.

**ParaQuake is a small, working demo of that idea**, built end-to-end: real hazard data, a
synthetic exposure portfolio, a hand-built geospatial trigger/payout engine, a multi-agent
LangGraph pipeline, and a GenAI-generated underwriting brief with a factuality guardrail — wired
into a Streamlit app you can actually click through.

It was built to genuinely learn and demonstrate two things I didn't have direct experience with
before: **geospatial data processing** and **NatCat (natural catastrophe) risk modelling** —
rather than just claiming interest in them.

## What it is *not*

This is an educational, portfolio-level demo, not a production actuarial model. Specifically:

- The **exposure portfolio is entirely synthetic and illustrative** — real coordinates in real
  seismically active regions, but no real insurer's policyholder data, sums insured, or trigger
  terms are used or implied.
- The **attenuation ("effective intensity") formula is a deliberately simplified, hand-picked
  shape**, not a peer-reviewed ground-motion prediction equation (GMPE). It captures the right
  qualitative behaviour (intensity falls off with log-distance and with depth) but the
  coefficients are not empirically fitted or validated against real ground-motion data. A
  production NatCat model would use a calibrated GMPE plus local soil/site amplification.
- Trigger thresholds are calibrated against this demo's own attenuation scale (see
  Methodology below), not against real regulatory or actuarial thresholds.

## Architecture

```
USGS Earthquake API ──► fetch_hazard_data ─┐
                                             ├─► compute_triggers ─► rank_and_filter ─► generate_report ─► qa_disclaimer_check
exposure_portfolio.csv ──► load_exposure ──┘         (geospatial +        (top 10 by      (Groq/Llama,        (checks disclaimer +
                                                     trigger/payout        payout)          LangChain)          grounds every EUR
                                                        engine)                                                 figure in ground truth;
                                                                                                                 retries once on failure)
```

A [LangGraph](https://github.com/langchain-ai/langgraph) state machine orchestrates six nodes.
The last edge is conditional: if the QA guardrail finds the LLM's report is missing its
mandatory limitations disclaimer, or mentions a EUR figure that doesn't match anything the risk
engine actually computed, the graph loops back to `generate_report` once with a corrective
instruction before giving up and flagging the issue in the UI. This mirrors the reliability
discipline from my B.Sc. thesis on reducing hallucinations in RAG systems: don't trust generated
text that contains numbers until you've checked it against ground truth.

## Methodology

**Hazard data**: real events from the [USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/)
(free, no authentication). One real response (the 6 Feb 2023 Türkiye–Syria sequence, 24 events)
is bundled as an offline fixture so the demo works without a live network call.

**Exposure portfolio** (`data/exposure_portfolio.csv`): 20 synthetic sites at real coordinates
across seismically active regions worldwide (Türkiye, Japan, Chile, Mexico, the Philippines, the
US West Coast, Indonesia, Nepal, Italy, New Zealand, and Haiti). Fields include location,
exposure type, a simplified construction-class vulnerability proxy (A = modern reinforced
concrete, B = mixed, C = unreinforced masonry), sum insured, and per-site parametric trigger
parameters.

**Geospatial trigger candidacy ("cat-in-a-circle")**: for every (event, site) pair, great-circle
distance is computed with a hand-implemented haversine formula. An event is only a "candidate"
for a site if it falls within that site's own `trigger_radius_km` **and** is shallower than 70km
(a well-known real qualitative fact: shallow earthquakes cause disproportionately more surface
shaking than deep ones at the same magnitude).

**Simplified attenuation**: for each candidate pair,

```
effective_intensity = magnitude - 1.5 * log10(distance_km + 1) - 0.001 * depth_km
```

This is *not* a calibrated GMPE — it's a hand-picked shape that gets the direction of every
term right (closer and shallower means higher intensity) without claiming empirical accuracy.
Because this attenuation decays fairly quickly with distance, per-site `trigger_magnitude`
values are calibrated against this formula's own output scale (roughly 3.5–5.2), not against raw
earthquake magnitudes — a real M7+ earthquake tens of kilometres away typically produces an
`effective_intensity` in the 4–6 range under this formula, not 7+.

**Payout tiers**: discrete, based on how far `effective_intensity` clears the site's
`trigger_magnitude` ("excess"):

| Excess over trigger | Tier | Payout (% of site's max cover) |
|---|---|---|
| < 0 | 0 | 0% (no payout) |
| 0.0 – 0.99 | 1 | 25% |
| 1.0 – 1.99 | 2 | 60% |
| ≥ 2.0 | 3 | 100% |

Payout is per-occurrence (the largest single triggering event in a run), not stacked across
multiple events.

**Basis risk**: because payout is driven entirely by a physical parameter, not an on-the-ground
loss assessment, a real parametric cover can pay out more or less than actual damage. This is a
known, accepted trade-off in the real product, made deliberately in exchange for fast,
unambiguous, dispute-free claims settlement — often within days instead of months.

**AI underwriting brief**: a Groq-hosted Llama model (`llama-3.3-70b-versatile`, via
LangChain's `ChatGroq`) is given only a condensed markdown table of already-computed numbers,
never raw data to reason over from scratch, and asked to write a short brief for both technical
and non-technical stakeholders. The `qa_disclaimer_check` node then verifies the mandatory
limitations disclaimer is present and cross-checks every EUR figure the brief mentions against
the computed ground truth, retrying generation once if either check fails.

## Case studies included

- **Türkiye–Syria, 6 February 2023** (bundled offline fixture): the real M7.8 Pazarcık
  earthquake and its M6.7 aftershock both register as candidates against the Gaziantep
  Residential Portfolio site, triggering tier 2 (60%) and tier 1 (25%) payouts respectively.
- **Haiti, 12 January 2010** (live USGS query): the real M7.0 earthquake near Port-au-Prince —
  the event whose real-world parametric CCRIF SPC payout is one of the best-known examples of
  this instrument working as designed.

## Repo structure

```
paraquake/
  app/streamlit_app.py           # Streamlit UI entry point
  app/components/                # map_view, tables, metrics rendering helpers
  src/paraquake/
    config.py                    # all tunable constants (documented as simplified)
    models.py                    # EarthquakeEvent, ExposureSite, TriggerResult
    data/                        # usgs_client.py, exposure_loader.py
    geospatial/distance.py       # haversine great-circle distance
    risk/                        # attenuation.py, trigger.py, payout.py
    agents/                      # LangGraph state, graph, prompts, and 6 nodes
  data/
    exposure_portfolio.csv       # 20 synthetic sites
    sample_usgs_response.json    # real, checked-in USGS response fixture
  tests/                         # pytest suite, incl. a mocked-LLM graph smoke test
```

## Deploying to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub (create a free
   account if you don't have one).
2. Click **New app**, select the `9117KET/paraquake` repo, branch `main`, and set the main file
   path to `app/streamlit_app.py`.
3. Under **Advanced settings → Secrets**, add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
4. Deploy. Once live, update the "Live demo" link at the top of this README with the assigned
   `*.streamlit.app` URL.

## Running locally

```bash
git clone <this-repo-url>
cd paraquake
pip install -r requirements.txt
pip install -e .
cp .env.example .env   # then add your own GROQ_API_KEY (free at console.groq.com)
streamlit run app/streamlit_app.py
```

Run the test suite (no API key or network access required — the LLM call is mocked and the
USGS client is tested against the bundled real fixture):

```bash
pytest
```

## How this maps to Munich Re's Graduate Trainee – AI Implementation JD

| JD requirement | How ParaQuake demonstrates it |
|---|---|
| Supporting AI/GenAI/agent-based solutions across the underwriting lifecycle, focused on NatCat modelling and risk assessment | A 6-node LangGraph pipeline (hazard data → exposure → geospatial trigger → filtering → GenAI report → QA guardrail) applied directly to a parametric NatCat underwriting use case. |
| Actively building, testing, and integrating solutions; configuring agent-based workflows; connecting AI components with existing underwriting systems | Hand-written Python geospatial/risk engine wired into a configured, conditional-edge LangGraph workflow connecting a real external hazard API (USGS) to a synthetic underwriting exposure system and an LLM report generator. |
| Solid practical skills in Python (or R/Matlab) | Entire stack in Python: data client, geospatial math, risk engine, LangGraph orchestration, Streamlit UI, pytest suite. |
| Applied AI/ML/GenAI interest in a real-world business environment, ideally NatCat risk modelling | GenAI (Groq-hosted Llama) translates quantitative trigger/payout output into a plain-English underwriting brief for a parametric earthquake product. |
| Foundational statistics and data analysis, including real-world datasets | Real USGS earthquake catalog (magnitude, depth, location, time), portfolio-level aggregation and tiering. |
| Experience or exposure to geospatial data (strong advantage) | Haversine great-circle distance engine, lat/lon exposure siting, radius-based "cat-in-a-circle" trigger logic, interactive pydeck map of epicenters vs. exposure sites. |
| Strong analytical skills, structured problem-solving, high attention to detail | Fully unit-tested quantitative core (distance/attenuation/trigger/payout), explicit named simplifying assumptions, and a QA agent that checks the LLM report's stated figures against computed ground truth. |
| Collaborate with technical AND non-technical stakeholders in a regulated environment | README written for a non-technical reader, a plain-English AI underwriting brief tab, and a prominent, explicit disclaimer distinguishing this educational demo from actuarial-grade catastrophe models. |

## License

MIT — see [LICENSE](LICENSE).
