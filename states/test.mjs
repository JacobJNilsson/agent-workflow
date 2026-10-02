/**
 * Test the state validator through its own command line.
 *
 * Each case is a declaration that must pass or fail, and the words the report
 * has to contain. The cases are the checks, so a check with no case is a
 * check nobody runs.
 */

import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const PROSE = "The author runs spec, then implement, then review, then unslop, then pr, then wait, then done.";

const cases = [
	{
		name: "a machine with no terminal state never finishes",
		declaration: "entry a\nstate a waits=none\nstate b waits=none\na -> b when=\"work done\"\n",
		expect: ["no state is terminal"],
	},
	{
		name: "a loop with no cap can run forever",
		declaration: "entry a\nstate a waits=none\nstate b waits=none\nstate done waits=none terminal\na -> b when=\"go\"\nb -> a when=\"back\"\na -> done when=\"ok\"\n",
		expect: ["loop a -> b has no cap"],
	},
	{
		name: "a state with no way out is a dead end",
		declaration: "entry a\nstate a waits=none\nstate b waits=none\nstate done waits=none terminal\na -> done when=\"ok\"\n",
		expect: ['state "b" has no way out'],
	},
	{
		name: "an edge into a state nobody declared is a typo",
		declaration: "entry a\nstate a waits=none\nstate done waits=none terminal\na -> dnoe when=\"typo\"\na -> done when=\"ok\"\n",
		expect: ['edge enters unknown state "dnoe"'],
	},
	{
		name: "a misspelled key is caught instead of ignored",
		declaration: "entry a\nstate a waits=none cap=three\nstate done waits=none terminal\na -> done when=\"ok\"\n",
		expect: ["cap must be a positive whole number"],
	},
	{
		name: "a state the prose never mentions has drifted",
		declaration: `entry spec\nstate spec waits=none\nstate mystery waits=none\nstate done waits=none terminal\nspec -> mystery when="go"\nmystery -> done when="ok"\nprose PROSE\n`,
		prose: PROSE,
		expect: ['state "mystery" is in the machine but not in the prose'],
	},
	{
		name: "an unreachable state has no entry",
		declaration: "entry a\nstate a waits=none\nstate orphan waits=none\nstate done waits=none terminal\na -> done when=\"ok\"\n",
		expect: ['state "orphan" cannot be reached'],
	},
	{
		name: "an entry naming a state nobody declared is caught",
		declaration: "entry nowhere\nstate a waits=none\nstate done waits=none terminal\na -> done when=\"ok\"\n",
		expect: ['entry names unknown state "nowhere"'],
	},
	{
		name: "a capped loop passes",
		declaration: "entry a\nstate a waits=none\nstate done waits=none terminal\na -> a when=\"again\" cap=3\na -> done when=\"ok\"\n",
		expect: [],
	},
	{
		name: "a second entry reaches states the first one cannot",
		declaration: "entry spec\nentry review\nstate spec waits=none\nstate review waits=none\nstate done waits=none terminal\nspec -> review when=\"approved\"\nreview -> done when=\"clean\"\n",
		expect: [],
	},
];

let failed = 0;

for (const testCase of cases) {
	const dir = mkdtempSync(join(tmpdir(), "states-test-"));
	const declaration = testCase.declaration.replace("prose PROSE", "");
	const file = join(dir, "machine.states");
	writeFileSync(file, declaration);

	const args = testCase.prose
		? [file, "--prose", writeProse(dir, testCase.prose)]
		: [file];

	let output = "";
	let status = 0;
	try {
		output = execFileSync(process.execPath, [validator(), ...args], {
			encoding: "utf8",
			stdio: ["ignore", "pipe", "pipe"],
		});
	} catch (error) {
		status = error.status;
		output = error.stderr ?? "";
	}

	const ok = testCase.expect.every((word) => output.includes(word)) && (status === 0) === (testCase.expect.length === 0);
	if (!ok) failed++;
	process.stdout.write(`${ok ? "pass" : "FAIL"}  ${testCase.name}\n`);
	if (!ok) process.stdout.write(`      got: ${output.trim().split("\n").join(" | ")}\n`);
}

function writeProse(dir, text) {
	const file = join(dir, "prose.md");
	writeFileSync(file, text);
	return file;
}

function validator() {
	return new URL("./validate-states.mjs", import.meta.url).pathname;
}

process.stdout.write(failed === 0 ? "\nall cases pass\n" : `\n${failed} case(s) failed\n`);
process.exit(failed === 0 ? 0 : 1);
