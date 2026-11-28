---
name: unslop
description: Cut AI tells from any writing. Must always apply.
---

# Unslop

Edit text to remove AI patterns.

## Process

1. Scan for the patterns below.
2. Rewrite. Preserve meaning, match intended tone.
3. Self-audit: "What makes this obviously AI generated?" Fix remaining tells.

## Patterns to detect and fix

Rule numbers are stable ids that other skills cite. A removed rule leaves a gap.

### Content

3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Just say "is" or "has".
9. **"Not just X, but Y."** State the point directly instead.
10. **Rule of three.** Forcing ideas into groups of three. Use the natural number.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** Colons are fine before a list or example. Not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Curly quotes.** Replace with straight quotes.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

23. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that" gets deleted. "On its own" gets deleted, or replaced by what is left out: "answers his question on its own" becomes "answers his question", and "each step can be rolled back on its own" becomes "each step can be rolled back without the other".
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
25. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. **Prefer the plain word.** "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer.
32. **Mannered prose.** Metaphor or flourish where a literal phrase exists: aphorisms ("wire it or delete it"), rhetorical fragments for effect, personified code ("the plan holds it"), figurative verbs ("rides along", "stands on"), stock framing phrases. "A dial worth turning" becomes "a parameter worth varying". Say what you mean. Rule 26 covers the metaphor nouns.
33. **Over-compression.** Dropped articles, verbless fragments, symbol-speak, and abbreviations that make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs, and spell out arrows and abbreviations.
34. **"Of" chains and bare names.** Identifiers used as bare nouns, stacked "of" phrases, and nouns made from verbs. "inserts the populate job of rollout in the transaction of repo. A rollback of that transaction also removes the job." becomes "inserts the rollout's populate job inside repo's transaction, so the job disappears if that transaction rolls back." Use the possessive, give the noun its article, and turn "a rollback of" into "if it rolls back".

### Order

35. **Answer last.** A reply restates the problem, walks through the diagnosis, and lays out proof before it reaches the decision. In a reply the reader already has the background. Lead with the decision. Then keep only the reason that would change whether the reader agrees, usually one fact they lack. "You're right that the cache is stale. I traced it to the TTL in `config.go` and checked staging. So I'd lower the TTL." becomes "I'd lower the TTL in `config.go` to 60 seconds. Staging shows no extra load at that value." Each sentence can read fine alone, so check the order of the whole reply.

### Staging

36. **One-line closers.** A short sentence or paragraph repeats the point just made: "That is the real win.", "That distinction matters.", "Let that sink in." The same closer after every section counts too. So do a sentence that names what an example just showed ("This shows the importance of tests."), a row of fragments ("No config. No setup. No waiting."), and a final "Ultimately" that restates the verdict. Cut the closer. Keep a short sentence only when it adds a new fact or consequence. Merge a row of fragments into one sentence with a claim: "It runs without a config file or a setup step."
37. **Staged openers.** A sentence announces the point instead of making it: "Let's dive in", "Here's the thing", "Here's what you need to know", "Honestly?", "Real talk". "The part" does the same work: "the hard part is X" stages X. "Here's the thing: the migration locks the table." becomes "The migration locks the table." Name the thing or state it. A literal part, such as one part of a multipart upload, is fine.
38. **Sayings that sound deep.** "The real question is", "at its core", "what really matters", "the heart of the matter", "X is the language of Y", "X becomes a trap". These dress an ordinary point as a hidden truth. "At its core, the real issue is trust." becomes the specific claim: "Users distrust the totals because the export rounds differently from the UI." Rule 32 covers aphorisms in general.
39. **Arguing with no one.** "To be clear", "I'm not saying", "This isn't about", "Don't get me wrong", "A tempting approach would be", "You might think... but". The text rejects an objection or an option that nobody raised, usually a leftover from an earlier draft. "A tempting approach would be to restart the service nightly, but that drops sessions. Tokens rotate in place." becomes "Tokens rotate in place." Keep an objection the text attributes to someone, and an option a reader would really weigh.

### Inflation

40. **Inflated significance.** "marks a pivotal moment", "plays a key role", "reflects a broader trend", "lasting legacy", "setting the stage for", a "Challenges and outlook" section. The text says an ordinary fact changed history or promises a future. "The team adopted Postgres in 2021, marking a pivotal shift in its data strategy." becomes "The team moved to Postgres in 2021." Keep the fact and drop the significance. Rule 25 covers the closing paragraph.
41. **Sales language.** "nestled", "in the heart of", "breathtaking", "renowned", "groundbreaking", "rich heritage", "commitment to", "diverse array". The text reads like an ad. "A renowned library with a diverse array of features" becomes "a library with plugins for auth, caching, and logging". State what the thing is and has.
42. **Prestige lists.** A list of outlets that cited someone, a follower count, or "featured in" stands in for what was said. "Her work has been cited by Wired, the BBC, and The Verge." becomes the claim itself, with its source: "In a 2024 Wired interview, she argued that..." If you don't know what the source said, cut the list. Rule 5 covers unnamed authorities.
43. **Vague connection.** "associated with", "in connection with", "linked to", "tied to". The text says two things relate without saying how. "He is associated with the project." hides whether he founded it, funds it, or filed one bug. Name the relation: "He maintains the project." If you don't know it, keep the vague word rather than guess.

### Structure

44. **Repeated sentence openings.** Several sentences in a row start with the same subject. "The parser reads the file. The parser checks the header. The parser returns the rows." becomes "The parser reads the file, checks the header, and returns the rows." Merge the sentences or begin one with the action. Don't swap in a synonym for the subject, because rule 11 still applies.
45. **Hyphens after the noun.** A compound modifier keeps its hyphen before the noun and drops it after. "A well-documented API" is right. "The API is well-documented" becomes "The API is well documented." Words the dictionary always hyphenates, such as "third-party", keep the hyphen everywhere.
46. **Decorative structure.** A horizontal rule between every section, a top heading that repeats the document title, and headings written for effect. "## The decision, on one page" becomes "## How the three options compare". Name what the section holds, and let the title stand once. Rules 17 and 18 cover title case and emojis.
47. **Heading repeated in the first sentence.** A heading is followed by a one-line paragraph that restates it: "## Performance", then "Speed matters.", then the content. Delete the restating line and start with the content.

### Leftovers

48. **Knowledge-limit disclaimers and guesses.** "as of my last update", "based on available information", "not widely documented", "it is believed that", "likely grew up in". The text says where its knowledge ends, or fills a gap with a plausible guess. "Details about the founding are limited, but it likely started in the 1990s." becomes "The sources don't give a founding date." Or cut the sentence.
49. **Writing about the document.** The text describes itself instead of its subject. It says what it replaced ("added to replace the old sleep loop"), how it was put together ("compiled from vendor pages"), or a layout the reader can see ("the table below compares"). "The retry wrapper was added to replace the old sleep loop." becomes "The retry wrapper backs off exponentially, up to five tries." Mention earlier versions only in changelogs and migration guides. Keep a source credit the reader can follow and a caveat that changes what the reader does.

Source: the pstack `unslop` skill (github.com/cursor/plugins, MIT). Rules 35 to 49 adapt humanizer v4 (github.com/blader/humanizer, MIT).
