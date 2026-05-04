# D6A — Stakeholder Role-Play Answers
**Stakeholder:** Amelia Forsythe, General Counsel, Helix Workforce Software
**Interviewer:** FDE Assessment Team
**Date:** 2026-04-30

---

## Category A: Policy/Knowledge Base Structure and Machine-Readability

---

**Q1: Is the playbook a single SharePoint page with sections for each of the 7 clause types, or is it distributed across multiple documents, pages, or linked files?**

It's a single SharePoint page — "Position Statements v3.4" — with numbered sections, one per clause type. Section 12 is DPA, for example. There are some linked Word templates in Annex C for the standard DPA and a couple of redline precedents, but the position statements themselves are all on one page. It's not a knowledge base in any sophisticated sense; it's a formatted document we've maintained as a page rather than a file because it's easier to update in place.

---

**Q2: What is the formal process for updating the playbook — does Amelia approve every change before it is published, or can any team member edit the SharePoint page?**

*[brief pause]* 

Formally, I should approve any change to a position statement. In practice, I'm the only one who ever edits it, so that hasn't been an issue. The lawyers use it as a reference, they don't edit it. If one of them thought a position needed updating, they'd flag it to me. But if I'm being honest, "formal process" is generous — there's no version control beyond SharePoint's built-in history, no change log, and no alert when the document changes. It works because I'm the only one touching it. If that changes, we'd need something more structured.

---

**Q3: Are there vendor-specific playbook exceptions — positions that apply only to certain vendors or vendor categories?**

No formal exceptions recorded anywhere. In practice there are a handful of large accounts where we've agreed slightly different positions through negotiation — a hyperscaler where we accepted their DPA template rather than ours, for instance — but those are recorded in the signed contract, not in the playbook. The playbook reflects our standard opening position. If a vendor has a pre-agreed carve-out, Tom wouldn't know about it unless he checked the prior contract, which he does for renewals but not always for new vendors.

---

## Category B: The Routing/Classification Logic — How It Actually Works Today

---

**Q4: For qualitative clause types — IP ownership, indemnity scope, governing law — how does Tom currently decide whether a clause is standard, negotiable, or escalation-required?**

Tom's pretty good, honestly. For the clear-cut ones — governing law, termination notice period — he matches against the playbook position fairly literally. For the fuzzier ones — indemnity scope, IP — it's more of a judgment call about whether the commercial intent is equivalent, even if the wording's different. He'd describe it as "does this achieve the same thing for us." He won't escalate something just because the wording isn't identical to ours. What he escalates is when the intent is different, not just the words. I'd say for liability cap and IP it's the most judgment-heavy; for governing law and termination it's nearly mechanical.

---

**Q5: Of the ~30 escalation-required contracts per quarter, what are the most common triggers?**

DPA and IP ownership, by a wide margin. DPA because it's the most technically complex and the playbook's been stale — Tom knows he's on thin ice there so he escalates anything that looks non-standard. IP because we sell software and IP ownership is commercial-critical; Tom knows he shouldn't be deciding that alone. Liability cap occasionally, if the deviation is severe. Governing law almost never — if it's not English law we escalate immediately, but most vendors offering UK services accept English law. Indemnity scope is a grey area; Tom sometimes gets those wrong in both directions.

---

**Q6: When Tom routes a contract to WS2 or WS3, does he record why?**

He makes notes — you've seen some of them, I assume, the margin annotations. But it's not systematic. He notes the clause, the issue, sometimes what he's planning to do. Whether those notes are preserved formally in Ironclad or whether they're just on his working copy of the Word document varies by contract. I wouldn't call it a structured decision log. If you wanted to reconstruct why a contract was routed a particular way, you'd have to find his annotated copy, which may or may not be in SharePoint.

---

## Category C: The Governance/Approval Rule — Exactly How It Works Operationally

---

**Q7: When a named lawyer signs off on a counteroffer today, how is that sign-off recorded?**

