---
name: website-copy-review
description: Reviews and rewrites the words on a website — headlines, lede, calls to action, feature and pricing copy, metadata and link previews. TRIGGER when the user asks to review, audit, critique, tighten, rewrite or improve the copy, text, wording, messaging or positioning of a site or landing page, or asks "does this page convert" or "act as a copywriter". Also tests that the conversion path works and that the claims match the real business. SKIP for visual design, layout, spacing, colour or motion work — use the impeccable skill for those.
---

# Copy Review

Review the words on a website. Find the copy that costs the owner a reader,
and the claims that are not true. Do not change files until the user approves
the findings.

The most expensive fault on a page is rarely a sentence. It is a call to
action that goes nowhere, or a promise the company cannot keep. Test for those
first.

## 1. Get a rubric before you form an opinion

Search the web for current guidance on landing page copy and on writing for
the web. State the rubric in three or four lines. Judge the page against that
rubric, not against taste.

Confirm these established findings and use them:

- People scan. They do not read.
- Copy that is concise, scannable and objective tests far better than
  promotional copy.
- A reader decides in about three seconds. The first screen must say what this
  is, who it is for, and what to do next.
- Lead with the benefit. A category name is not a benefit.
- One call to action, written as an action.

## 2. Read the source, not the rendered page

Read the page source, the metadata, the structured data and the image files
used in link previews. Read the README and the recent commits. The project
files tell you what the product does and which parts are unfinished.

## 3. Test the conversion path

Do this before you review one word. This step finds the faults that matter.

- Follow every call to action to its target. Confirm the target exists.
- If a call to action is an email address, check the MX records for that
  domain with `dig MX <domain>`. No MX record means the address receives no
  mail. Query two or three independent resolvers. Query a domain known to have
  mail, to prove your tool works.
- If a call to action is a form or a link, confirm the endpoint responds.
- Build the site and open it in a browser. Look at the first screen at desktop
  width and at 390 pixels. Measure widths and fits. Do not estimate them.
- Count the characters in the title tag and in the meta description. A search
  result cuts the description near 155 characters.
- Open the link preview image. Read the text drawn into the picture. Compare
  it to the current headline. Text inside an image goes stale, and then a
  shared link disagrees with the page.

Report what you tested and what you did not. If you cannot complete a test,
name the test that would prove the last step.

## 4. Check the claims against the real business

Copy makes promises. A promise that does not match how the company works is a
defect, not a question of style. You cannot read the delivery model out of the
code, so ask the user:

- Who does the setup? The customer, or your team?
- Who approves or accepts the output?
- What can a customer see, and what do they get?
- Is the service self-serve, or hands-on?
- What is true today, and what is planned?

Then look for these faults:

- The page says "you" for work the reader never does.
- The page rules out something the company actually does.
- The page promises access, a reply time or a deletion that nobody agreed to.
- The page names a feature that nobody has built.

## 5. Review the copy

- Headline: can a reader understand it in one pass? An ambiguous pronoun or a
  clever line costs a second reading.
- Opening paragraph: does it start with the job, or with a category label?
- Emphasis: three bold phrases in one paragraph emphasise nothing.
- Sentences longer than 25 words. Split them.
- Jargon: compare the vocabulary to the audience the page says it wants.
- Headings: a heading is read alone, at speed. A heading that needs decoding
  is in the wrong place. Move the good line into the paragraph below it.
- Lists: a list that holds two kinds of item needs two labels.
- Undefined nouns, above all in step one of any process.
- Repetition: two sections that explain the same mechanism. Make one say why.
- Consistency: the same promise must use the same words in the title tag, the
  headline, the preview image and the alt text.
- Objections: name what stops the reader from acting, then confirm the page
  answers it. Confidentiality, price, effort and time are the usual four.

## 6. Rules

- Rank by cost, not by ease. A broken conversion path outranks every wording
  note. Say so plainly.
- Never invent a fact about the product. If you need a fact you do not have,
  ask the user. If you must write without it, state the assumption where the
  user will see it, and repeat it in the commit message.
- Name what already works and must not change. A voice is expensive to build
  and easy to erase.
- Correct yourself when the evidence changes. Say what changed, then continue.

## 7. Output

Give the user:

1. A one-line verdict.
2. The findings in order of cost. For each one: the defect, what it costs the
   reader or the business, and the replacement text.
3. The claims that need the user's confirmation.
4. What you tested, and what stays unproven.

## 8. After approval

Apply the changes. Use one commit for each finding. Follow the
`commit-message` skill. In each message, state the problem, why it cost a
reader, and what the new text does.

Build the site and look at the result in a browser before you report success.
If a change needs a fact the user has not confirmed, say so in the commit
message and in your report.
