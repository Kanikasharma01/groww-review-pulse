# Groww Review Pulse: from raw app reviews to a weekly product update and a support-ready fee explainer

An n8n workflow that reads recent public Groww app reviews, finds the main product themes, picks out a recurring fee/charge pain point, and produces:

1. a weekly internal **product pulse** (250 words or fewer), and
2. a customer-facing **fee explainer** (6 bullets or fewer, facts only, 2 official links, "Last checked").

After a human approval step, it appends the output to a Google Doc and creates a Gmail draft. It never sends email.

Built for the NextLeap PM Fellowship. Product: Groww (the same product as my facts-only mutual fund chatbot).

- Demo video: https://screenrec.com/share/yN3VYXaU1J
- Fee issue identified: **Brokerage and other charges on stock trades** (details below)

## What it does

| Step | What happens | n8n node |
|---|---|---|
| 1 | Reads reviews from a Google Sheet | Google Sheets |
| 2 | Keeps the last 12 weeks, drops duplicates and very short or very long reviews, samples up to 400 evenly across the window | Code: `Prepare Reviews` |
| 3 | The AI agent names up to 5 problem/request themes and picks one fee category | AI Agent |
| 4 | Splits the sample into batches of 50 | Code: `Make Batches` |
| 5 | The model labels every review with a theme number | Basic LLM Chain: `Classify Reviews` |
| 6 | Code counts the labels, ranks the themes, picks 3 quotes copied word for word from the sheet, and counts the fee reviews | Code: `Validate Insights` |
| 7 | Builds the fee explainer from facts taken from Groww's official pricing page | Code: `Fee Explainer` |
| 8 | Writes the pulse from the verified facts only | Basic LLM Chain |
| 9 | Checks the pulse (word count, exact quotes, 3 numbered actions) and builds the Doc entry and email text | Code: `Assemble Outputs` |
| 10 | **Approval gate**: pauses and shows the preview with Approve / Reject | Wait (form) + If: `Approved?` |
| 11 | On Approve: appends the entry to a Google Doc, then creates a Gmail draft | Google Docs, Gmail |

## Where approval happens (MCP-style gating)

The `Approval Gate` node (a Wait node in form mode) pauses the workflow after the outputs are generated and shows the pulse, the fee explainer and the two pending actions. The `Approved?` If node routes only an `Approve` answer to the Google Docs and Gmail nodes. A `Reject` answer goes to a no-op node, so nothing is logged or drafted. There is no send node anywhere in the workflow.

Note on MCP: this build uses n8n's built-in Google Docs and Gmail nodes behind an explicit approval step, which is the minimum the brief allows. It does not use an MCP server.

## What fee issue was identified from the reviews

**Brokerage and other charges on stock trades.**

From the final run (17 October 2026):

- Reviews in the CSV: 12,660. Usable after filtering (unique, 40 to 280 characters, last 12 weeks): 1,925. Analysed: 400 (sampled evenly across the window).
- Reviews mentioning brokerage or other charges (excluding praise about low charges): 41 of 400.
- Of those, reviews describing hidden or unexpected deductions: 5.
- Top 3 themes: Technical Glitches (63), Missing Features (52), High Brokerage Charges (40).

Most fee reviews say charges are high; a smaller group says deductions were unexpected or not clearly shown. So this is a pain point, not mainly a confusion about a single fee. The explainer therefore lists what is charged on a trade and where each charge comes from, and takes no side.

## Controls against bad AI output

- Quotes are never written by the model. Code copies them from the sheet by review id, skips abusive reviews, and prefers complaints in English.
- Theme counts come from code counting the model's labels, not from the model's own numbers. The run stops if the model labelled fewer than 90% of the reviews.
- The fee issue must appear in at least 10 sampled reviews, or the run stops.
- The fee explainer is built from fixed facts copied from Groww's pricing page, not from the model. An unknown fee category stops the run.
- The pulse is checked for 250 words or fewer, exact quotes and 3 numbered actions before anything reaches the approval step.
- The pulse prompt forbids investment advice and fee amounts.

## How to run

1. Get reviews as a CSV with columns `reviewId`, `content`, `score`, `at` (`scripts/fetch_reviews.py` produces this from the Play Store; run it in Google Colab).
2. Upload the CSV to a Google Sheet (File, Import).
3. In n8n: Workflows, Import from file, choose `workflow/review-pulse.json`.
4. Connect credentials: Google Sheets, Google Docs and Gmail. The three `OpenAI Chat Model` nodes (under the AI Agent, `Classify Reviews` and the pulse chain) were built with n8n's managed AI credits, so open each one and select your own OpenAI credential.
5. Point the Google Sheets node at your sheet and the Google Docs node at your own doc URL.
6. Open the chat and send `run weekly pulse`.
7. At the Approval Gate, open the form link, review the preview, and choose Approve or Reject.

## Files

- `workflow/review-pulse.json`: the n8n workflow (credentials and personal links removed)
- `data/groww_reviews.csv`: public Play Store reviews used as input
- `outputs/weekly_pulse.md`: the pulse and fee explainer from the final run
- `docs/`: screenshots of the Doc entry, the email draft and the workflow
- `sources.md`: source list
- `scripts/fetch_reviews.py`: review fetcher

## Limitations

- The model names the themes on every run, so theme names and counts shift slightly between runs. Temperature is 0 on the theme and labelling steps to reduce this (the pulse writer uses 0.2).
- Counts come from a sample of 400 reviews, not all reviews.
- Star ratings are unreliable in this data (some 5-star reviews are complaints), so themes are judged from the text.
- Fee facts are copied from Groww's pricing page on the date shown in "Last checked" and must be rechecked before reuse.
- Reviews are in several languages; quotes are limited to English by design.
- Quotes are the longest eligible review per theme, so one quote can be an outlier. In the final run, the second quote and the second action idea come from a single unusual request (banking app integrations) and are not typical of the Missing Features theme. A fix is to pick the quote that shares the most wording with the other reviews in its theme.

## Disclaimer

This project states facts about charges and gives no investment advice. It is a learning prototype, not an official Groww product.
