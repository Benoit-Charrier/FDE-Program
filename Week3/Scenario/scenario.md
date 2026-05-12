## 3. The MedFlex scenario

> **MedFlex** — healthcare staffing agency, 200 employees, 5-state US region. B2B with hospital systems and B2C with travel nurses.
>
> ### Current operations
>
> - **Hospitals submit shift requests** via email, portal, or phone.
> - **8 coordinators manually match nurses to shifts** based on credentials, proximity, availability, hospital preferences, nurse preferences.
> - **Compliance verification** — license checks, background, training certifications — done manually against state regulatory databases.
> - **~120 shift-matching decisions per coordinator per day.**
> - **Average time to fill: 4.2 hours.** Target: under 1 hour.
> - **Mismatch rate (wrong credentials for facility type): 7%.**
> - **No-show rate: 12%.**
>
> ### Your stakeholder — Marcus Reyes, CEO
>
> Just closed Series B. Board wants significant growth on the horizon of in 24 months. Two failed AI projects already (a chatbot hospital staff rejected; a recommendation engine nobody used). Background: operations + growth, not engineering. Tone: confident, time-pressured, results-oriented. Cuts off rambling questions. Respects FDEs who challenge framing with substance. 
>
> ### Engagement framing
>
> *"10x the business without 10x-ing the coordinators"* — in 8 weeks.
>
> ### What's in scope
>
> Design the agentic transformation of MedFlex's matching + compliance + coordination workflow. Architecture, agent decision points, capability specifications, ADRs, validation plan, build-loop response. Deliverables in §6.
>
> ### What's out of scope (named explicitly so the gate doesn't drift)
>
> - Building a hospital-facing portal for shift submission. They submit by email/portal/phone today; your engagement does not change that channel.
> - Building a nurse-facing mobile app. Nurses today are reached by phone, SMS, or email; same.
> - Pricing engine / margin optimisation. The agent matches; the pricing remains MedFlex's existing process.
> - Continuing-education renewal automation for nurses. Not in v1.
>
> **You are the FDE. Marcus is your point of contact through the engagement. Go.**

---