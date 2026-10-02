#!/usr/bin/env node
/**
 * Check a state declaration against the rules a workflow has to hold.
 *
 * A declaration is a plain text block. One line per state, one per edge:
 *
 *   prose ../../skills/way-of-working/SKILL.md
 *
 *   entry plan
 *   entry review
 *
 *   state plan     waits=human  cap=5
 *   state done     terminal
 *
 *   plan -> review  when="plan approved"  cap=3
 *
 * The point is not to run the workflow. It is to stop the machine and the
 * prose from drifting apart. Every check is a way the two have drifted
 * before.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const STATE_KEYS = new Set(["waits", "cap", "terminal"]);
const EDGE_KEYS = new Set(["when", "cap", "human", "note"]);

/** Pull the declaration block out of a markdown file, or take the file as is. */
export function extract(raw) {
	const fenced = raw.match(/```states\n([\s\S]*?)```/);
	return fenced ? fenced[1] : raw;
}

/** Split a line into words, keeping a double-quoted value as one word. */
function tokenize(line) {
	return line.match(/[^\s"]+="[^"]*"|"[^"]*"|[^\s"]+/g) ?? [];
}

function unquote(word) {
	return word.startsWith('"') ? word.slice(1, -1) : word;
}

function isPositiveInteger(value) {
	return /^\d+$/.test(value) && Number(value) > 0;
}

/** Parse declaration lines into states and edges. Unknown keys are errors. */
export function parse(text) {
	const states = new Map();
	const entries = [];
	const edges = [];
	const errors = [];

	for (const [index, line] of text.split("\n").entries()) {
		const at = index + 1;
		const trimmed = line.trim();
		if (!trimmed || trimmed.startsWith("#") || trimmed.startsWith("prose ")) continue;

		const entry = trimmed.match(/^entry\s+([a-z][a-z0-9-]*)$/);
		if (entry) {
			entries.push(entry[1]);
			continue;
		}

		const state = trimmed.match(/^state\s+([a-z][a-z0-9-]*)\s*(.*)$/);
		if (state) {
			const attrs = readAttributes(tokenize(state[2]), at, STATE_KEYS, errors);
			if (attrs.cap !== undefined && !isPositiveInteger(attrs.cap)) {
				errors.push(`line ${at}: cap must be a positive whole number`);
			}
			if (states.has(state[1])) errors.push(`line ${at}: state "${state[1]}" declared twice`);
			states.set(state[1], {
				name: state[1],
				waits: attrs.waits,
				cap: attrs.cap === undefined ? undefined : Number(attrs.cap),
				terminal: "terminal" in attrs,
			});
			continue;
		}

		const edge = trimmed.match(/^([a-z][a-z0-9-]*)\s*->\s*([a-z][a-z0-9-]*)\s+(.*)$/);
		if (edge) {
			const attrs = readAttributes(tokenize(edge[3]), at, EDGE_KEYS, errors);
			if (attrs.cap !== undefined && !isPositiveInteger(attrs.cap)) {
				errors.push(`line ${at}: cap must be a positive whole number`);
			}
			if (!attrs.when) errors.push(`line ${at}: edge needs a when= clause`);
			edges.push({
				from: edge[1],
				to: edge[2],
				when: attrs.when,
				cap: attrs.cap === undefined ? undefined : Number(attrs.cap),
				human: "human" in attrs,
				note: attrs.note,
			});
			continue;
		}

		errors.push(`line ${at}: cannot read "${trimmed}"`);
	}

	return { states, entries, edges, errors };
}

function readAttributes(words, at, allowed, errors) {
	const attrs = {};
	for (const word of words) {
		const [key, ...rest] = word.split("=");
		if (!allowed.has(key)) {
			errors.push(`line ${at}: unknown key "${key}"`);
			continue;
		}
		attrs[key] = rest.length === 0 ? true : unquote(rest.join("="));
	}
	return attrs;
}

