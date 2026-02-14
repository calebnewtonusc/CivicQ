# **What CivicQ is, in one breath**

CivicQ is a city-level “candidate Q\&A \+ ballot info” layer that makes campaigning look like **answering the public’s top questions, on record, in one place**, instead of spending money to grab attention.

It starts with **city council, mayor, school board, and local ballot measures** because the pain is high (voters have no idea what anyone stands for) and the adoption path is realistic.

---

# **What exists today, what’s not working, and what we’re doing differently**

A bunch of organizations have tried to solve pieces of this problem. Most of them prove the demand is real. Their limitations show exactly where CivicQ needs to be opinionated.

**Text questionnaires and voter guides work, but candidates often avoid them.**  
Organizations like League of Women Voters run VOTE411 and explicitly publish candidate answers “word for word.” ([VOTE411](https://www.vote411.org/candidate-contact?utm_source=chatgpt.com)) That’s valuable, but the format is still mostly text, and participation can be uneven in smaller races because candidates don’t feel pressure to respond (or they fear getting clipped out of context in attack ads, which is a known pattern with candidate questionnaires). ([Vote Smart](https://justfacts.votesmart.org/about/political-courage-test/?utm_source=chatgpt.com))  
**CivicQ difference:** video answers recorded in-app (no editing), plus a design that reduces “clip risk” by forcing structured clarity and giving immediate rebuttal rights (more on that below).

**Personalized ballot platforms exist, but they don’t create a public “answer-on-record” arena.**  
BallotReady can generate a personalized ballot and provide candidate/measure info via products like Ballot Engine. ([BallotReady for Organizations](https://organizations.ballotready.org/ballot-engine?utm_source=chatgpt.com)) Great for “what’s on my ballot,” but it’s not built around “top questions chosen by verified voters with standardized video answers.”  
**CivicQ difference:** your ballot is the home screen, but the atomic unit is “question → answer → rebuttal → sources → transcript,” with a ranking system that represents the whole electorate instead of the loudest faction.

**Candidate Q\&A platforms have existed, but sustainability and participation are hard.**  
AskThem (from the Participatory Politics Foundation) is a direct ancestor of the idea, and they eventually went offline while trying to redesign. ([Participatory Politics Foundation](https://participatorypolitics.org/askthem-is-being-redesigned-for-2018-midterms/?utm_source=chatgpt.com)) That doesn’t mean the concept is bad. It means: governance, funding, moderation, and distribution are existential.  
**CivicQ difference:** start as a paid city product with a pilot playbook and procurement path, not a volunteer-run national platform from day one.

**Identity and content authenticity is now a first-class problem because of AI impersonation and deepfakes.**  
Ballotpedia partnered with Truepic to verify candidate identities and reduce impersonation and AI-generated content risks. ([Truepic](https://www.truepic.com/blog/ballotpedia-and-truepic-partner-to-verify-u-s-political-candidate-identities-and-help-reduce-impersonation-and-ai-generated-content-risks?utm_source=chatgpt.com))  
**CivicQ difference:** we bake provenance into the recording flow (record in-app, cryptographic signing, tamper-evident pipeline) so answers are natively verifiable, not “uploaded from anywhere.”

**Digital deliberation tools show how to avoid mob dominance, but they’re not election products.**  
Polis and Taiwan’s vTaiwan show that large-scale input can be structured into something legible, and that a “consensus map” is often more useful than a comment war. ([Computational Democracy](https://compdemocracy.org/polis/?utm_source=chatgpt.com))  
**CivicQ difference:** we keep the UI simple (questions \+ answers), but we steal the core idea: represent clusters of viewpoints rather than rewarding one faction’s brute-force voting.

**Voter verification is real, but it’s politically sensitive and UX-fragile.**  
The Internal Revenue Service has used ID.me for identity verification for some online services. ([IRS](https://www.irs.gov/newsroom/new-identity-verification-process-to-access-certain-irs-online-tools-and-services?utm_source=chatgpt.com)) That history also shows how quickly verification choices can trigger privacy backlash (especially around facial recognition). ([The Washington Post](https://www.washingtonpost.com/technology/2022/02/07/irs-idme-face-scans/?utm_source=chatgpt.com))  
**CivicQ difference:** verification is modular, city-configurable, and designed to minimize data retention. Also: in the MVP, verification’s job is to protect question-ranking integrity, not to run elections.

One sentence summary of the differentiation: CivicQ is “VOTE411 meets verified Reddit meets in-app recorded video provenance,” deployed city-by-city with a procurement-ready playbook, and designed specifically to reduce polarization incentives rather than amplify them.

---

# **CivicQ PRD v1**

## **Product intent and success definition**

You wrote the core problem clearly: campaigns aren’t effectively answering what people actually want to know, and instead optimize for attention and hate.

CivicQ’s purpose is to turn campaigning into **public service clarity** by changing the default “campaign surface area” from paid persuasion to structured answers.

Success looks like this in a pilot city:

A normal voter can open CivicQ, see their ballot, watch a handful of answers, and genuinely feel “I understand what these candidates actually plan to do,” without needing flyers, rumor, or five different websites.

Failure looks like what you said: increased polarization, performative dunking, or the platform becoming another corruption channel. So the PRD treats “anti-polarization by design” as a first-class requirement, not vibes.

## **Non-goals for v1**

CivicQ v1 is not:

An official voting system. We do not collect votes for elected office.

A replacement for campaign finance law. CivicQ can make paid campaigning feel less necessary, but it can’t ban it by itself.

A news feed. No doomscrolling. No “engagement algorithm” that rewards outrage.

A debate stage. The whole point is that debates are often theater. CivicQ is the permanent record.

## **Who CivicQ serves**

Voters (primary): want clarity fast; want to ask what they care about; want trust that the ranking isn’t botted.

Candidates (primary): want a fair channel to present positions; want protection against bad faith; want a predictable format.

City election staff / clerk / city manager (primary): want low drama; want compliance; want accessibility; want clear reporting.

Local civic groups (secondary): want a clean, shareable source of truth to distribute.

## **Core product principles**

CivicQ runs on a few principles that become rules:

No pay-to-win visibility. No ads. No boosting. No “sponsored answers.”

No edited answer videos. All answers recorded in-app, time-boxed, and standardized.

Everything important is on record. Questions are versioned. Answers attach to a question version forever.

Ranking must represent the community, not just the loudest faction.

Verification is required to rank (upvote/downvote) and to submit questions, but watching is public.

## **The content model (what exists inside CivicQ)**

CivicQ content is not a feed. It is a structured ballot library.

A “ballot” contains contests (races \+ measures). Each contest contains candidates or positions (for/against on measures). Candidates have answer sets tied to questions. Questions are tagged by issue, clustered for duplicates, and ranked.

Everything is anchored to “what’s actually on the ballot,” which is how you avoid drifting into national outrage content.

## **The voter experience (3-minute happy path, 30-minute deep dive)**

### **3-minute happy path**

A voter opens CivicQ and enters address (or chooses city).

They see “Your Ballot” as the home screen. Each contest has a completion bar like “3 of top 10 questions answered.”

They tap the first contest they care about (usually mayor or a hot school board race).

They watch two short answers from each candidate: the top-ranked question and a second high-signal question from another viewpoint cluster.

They leave with a confident mental model: what each person stands for, and what’s contested.

### **30-minute deep dive**

They tap into “Issues” and follow two or three topics (housing, school safety, taxes, etc.). Following issues creates a curated “Answer Set” across races: “show me every relevant answer from all candidates who touch this issue.”

They compare candidates on the same question side-by-side (split-screen transcripts, not split-screen video).

They watch rebuttals only when they want them, and they can see “source cards” attached to claims.

They share a single link that deep-links to “Candidate X answering Question Y \+ Candidate Z rebuttal \+ transcript.”

## **Screens and flows (v1)**

I’m going to describe screens in paragraphs so it’s readable, but each paragraph is specific enough for designers and engineers.

### **Onboarding and verification**

The onboarding screen offers “Browse as guest” and “Verify to participate.” Guest mode is immediate: no friction for watching. Verify mode explains why: “You can submit questions and vote questions up/down only as a verified resident of this city.”

Verification in v1 supports multiple city-configurable methods. The UI is the same; only the backend adapter changes. The user completes verification, then gets a badge like “Verified resident: San Marino” and a privacy note about what’s stored.

### **Home screen: Your Ballot**

Home is “Your Ballot.” It shows contests as cards. Each card shows: contest title, candidates, and a progress indicator that represents “answers available” and “answers watched.” The top CTA is always: “Watch the top questions.” Secondary actions: follow contest, follow issue topics, share.

There is no infinite scroll. The screen ends.

### **Contest screen: Race or Measure**

For a race, the contest screen has three zones:

First, a “Top Questions” module that shows the ranked list (with issue tags), plus a toggle for “All questions” vs “Top set.”

Second, a “Candidate Answer Grid” that shows each candidate with status: answered X of top Y. This creates social pressure without forcing requirements.

Third, a “Compare” module that lets the voter choose a question and see all candidates’ answers in one place.

For a ballot measure, the contest screen shows the official measure summary and fiscal impact (city-provided text), plus “Top Questions for Pro/Con” with verified proponents and opponents answering, if those roles exist in that city’s process.

### **Question screen: the atomic unit**

The question page is the most important screen in CivicQ.

It shows the question text, issue tags, and a “version history” link. It shows how many verified voters upvoted/downvoted it, plus the representation metadata (example: “highly ranked across multiple neighborhoods,” if the city supports that).

Below that is “Answers” with one card per candidate: video, transcript, and a “claims & sources” panel that candidates can optionally attach. Rebuttals appear as a second layer: “Candidate B rebuttal to Candidate A,” time-boxed and specifically bound to a quoted clip or transcript segment, so rebuttals are anchored, not free-floating rants.

### **Ask a question (voter submission)**

Submitting a question forces a clean structure.

The voter enters a question in one sentence, chooses issue tags, and optionally adds a short context line (“Why this matters to me”). Before posting, the app runs duplicate detection and offers: “This looks similar to these existing questions; want to upvote one instead?” The user can still post, but the system will likely merge it later.

After posting, the question enters “Pending sanity check” (automated) and may be escalated to the city moderation board depending on thresholds.

### **Voting on questions (ranking UI)**

The question list is intentionally boring. It is a list with upvote/downvote arrows, an issue tag, and a “why it’s ranked here” tooltip.

The key is: the UI teaches voters that the goal is not “my team wins.” The goal is “these are the questions we collectively need answered.”

### **Candidate portal (v1)**

Candidates get a clean portal, web-first.

They verify candidate identity (city-issued candidate filing ID plus extra proof). Their profile shows what races they’re in and which questions are in their “Top 100 queue” plus deadlines.

Recording is in-app or in-browser, but always “recorded through CivicQ.” The camera UI shows time remaining, question text, and structured prompts like “Give your position, the tradeoff you accept, and what you would measure after 6 months.” They submit. The system generates transcript, captions, and a “review your transcript” screen where they can correct transcription errors without altering the video.

Candidates can also choose to attach sources for claims. The source attachment tool is constrained: link to official docs, budgets, ordinances, audits, or reputable datasets. This doesn’t solve lying, but it raises the cost of lying, and it gives rebuttals something concrete to target.

## **Ranking and the mob dominance problem**

You identified the failure mode perfectly: one loud faction floods the top 100\.

So ranking is not “Reddit raw score.” It’s “Reddit UI with representative math underneath.”

In v1, the ranking system uses:

Verified-only voting. Watching is public, ranking is gated.

Rate limiting and anomaly detection. If a small cluster of accounts votes in lockstep at unnatural cadence, those votes are downweighted pending review.

Issue buckets. Questions are tagged by issue; the “Top 100” is not one list. It’s a portfolio. Example: Top 100 might contain 20 housing, 15 public safety, 15 education, 10 budgeting, etc., based on the city’s chosen schema. The portfolio weights can be learned from vote patterns but capped so one issue cannot consume everything.

Viewpoint clustering. Questions that are semantically similar are clustered; clusters are limited in how many slots they can occupy. This prevents “ten versions of the same talking point” from taking over.

A “minority concern slot” mechanism. If a question is intensely important to a smaller segment but not everyone, it can still surface in a guaranteed portion of the set. This is how you reduce polarization: you force the system to acknowledge minority concerns without making them dominant.

The result is that top questions feel “community-shaped,” not “faction-shaped.”

## **Candidate participation rules (constraints that force clarity)**

This is the section you said “do whatever you think is best,” so I’m going to be decisive.

Candidates hate questionnaires because they fear gotchas and clips. So CivicQ’s constraints are designed to reduce clip risk while increasing clarity.

Answer format v1:

Time-boxed answers per question (city-configurable). Example: 90 seconds for local races, 120 seconds for mayor, 180 seconds for measures.

Required structure: position → rationale → tradeoff → implementation → measurement. The UI prompts this; candidates don’t have to label it, but the structure is enforced by the recording flow and post-processing.

One optional “values sentence.” Candidates can state the principle driving their view. This is crucial for voters, and it reduces the incentive to dodge.

One optional “I don’t know yet” path. Candidates can say “I need to learn X before committing.” That honesty should be rewarded, not punished. The UI can label it as “Open question” instead of “dodged.”

Rebuttals:

Rebuttals are time-boxed, and they must attach to a specific quoted claim. Rebuttal content is not “free attack mode.” It’s “you said X; here’s why that’s wrong or missing context.”

Candidates also get a “correction” tool. If they misspoke, they can post a correction that shows up as an appended note with timestamp. The original remains. The correction does not replace it. This is a key anti-corruption mechanic: it rewards truth maintenance without allowing quiet edits.

## **Question rules (what’s allowed, editing, merging)**

Questions are freeform but bounded by civic relevance: they must be about the office’s jurisdiction, ballot measure content, or governance topics.

Editing is allowed, but it is transparent and versioned. If a question changes materially, it becomes a new version. Answers bind to versions. If someone tries to “bait-and-switch,” the UI makes it obvious.

Duplicate questions are merged automatically when confident. When uncertain, they go to a review queue for city moderators.

Bad-faith questions can be filtered, but this must be transparent and appealable, or you’ll get legitimacy blowback. The moderation policy must be published inside the app.

## **Moderation and trust**

CivicQ moderation has three layers:

Automated filters for doxxing, slurs, threats, and spam.

Civic integrity rules: off-jurisdiction questions, pure harassment, propaganda phrased as a question.

A city moderation board for edge cases, with a strict “process over opinions” standard. The board is not allowed to remove a question because it makes a candidate look bad. It can remove questions that violate published standards.

Every moderation action creates an audit log entry visible in aggregate: “X questions removed for doxxing,” etc. The goal is to prevent the suspicion that moderation is political.

## **Anti-polarization mechanics (the part that makes this not just “politics YouTube”)**

CivicQ prevents the platform from becoming a rage machine by limiting the exact features rage needs.

No comments under videos in v1. Comments create performative dunking and turn the product into a social war. Sharing exists, but the share is the record, not a comment section.

No engagement feed. CivicQ is a library, not a casino.

No “reaction” metrics. No like counts on candidates. Only question importance signals.

Structured rebuttals only. No open-ended attack content.

Portfolio ranking that forces representation.

These are product decisions, not moral speeches. They are the difference between civic clarity and a weapon.

## **Metrics and reporting (how we prove it works)**

CivicQ metrics are designed to prove “informed voting” improvement, not dopamine.

Adoption: verified users as a share of eligible voters; guest users; repeat weekly active.

Coverage: percent of contests with at least one candidate participating; percent of top questions answered by each candidate.

Engagement quality: median watch time per voter; number of “compare answers” actions; number of voters who watch both candidates on the same question.

Diversity of attention: how evenly voters watch across issues (not just one hot-button topic).

Trust indicators: report rates, appeal outcomes, verification failure rates, moderation turnaround.

Outcome proxy: post-election survey: “I felt informed,” “I understood differences,” “I saw direct answers to what I care about.” The survey is essential in pilots.

---

# **Technical spec v1**

## **Architecture overview**

CivicQ is a location-anchored, high-integrity content system. Architecturally, it is closer to “secure civic portal \+ media pipeline” than to social media.

Core components:

Client apps: Web first (mobile responsive). Mobile app optional in v1, but the recording experience benefits from native. We can still ship web-based recording for MVP.

API backend: one service for core CRUD \+ ranking \+ moderation flows.

Database: relational for integrity (Postgres).

Search/semantic layer: used for dedupe and clustering (vector search).

Media pipeline: upload → transcode → captions/transcripts → provenance signing → CDN delivery.

Admin console: city staff dashboards, candidate onboarding, moderation queues, reporting.

## **Identity and verification choices**

This is the hardest part, and the spec treats it as modular.

Verification has two independent goals:

Prove “one person \= one account for ranking and asking questions.”

Optionally prove “resident of city / eligible voter,” depending on city preference.

The verification system should align with digital identity best practices like NIST digital identity guidance. ([NIST Pages](https://pages.nist.gov/800-63-4/?utm_source=chatgpt.com))

Verification methods v1 (city picks one):

Light verification (low friction): SMS \+ address confirmation code mailed to residence. This is slow but extremely hard to bot at scale and stores minimal PII.

Medium verification: match against voter roll or resident roll via name \+ DOB \+ address, plus knowledge check (not ideal because knowledge checks are weak post-data-breaches, but sometimes cities already do this).

Strong verification: third-party identity proofing vendor similar to what the IRS has used for online services. ([IRS](https://www.irs.gov/newsroom/new-identity-verification-process-to-access-certain-irs-online-tools-and-services?utm_source=chatgpt.com)) This must be opt-in per city, with clear privacy disclaimers, because vendor choices can trigger backlash. ([The Washington Post](https://www.washingtonpost.com/technology/2022/02/07/irs-idme-face-scans/?utm_source=chatgpt.com))

In all cases, CivicQ stores the minimum: a verification token, status, city scope, and timestamps. Any sensitive documents should be processed by the verification provider and never stored by CivicQ.

## **Candidate identity verification**

Candidates must be verified differently than voters.

Candidate verification ties to the official filing list for the contest. The city uploads candidate roster or CivicQ ingests it from the election office’s official export.

Candidate must then complete a “recording authenticity handshake.” This is where the Ballotpedia/Truepic model is informative: identity verification plus authenticated capture reduces impersonation risk. ([Truepic](https://www.truepic.com/blog/ballotpedia-and-truepic-partner-to-verify-u-s-political-candidate-identities-and-help-reduce-impersonation-and-ai-generated-content-risks?utm_source=chatgpt.com))

CivicQ v1 approach:

Candidate portal login \+ one-time code delivered via filing contact method.

First recording session includes a short “liveness \+ phrase” clip that is never public, used only to bind identity.

All published videos carry an authenticity stamp and a chain-of-custody log (internal).

## **Data model (core tables)**

I’m writing this in plain language, but it maps 1:1 to Postgres tables.

Users: account id, role (voter/candidate/admin/mod), city scope, verification status, created/last active.

VerificationRecords: user id, method, provider, city scope, status, timestamps, minimal metadata.

Ballots: city, election date, version, source metadata.

Contests: ballot id, type (race/measure), title, jurisdiction, office, seat count.

Candidates: contest id, name, filing id, status, contact for onboarding, profile fields.

Measures: contest id, measure text, summary, fiscal notes, pro/con roles.

Questions: contest id, canonical question id, current version id, issue tags, status, cluster id.

QuestionVersions: question id, version number, text, edit author, created timestamp, diff metadata.

Votes: user id, question id, value (+1/-1), timestamp, device risk score, weight.

VideoAnswers: candidate id, question version id, video asset id, transcript id, duration, published status.

Rebuttals: candidate id, target answer id, target claim reference, video asset id, transcript id.

Claims: answer id, extracted claim snippet, candidate-provided sources, reviewer notes.

Reports: reporter id, target type (question/answer/rebuttal), reason codes, status.

ModerationActions: target, action type, moderator id, rationale code, timestamps.

AuditLog: immutable event stream for anything integrity-sensitive.

Follows: user id, follow target (contest/candidate/issue tag), notification prefs.

## **Ranking algorithm (v1)**

The ranking algorithm is where CivicQ either works or becomes faction theater.

v1 ranking score is not just upvotes minus downvotes.

It is a composite:

Base score from verified votes, time-decayed slightly to prevent early capture.

Cluster cap: no more than N questions per semantic cluster in the top set.

Issue portfolio constraint: the top set is allocated across issue tags based on vote distribution with caps.

Anomaly adjustments: votes from suspicious accounts are downweighted until cleared.

Geographic or district balancing (optional): if the city provides neighborhood/district mapping, CivicQ can ensure representation across areas.

This is inspired by the “represent the space of viewpoints” logic used by deliberation tooling, even though CivicQ is not a deliberation forum. ([Computational Democracy](https://compdemocracy.org/polis/?utm_source=chatgpt.com))

## **Question dedupe and clustering**

This is critical because voters will ask the same question 40 times.

Pipeline:

On submission, generate embeddings and compare to existing questions in the same contest.

If similarity \> threshold, suggest existing question to upvote.

If still submitted, mark as “candidate for merge.”

Nightly clustering job groups near-duplicates.

If cluster confidence high, auto-merge: one canonical question with multiple “asked by” references.

If cluster confidence medium, send to moderation queue.

This is where we borrow the best “input crowd, output meaning” idea, but we keep the UI simple. ([Computational Democracy](https://compdemocracy.org/polis/?utm_source=chatgpt.com))

## **Video pipeline and provenance**

CivicQ’s media pipeline is not optional. It is the product’s credibility.

Capture requirements:

Video must be recorded in CivicQ, not uploaded.

No filters, no cuts.

Time-box enforced at capture layer.

Processing steps:

Upload to object storage.

Transcode into streaming formats.

Generate transcript and captions.

Hash the raw file \+ transcoded assets and store hashes.

Attach authenticity metadata to the asset (tamper-evident).

Serve via CDN.

This is aligned with the reality that candidate impersonation and synthetic media are now a mainstream risk for elections. ([Truepic](https://www.truepic.com/blog/ballotpedia-and-truepic-partner-to-verify-u-s-political-candidate-identities-and-help-reduce-impersonation-and-ai-generated-content-risks?utm_source=chatgpt.com))

## **APIs (v1 surface)**

Auth and identity:

POST /auth/signup  
POST /auth/login  
POST /auth/verify/start  
POST /auth/verify/complete  
GET /me

Ballot and contest discovery:

GET /cities  
GET /elections?city=  
GET /ballot?city=\&address=  
GET /contests?ballot\_id=  
GET /contest/:id

Questions and ranking:

POST /contest/:id/questions  
GET /contest/:id/questions?sort=top\&issue=  
POST /questions/:id/vote  
GET /questions/:id  
GET /questions/:id/versions  
POST /questions/:id/edit

Candidates and answers:

GET /contest/:id/candidates  
GET /candidates/:id  
POST /candidate/:id/answers (candidate only)  
POST /candidate/:id/rebuttals (candidate only)

Moderation and reporting:

POST /reports  
GET /admin/modqueue  
POST /admin/modaction

Analytics and reporting (city admin):

GET /admin/metrics  
GET /admin/coverage  
GET /admin/export (public archive / retention)

## **Infrastructure choices (sane MVP defaults)**

You can implement this on any modern cloud. The important part is choosing boring, secure defaults.

Suggested stack for MVP:

Postgres (managed): transactional integrity, row-level access control.

API: FastAPI or Node (either works). The key is strong auth middleware, audit logging, and rate limiting.

Object storage for video: S3-compatible.

Transcoding: managed media pipeline if budget allows, or a containerized FFmpeg worker.

Search: Postgres full-text for simple; plus vector DB (pgvector) for dedupe.

CDN: Cloudflare or similar for streaming performance.

Observability: structured logs, error tracking, basic tracing.

Security baseline:

OWASP protections, strict CORS and CSP, WAF, DDoS protection.

Encryption at rest and in transit.

Secrets in a managed vault.

Immutable audit log.

Rate limits on question submission and votes.

Device and network anomaly detection.

Privacy model:

Minimal PII.

City-scoped identities.

Public content is answers and questions, not user profiles.

Verified voters can be pseudonymous publicly. The city can audit counts without seeing individuals.

## **Governance and deployment model (how you keep it legit)**

CivicQ should be structured as a civic product with explicit neutrality.

No paid political advertising.

No candidate favoritism in UI.

Published moderation standards.

Public transparency report after each election.

Independent advisory board for the pilot city (optional but powerful).

---

# **Pilot playbook**

## **Pilot thesis**

Local elections are the perfect wedge because voters are least informed, and the “marketing spend arms race” is the most obviously stupid at small scale.

The first pilot must produce one undeniable outcome: “Our city finally had one place where candidates answered what residents actually asked, and it was usable.”

## **Pick the pilot city like a strategist**

Ideal pilot city characteristics:

Small enough that you can reach a meaningful share of voters.

Has a real election coming up (60–120 days out is workable).

City staff open to digital civic innovation.

Local civic groups willing to promote (PTA, neighborhood associations).

A few candidates who will participate early and publicly.

## **Stakeholder map and who to pitch**

You pitch different benefits to different people.

City Clerk / Elections: reduces confusion, improves access, creates a clean record.

City Manager / Council: improves legitimacy, reduces misinformation, modernizes engagement.

Candidates: fair channel, equal exposure, less need to spend.

Civic groups: easy voter education tool.

Local media: embed-ready “answer set” instead of chasing candidates.

## **The first meeting pitch (tight script)**

If you get 10 minutes with a city:

“Right now, your voters get flyers and rumors. They don’t get direct answers. CivicQ is a city-branded portal where verified residents submit and rank questions, and every candidate answers the top questions on video, recorded inside the platform with no editing. It’s a public record that’s easy to share, and it helps voters understand differences fast. It does not run voting. It makes voter information and campaigning converge into one transparent record.”

Then you show three screens: ballot home, question page with two candidate answers, and candidate portal “Top Questions queue.”

## **Procurement and pricing (simple, realistic)**

For pilots, you need a number that feels trivial to a city budget but real to you.

Pilot price examples:

$5k–$25k per election depending on city size and whether the city wants custom verification.

Optional sponsorship from nonpartisan civic philanthropy if the city needs it.

No per-candidate fees. That would instantly poison legitimacy.

## **Timeline (90-day pilot template)**

Weeks 1–2: city agreement, election data ingest, branding, moderation policy approval, candidate roster import.

Weeks 3–4: candidate onboarding, verification method setup, soft launch to civic groups.

Weeks 5–8: question submission window \+ ranking phase, weekly reporting to city.

Weeks 6–10: candidate answer recording window, with deadline waves.

Weeks 10–12: final “top set” published, share campaign, post-election survey.

## **Candidate onboarding plan (the part that makes or breaks adoption)**

Candidates need it to feel fair, easy, and safe.

Onboarding steps:

They receive an official invite via city clerk email list or public filing contacts.

They see the format, time limits, and rebuttal rules upfront.

They get “recording office hours” support (even if that’s just Zoom).

They see a progress bar relative to other candidates. Social pressure is gentle but real.

If a candidate refuses, CivicQ displays a neutral status: “No response submitted.” No shaming language.

This matches the reality that candidate questionnaires often have uneven response rates, even for established organizations. ([VOTE411](https://www.vote411.org/candidate-contact?utm_source=chatgpt.com))

## **Voter acquisition (without becoming a campaign)**

You do not run growth like a startup. You run distribution like a civic utility.

Channels that fit CivicQ’s identity:

City website banner and QR codes on official mailers if allowed.

Library, schools, community centers posters.

Neighborhood association newsletters.

PTAs.

Local League of Women Voters chapters (if they want), since the mission aligns with “hear directly from candidates.” ([VOTE411](https://www.vote411.org/candidate-contact?utm_source=chatgpt.com))

Local media embeds.

The share format matters: every answer should be shareable as a clean link with transcript snippet, not as an attention trap.

## **Weekly reporting to the city (make it feel safe)**

Every week during the pilot, the city gets a one-page report:

Verified users count.

Top issues emerging.

Number of questions submitted, merged, removed (by reason).

Candidate participation progress.

Any integrity flags (suspected botting attempts, resolved actions).

This report is how the city trusts you.

## **Moderation runbook (practical)**

Define rule categories, not political judgments:

Spam and bot content.

Personal info and doxxing.

Threats.

Off-topic (not jurisdiction-relevant).

Harassment disguised as a question.

Publish the rules inside the app and allow appeals.

Moderation turnaround targets (example): 24 hours for safety items, 72 hours for borderline items.

## **End-of-pilot evaluation (prove impact)**

After election day, you run:

Voter survey: informedness, clarity, trust, ease.

Candidate survey: fairness, effort required, whether they’d use it again.

City staff survey: admin overhead, public feedback, complaints.

Hard stats: participation rates, answer coverage, watch behavior.

You publish a transparency report.

Then you go sell the next city with proof.

---

# **Team onboarding guide (so anyone can join instantly)**

This is how you recruit across disciplines without confusion.

Engineers join by owning one of four pillars:

Integrity pillar: verification adapter, vote weighting, anomaly detection, audit logs.

Media pillar: recording UX, transcript pipeline, provenance, CDN performance.

Ranking pillar: clustering, portfolio top-k, fairness constraints, explainability UI.

Admin pillar: city console, moderation queue, reporting exports, accessibility.

Designers join by owning “clarity UX”:

Make the ballot the home screen.

Make compare mode unbelievably simple.

Make candidate recording feel safe and structured.

Make the product feel calm, like a civic tool, not an app.

Politics/government people join by owning “legitimacy”:

City outreach.

Procurement and compliance.

Moderation governance.

Partnerships with civic groups.

Candidate relationship playbook.

Business/marketing people join by owning “distribution without toxicity”:

Pilot case study story.

City-by-city rollout strategy.

Pricing and packaging.

Partnership engine.

Brand that screams “nonpartisan utility.”

---

# **Final notes: the two hardest problems, stated honestly**

Problem 1 is verification. It’s not just technical. It’s trust. The IRS example shows verification can work, but it also shows the backlash risk if it feels invasive. ([IRS](https://www.irs.gov/newsroom/new-identity-verification-process-to-access-certain-irs-online-tools-and-services?utm_source=chatgpt.com)) CivicQ has to be modular and minimalist about data retention, or you’ll lose legitimacy.

Problem 2 is candidate participation. Tools like VOTE411 show “publish answers word for word” is valuable, but participation is always a battle and must be designed for. ([VOTE411](https://www.vote411.org/candidate-contact?utm_source=chatgpt.com)) CivicQ’s constraints and rebuttal rules are specifically meant to make participation feel safer, not riskier.

If you want one north-star sentence to put at the top of every doc and pitch:

CivicQ turns campaigning into a standardized, verifiable public record of candidates answering the public’s top questions, city by city, with integrity by design.

If you want, I can also generate a “Pitch Deck Outline v1” that matches this PRD and pilot plan, but in the exact 10-slide structure you’d use to recruit engineers and convince a city in one meeting.