*[pause]*

I'll be straightforward with you: it's not as structured as I'd like. The standard practice is that the draft counteroffer goes into a shared email thread or a Teams message — the lawyer reads the redlined document, replies with something like "approved, send" or suggests changes. Tom then sends the counteroffer. There's no formal sign-off field in Ironclad for this step. The Ironclad case record gets updated with the outcome, but the approval itself lives in email. I've flagged this as a gap before. It's on my list. If someone were ever to audit a specific sign-off decision, we'd be reconstructing it from email timestamps.

---

**Q8: Who can provide the named-lawyer sign-off — any of the three commercial lawyers, or is sign-off authority scope-limited?**

For standard deviations going to WS2, any of the three commercial lawyers can sign off. For escalation cases — WS3, anything involving DPA, IP disputes, or anything above a certain deal size — I expect it to come through me. That's not written down anywhere formally, but it's understood. The commercial lawyers know their lane. If it's a large deal or there's any regulatory dimension, they'll bring it to me before anything goes out. Tom knows this too; he routes escalations to me directly.

---

**Q9: Does the sign-off apply at the contract level — one approval for the whole counteroffer — or at the clause level?**

In practice it's at the contract level — one approval for the full redline package going out. The rule says "the specific clauses being negotiated" because I want the lawyer to have actually read the specific clauses, not just approved blindly. But the sign-off act itself is a single approval for the package. We don't have a workflow where clause A gets approved Tuesday and clause B gets approved Thursday and then we send. It goes out together, approved together.

---

## Category D: Exception Patterns and Edge Cases

---

**Q10: What makes a clause escalation-required versus merely negotiable in practice?**

A few things. Magnitude — a liability cap at half our playbook floor isn't a redline, it's a negotiation we need a lawyer to lead. Clause type — anything touching regulatory obligation, especially DPA or anything with GDPR or now DPDI implications, I want a lawyer's eyes on it. The vendor's profile matters informally — if it's a large regulated enterprise procurement that we know is CRO-priority, the commercial lawyers are more likely to loop me in even on something borderline. And sometimes it's pattern recognition — Tom has seen enough contracts to know when a clause has been drafted unusually, even if on paper it's within range.

The honest answer is that "escalation-required" lives partly in Tom's judgment, and his judgment is mostly good. The cases I'm most worried about are the ones where the clause looks standard but has an unusual framing that he doesn't catch — that's the failure mode that keeps me up at night more than the obvious deviations.

---

**Q11: How often do contracts arrive in a form that is not a standard Word document via Outlook email?**

More often than the official process would suggest. I'd guess 10 to 15 percent arrive as PDFs, mostly from larger enterprise procurement teams who generate contracts from their own systems. Some come as SharePoint links from vendors who use their own CLM. Occasionally we get an amendment-only document that references a master agreement we have to locate separately. Tom handles those manually. We've never formally quantified it but it's definitely not a rare exception.

---

## Category E: Data and System Reality

---

**Q12: Is Ironclad used to track all 300 contracts per quarter throughout their lifecycle?**

For WS2 and WS3 cases, yes — everything that goes to negotiation or escalation is in Ironclad. For WS1 standard-path contracts that we accept as-is, honestly, it's inconsistent. Tom is supposed to log them, but some of the quick-turnaround standard contracts end up tracked in a spreadsheet or just filed without a full Ironclad case record. If you asked me what percentage of the 300 have complete Ironclad records end-to-end, I'd want to check before I gave you a number. It's a known gap we've been meaning to address.

---

**Q13: Do vendor contracts always arrive as Word (.docx) attachments to Outlook emails?**

Word via Outlook is the standard path and the majority. PDFs are the main exception — I'd say roughly 10 to 15 percent as I mentioned, mostly from larger enterprise vendors. Scanned documents are rare but not unheard of; some older-school procurement teams still do that. We don't have a vendor portal; everything comes through Outlook. If a vendor sends a SharePoint link, Tom asks them to attach the document — you saw that thread in the briefing materials.

