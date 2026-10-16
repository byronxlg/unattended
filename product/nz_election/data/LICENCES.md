# Dataset licences

Polls, averages, theoretical seats and their CSV siblings: CC BY-SA 4.0.
Source: Wikipedia contributors. CC BY-SA 4.0. Parsed and averaged by this project.
Revision: https://en.wikipedia.org/w/index.php?oldid=1380524613
Contributor history: https://en.wikipedia.org/w/index.php?title=Opinion_polling_for_the_2026_New_Zealand_general_election&action=history
Licence: https://creativecommons.org/licenses/by-sa/4.0/

Source: Electoral Commission. Copyright Electoral Commission. No open licence stated.
EC captures validate the 2023 calculation and supply the explicitly labelled electorate assumption.
The poll licence does not relicense EC material.

Method: Electoral Act 1993, sections 191-193. Legislation has no copyright.
Validation data: Electoral Commission.

CSV contract: provenance columns repeat on each row. Nested values use canonical JSON
in *_json columns. Empty scalar cells mean null; booleans are true/false. Counts mean
payload records. Manifest hashes and sizes exclude self-reference.
Poll totals are the sum of each row's shares divided by its scale, including Others;
no input is forced to total 100. Fixture runs are offline verification, not live polling.