/** Every simple cycle in the edge list, as a list of state names. */
export function cycles(states, edges) {
	const outgoing = new Map([...states.keys()].map((name) => [name, []]));
	for (const edge of edges) if (outgoing.has(edge.from)) outgoing.get(edge.from).push(edge.to);

	const found = new Set();
	const stack = [];
	const onStack = new Set();
	const settled = new Set();

	const visit = (node) => {
		stack.push(node);
		onStack.add(node);
		for (const next of outgoing.get(node) ?? []) {
			if (onStack.has(next)) {
				found.add(rotate(stack.slice(stack.indexOf(next))).join(" "));
			} else if (!settled.has(next)) {
				visit(next);
			}
		}
		stack.pop();
		onStack.delete(node);
		settled.add(node);
	};

	for (const name of states.keys()) if (!settled.has(name)) visit(name);
	return [...found].map((key) => key.split(" "));
}

/** Rotate a cycle so its smallest name comes first, so the same loop matches. */
function rotate(cycle) {
	const smallest = cycle.indexOf([...cycle].sort()[0]);
	return [...cycle.slice(smallest), ...cycle.slice(0, smallest)];
}

/** Does any state or edge inside the cycle declare a cap? */
function cycleIsBounded(cycle, edges, states) {
	return cycle.some(
		(name) =>
			states.get(name)?.cap !== undefined ||
			edges.some(
				(edge) => edge.cap !== undefined && cycle.includes(edge.from) && cycle.includes(edge.to),
			),
	);
}

function reachableFrom(entry, edges) {
	const seen = new Set();
	const walk = (name) => {
		if (seen.has(name)) return;
		seen.add(name);
		for (const edge of edges) if (edge.from === name) walk(edge.to);
	};
	walk(entry);
	return seen;
}

/**
 * Report every way the declaration and the prose can disagree.
 * `prose` is the text of the file the `prose` line points at, or null.
 */
export function check(declaration, prose) {
	const problems = [];
	const { states, entries, edges, errors } = parse(declaration);
	problems.push(...errors);
	if (states.size === 0) return problems;

	for (const entry of entries) {
		if (!states.has(entry)) problems.push(`entry names unknown state "${entry}"`);
	}
	for (const edge of edges) {
		if (!states.has(edge.from)) problems.push(`edge leaves unknown state "${edge.from}"`);
		if (!states.has(edge.to)) problems.push(`edge enters unknown state "${edge.to}"`);
	}

	for (const state of states.values()) {
		if (state.terminal) continue;
		if (!edges.some((edge) => edge.from === state.name)) {
			problems.push(`state "${state.name}" has no way out`);
		}
	}

	if (![...states.values()].some((state) => state.terminal)) {
		problems.push("no state is terminal, so the machine never finishes");
	}

	for (const cycle of cycles(states, edges)) {
		if (!cycleIsBounded(cycle, edges, states)) {
			problems.push(`loop ${cycle.join(" -> ")} has no cap, so it can run forever`);
		}
	}

	const reachable = new Set();
	for (const entry of entries.length > 0 ? entries : [...states.keys()].slice(0, 1)) {
		for (const name of reachableFrom(entry, edges)) reachable.add(name);
	}
	for (const name of states.keys()) {
		if (!reachable.has(name)) problems.push(`state "${name}" cannot be reached`);
	}

	if (prose) {
		for (const name of states.keys()) {
			if (!prose.includes(name)) {
				problems.push(`state "${name}" is in the machine but not in the prose`);
			}
		}
	}

	return problems;
}

function readProse(file, raw) {
	const pointer = extract(raw).match(/prose\s+(\S+)/);
	if (!pointer) return undefined;
	const base = pathToFileURL(file);
	try {
		return readFileSync(fileURLToPath(new URL(pointer[1], base)), "utf8");
	} catch {
		process.stderr.write(`cannot read prose file ${pointer[1]}\n`);
		process.exit(2);
	}
}

function main(argv) {
	const target = argv[2];
	if (!target) {
		process.stderr.write("usage: validate-states.mjs <declaration>\n");
		return 2;
	}
	const file = resolve(target);
	const raw = readFileSync(file, "utf8");
	const override = argv.indexOf("--prose");
	const prose =
		override > -1
			? readFileSync(resolve(argv[override + 1]), "utf8")
			: readProse(file, raw);

	const problems = check(extract(raw), prose);
	if (problems.length === 0) {
		process.stdout.write(`ok: ${target}\n`);
		return 0;
	}
	for (const problem of problems) process.stderr.write(`${target}: ${problem}\n`);
	return 1;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) process.exit(main(process.argv));