---

**Q14: Does Salesforce contain a procurement record for every inbound vendor contract before it reaches Legal?**

No. Salesforce is the source for contracts tied to a live sales opportunity — prospects and renewals where there's a commercial account. But we also receive vendor paper from suppliers, SaaS tools the team is procuring, infrastructure vendors — those often come through directly to Legal without any Salesforce record because there's no sales relationship. I'd estimate roughly 70 percent of our inbound volume has a corresponding Salesforce opportunity; the rest is supplier-side procurement that bypasses sales entirely.

---

## Category F: Organisational and Trust Context

---

**Q15: What level of autonomous classification would you accept in production for the standard path?**

Not fully autonomous from day one — no. I'd want a period where Tom reviews everything the agent produces before any classification is committed as final. Call it three to six months. Not because I don't think the technology can work, but because I need to know what the failure modes actually look like before I take Tom out of the loop on 210 contracts a quarter. What I'd accept: the agent does the classification, presents it to Tom in a format that makes his review faster, and Tom approves or overrides. When the override rate has been below a threshold we agree on for two or three consecutive quarters, we discuss expanding autonomy. I'm not signing off on a design where the agent routes contracts to "accept" and no one checks until we do a quarterly audit.

---

**Q16: The DPDI Act playbook update has been discussed since March but not completed. Is there a named owner and a realistic completion date?**

*[pause — slightly uncomfortable]*

No named owner and no committed date, if I'm honest. I'm the person who needs to own it, and I haven't done it. Sarah and I had a conversation in March when the Q1 guidance came out, I made a note, and then CRO pressure and quarter-end ate the calendar. It's not forgotten — it's on my desk literally, on the sticky note — but it doesn't have a deadline attached to it. If you're telling me this is a deployment gate for the agent, then you've just given me the deadline I needed. I'd say I could have a draft update to the DPA section within three weeks if I prioritise it. I'd want Sarah to review it before it's published.

---

**Q17: When Tom overrides the agent's classification, would you want that override recorded as a training signal for model improvement, or does creating a correction log create a discoverability or liability concern?**

That's a question I'd want to think about carefully, and I'd probably want to speak to one of the commercial lawyers before answering definitively. My instinct is that there's a difference between an aggregate accuracy metric — "the agent made X classification errors this quarter on clause type Y" — which I'd be comfortable with, and a granular record of "in contract IRONCLAD-0234, the agent said COMPLIANT, Tom said MAJOR_DEVIATION" — which could be discoverable and could be used to argue that we knew the system was misclassifying and proceeded anyway. I wouldn't want a detailed per-contract correction log sitting in our system without legal advice on how it would be treated in litigation. If you need correction signals for calibration, I'd want to understand the minimum necessary data and whether it can be held separately from the Ironclad case record.

---

## Summary — Amelia's 3 Key Messages

1. **The sign-off audit trail is my single biggest practical gap.** I've said the rule — no counteroffer without a named lawyer's sign-off — but the recording of that sign-off currently lives in email, not in Ironclad. If your system is going to enforce the governance gate structurally, that's actually going to force us to formalise something we should have formalised years ago. I'm open to that. But you need to design around the current state, not around an assumption that Ironclad already has a sign-off field, because it doesn't.

2. **The DPDI update is on my critical path and I now have a reason to finish it.** Three weeks, draft plus Sarah's review. If you make me the deployment gate, I'll act like one.

3. **Start with Tom in the loop.** I'm not unreasonable about what the technology can do — the CRO pressure is real and I understand the case for automation. But I need to see the failure modes before I trust the system with 210 contracts a quarter running without review. Give me a supervised phase, give me an override rate that gives me confidence, and then we can talk about expanding autonomy. Don't ask me to skip that step.
