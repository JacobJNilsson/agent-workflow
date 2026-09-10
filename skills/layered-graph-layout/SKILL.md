---
name: layered-graph-layout
description: Rules for a readable drawing of a directed graph around one root node, with many nodes per rank. Use when a mermaid or dagre drawing of a dependency, flow, or hierarchy graph is unreadable, when the user asks for a more structured graph, or when edges must stay traceable in a large graph. Covers node order, rank columns, edge routing, and the ELK port mechanism that mermaid cannot express.
---

# Layered graph layout

Rules for drawing a directed graph around one root node as columns. The rules
came from a graph with 115 nodes and 119 edges, where a default mermaid
drawing was one tall strip with crossing lines. Apply them to any graph with
a root, a direction (upstream feeds downstream), and many nodes per rank.

## Terms

- **Root**: the node the drawing is about.
- **Rank**: a node's shortest distance from the root along edges. Upstream
  ranks are positive, downstream ranks are negative. The shortest path sets
  the rank. A node that feeds both the root and a rank 1 node is rank 1.
- **Feeder**: the source node of an edge. **Receiver**: the target node.
- **Column**: all nodes of one rank, drawn as a full-height band with a
  label.
- **Cluster**: a receiver together with the feeders that stand in its own
  rank.

## The rules

Layout:

1. One column per rank. Upstream to the left of the root, downstream to the
   right. Draw each column as a full-height band with its label.
2. Every edge is a line. Never drop an edge or replace it with a marker.
3. Two lines may share a segment only when they have the same receiver.
   Lines to different receivers never share a segment, horizontal or
   vertical. A reader who follows a line always reaches exactly one node.
4. Lines into the same receiver join into one line before they reach it.
5. Every line leaves the feeder on the right side of its box and enters the
   receiver on the left side of its box.
6. One line colour, no arrowheads, rounded corners. The columns give the
   direction.
7. Every node except the root is a link to its own drawing, when such a page
   exists. A link keeps the query string.
8. A click on a line highlights it in a second colour and raises it above
   the other lines. A second click, or a click on empty space, clears it.
   Give every line a wide invisible hit path, a 1.5 px line is hard to hit.

Order within a column:

9. Build column N from column N-1. Walk column N-1 from the top. For each
   node, emit its rank N feeders in sibling order. The feeders of the node
   that stands higher stand higher.
10. A feeder that also feeds a node in its own rank belongs to that node's
   cluster. Emit it directly after that node, before the next group, and
   apply the same rule to its own same-rank feeders. A same-rank circle that
   no walk reaches comes last in the column, in sibling order.
11. Sibling order: a node whose direct feeders are all already placed comes
    first. A feeder is placed when a node that stands higher in this column
    also has it. Then nodes with more direct feeders first, then case
    insensitive name, then id. Nodes with no feeders come last. Pick the
    siblings one at a time, because each pick places more feeders.
12. Downstream mirrors every rule, with receivers in place of feeders.
13. The output is deterministic. Same graph, same drawing.

Vertical placement:

14. A node stands as high as it can, subject to four limits. It never
    stands above the node above it in its column, above the receiver it is
    grouped under, above the first feeder grouped under it, or
    level with or above the last node of the feeder group of the node
    above it. The feeder group is the run the node emitted into the next
    column, grouped feeders plus their same-rank clusters, not every
    feeder. A limit that points at a feeder placed elsewhere can point
    below the node, and the loop then never settles. Start every node at
    the top and raise the limits to a fixed point, it settles in a few
    passes. Cap the passes and report a failure to settle. A receiver then stands level with its first
    feeder, and no node stands inside another node's feeder group. The
    fourth limit is what holds a node without feeders down.
15. Boxes align on the edge that faces the root. Upstream columns align on
    their right edge, downstream columns on their left edge. This needs a
    root, a graph without one has no facing side.

## Why each rule exists

- Rule 1 and 9: a free layered layout chooses the column by the longest
  path and the row by edge straightness. Both move related nodes apart.
- Rule 3: a merged bus that also carries lines to another node makes it
  impossible to see which lines end where. One test graph had a receiver
  with ten feeders next to a bus of 75 lines to the root.
