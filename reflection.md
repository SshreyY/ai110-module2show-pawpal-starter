# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before touching any code, I tried to think through what a real user would actually need to do with this app. I landed on three core actions:

1. **Set up their pet and owner info** — The user needs a way to tell the app who they are and basic details about their pet (name, age, any special needs). Without this, the scheduler has no context to work with. So this is really the starting point before anything else can happen.

2. **Add and edit care tasks** — This is the meat of the app. The user should be able to add tasks like a morning walk, medication, feeding, grooming, etc. Each task needs at least a duration (how long it takes) and a priority (how important it is). I also wanted users to be able to come back and edit or remove tasks, not just add them once and be stuck with them.

3. **Generate and view the daily plan** — Once the tasks are in, the user hits some kind of "plan my day" action and the app figures out what order to do things in based on time available and priority. The plan should actually display clearly so they can see what's scheduled and (ideally) understand why the app made those choices.

These three actions basically map to the whole flow: set up → build your task list → get your schedule. That's what shaped my initial class design.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