- Rule 5: a line that enters a box on its right side reads as a line that
  leaves it.
- Rule 10: a node that feeds the root and a rank 1 node stands with that
  node, not with the root's other 70 feeders.
- Rule 11: the nodes with no feeders are the long tail. Together at the end
  they read as a list, mixed in they hide the structure.

## What mermaid can and cannot do

Mermaid with the ELK renderer gives columns and orthogonal lines. It cannot
give rules 3, 4 and 5 together:

- `mergeEdges` merges at the source port as well as the target port, so a
  node with two receivers gets one shared segment for both lines. That
  breaks rule 3.
- Without `mergeEdges` every line gets its own slot, which breaks rule 4 and
  doubles the width.
- Mermaid exposes five ELK options and no ports, so there is no middle
  ground.
- Mermaid subgraphs pack each group into a compact box and place the box by
  its barycentre, so a subgraph per rank pulls nodes away from their
  receivers. Do not use subgraphs for ranks.

If the goal is only "more structured", mermaid with the ELK renderer,
`considerModelOrder: NODES_AND_EDGES` and `forceNodeModelOrder: true`, and
nodes emitted in the order of rule 9 to 12, is a large step. Load ELK from
the package's own dist file. The jsdelivr `+esm` bundle silently ignores
the layout loader.

For the full rule set call elkjs directly and draw the SVG yourself. That
is about 250 lines of page script.

## The ELK mechanism for rules 3 to 5

- Give every node one input port on the WEST side and one output port PER
  EDGE on the EAST side, `elk.portConstraints: FIXED_SIDE`. ELK's router
  bundles every edge on one port into one hyperedge, so edges into one
  receiver merge, and edges out of one feeder to different receivers never
  touch.
- Columns from rank: set `x = (maxRank - rank) * 400` on every node and use
  `elk.layered.layering.strategy: INTERACTIVE` and
  `elk.layered.cycleBreaking.strategy: INTERACTIVE`.
- Rows from rule 14: compute y yourself, pass `x` and `y` on every node,
  and set `elk.layered.nodePlacement.strategy: INTERACTIVE`. ELK keeps
  the positions exactly and still routes the edges.
- Order from the model: `elk.layered.considerModelOrder.strategy:
  NODES_AND_EDGES` and `elk.layered.crossingMinimization.forceNodeModelOrder:
  true`. Emit the nodes in the order of rule 9 to 12.
- Width: `elk.layered.spacing.edgeEdgeBetweenLayers: 4` keeps unmerged
  lines cheap.
- Rounded corners: shorten each segment by the radius at a bend and join
  the ends with a quadratic curve through the bend point. Skip zero length
  segments.
- `nodePlacement.strategy: LINEAR_SEGMENTS` throws in the mermaid ELK
  adapter. Use `BRANDES_KOEPF` with `BALANCED` alignment.

Same-rank edges (rule 10 makes them common): a layered layout has no place
for an edge inside a column. Keep them out of the ELK graph and draw them
after layout. Leave the feeder near a box corner, with a small offset per
receiver so two lines from one feeder stay apart. Run along the right gap
in a slot shared per receiver. Cross the column 4 px below the receiver's
box, so every receiver has its own crossing height. Run along the left gap
in the same shared slot. Enter the receiver at its input port. Reserve the
slot room on both sides of every column with `edgeNodeBetweenLayers` and
`nodeNodeBetweenLayers`.

## Checks before you call it done

- Render the real data, not a sample. The failures above only showed on a
  node with ten feeders.
- Script a check: collect every horizontal and vertical segment, and report
  any pair with different receivers that overlap within 1.5 px.
- Zoom to 100 percent at the busiest receiver and at the root.
- Confirm the order in the second and third column follows the first, not
  the depth-first walk.
- Confirm a node that feeds two receivers in different ranks stands with
  the receiver in its own rank.
- Confirm the page reports a failure to load the layout library instead of
  a blank page.
- Confirm every receiver sits level with its first feeder and no feeder
  group interleaves with another.
