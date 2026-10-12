# Case study: building a course-accurate Linux trainer with Claude Code

**Who:** Betzalel Tusk, a student in DCOM 142 (Linux+ part 1) at the Community College of Baltimore County
**When:** October 10-12, 2026, three days before the DCOM 142 midterm
**Tools:** Claude Code in the Claude desktop app (Claude Opus 5.5 and Sonnet 5.5), Python's standard library, Brightspace's read-only API
**Result:** a 152-question terminal game where every question traces to the course's own slides, published as open source

## The problem

The DCOM 142 midterm covers Modules 1-5: Linux basics, users and groups, user configuration and sudo, standard permissions, and special permissions and ACLs. It is multiple choice, but there is also a hands-on practical, so knowing *about* a command isn't enough; you have to be able to type `usermod -aG wheel dcom` or `setfacl -m u:userA:r file1` from memory. Flashcards don't test that, and generic Linux quizzes cover a lot the course never taught.

## How it went

### 1. "What do we have going on this week?"
The session started as a planning question, not a coding one. Claude read the student's course calendars, assignments and announcements through Brightspace's read-only API in the desktop app's built-in browser. The student signed in themselves, and Claude never handled credentials. That turned up the DCOM 142 midterm on Wednesday the 14th and the deadlines around it, and Claude updated the study plan to match.

### 2. A review game for command syntax
The student asked for a command-line review game. The first version was a standard-library Python quiz with 140 questions and an answer matcher built to be fair rather than literal:
- `sudo` is optional
- quote style is ignored
- flag letters can come in any order (`-la` = `-al`)
- argument order still matters (`chown file alice` is wrong)

It also generated endless permission-math drills (octal ⇄ rwx, symbolic chmod, umask, SUID/SGID) and saved progress, weighting missed questions to come back more often.

### 3. Making it fun
The next request was "more colorful and interactive," with a Matrix-green cursor and input. That became:
- a digital-rain intro that decodes the title
- arrow-key menus
- "ACCESS GRANTED / ACCESS DENIED" feedback
- a word-by-word comparison of your answer against the expected one
- streaks, XP ranks and a 90-second lightning mode

### 4. Learning from mistakes
Two usability requests followed:
- an explanation every time an answer is wrong;
- pressing Enter after a wrong first try should count as the second attempt and reveal the answer, rather than just adding a blank line.

Every question got an explanation that breaks the command into its parts. The permission drills got step-by-step working, like "rwx = 4+2+1 = 7".

### 5. "Ensure all the questions are ones we covered in DCOM 142"
This was the most important step. The first question set was written from general Linux+ knowledge and a study guide, and the study guide itself admitted it added background beyond the slides. So Claude pulled the instructor's current Module 1-6 slide decks, the objectives pages and a new midterm review deck, and read them. It then:
- **Dropped topics the course hadn't taught yet:** package management and storage (18 questions), `cp`/`mv`/`rm`, `man -k`, `sudo -l`, the sticky bit's octal digit, ACL masks and others.
- **Added commands the slides do teach that the game was missing:** `usermod -e`, `getent passwd`, `killall -u`, `groupmod -g`, `chage -m 1 -M 120 -W 5`, `sudoedit`, `pkexec`, the exact sudoers line `kgarcia ALL=(root) /sbin/shutdown`, and the in-class chmod exercises.
- **Rebuilt the question bank:** it now has 152 questions, and only 26 of the original 140 survived word for word. Each question records its source slide, and the game shows it with the explanation.
- **Machine-checked the result:** for every question, the key command or phrase was searched for in the deck it cites. All 149 phrases were found; three Module 5 questions share evidence with their neighbors.
- **Caught a slide typo:** the Module 4 deck lists `chmod -r` for recursive, but the real option is `-R` (lowercase `-r` would remove read). The explanation now says so.

Module 6 (taught after the midterm) is in the game but kept out of the default rounds.

### 6. Publishing safely
The student asked to publish the project on GitHub. The project folder held things that should never be public:
- the instructors' slide decks and publisher textbook material (one marked "may not be posted to a publicly accessible website")
- the student's grades
- a class Teams meeting passcode

Claude flagged these before pushing anything, and the student chose to publish only the tools. One script had the student's four course-section IDs hard-coded. It was changed to discover courses from whoever is signed in, so the public version is generic. An MIT license and this case study came after.

## How quality was checked

Nothing was handed back untested. The checks grew with the project:

| Check | What it covers |
|---|---|
| Unit tests | the answer matcher (accepted variations and wrong answers), question-bank integrity, explanation coverage, course sources |
| Ground-truth comparison | all 4,096 permission modes compared against Python's `stat.filemode`; symbolic chmod checked for 14 expressions on all 512 starting modes |
| Scripted sessions | keystrokes piped through every menu, including hints, retries, skips, overrides, quitting mid-round and input ending without warning |
| Perfect-play bot | answers every question correctly, to test scoring, streak bonuses, XP, ranks and saving |
| Terminal emulator | interactive screens replayed through a small emulator and rendered to PNG, so the visuals could actually be looked at (the README screenshots come from it) |
| Source check | each question's key phrase searched for in the slide deck it cites |

### What the checks caught
- **A retry that didn't work:** a "try again" message that didn't actually allow a retry.
- **A pointless prompt:** skipping a question still asked "was yours actually valid?"
- **Lost quotes:** the answer comparison dropped quotes (`alias ll=ls -la`).
- **Wrong umask math:** a umask explanation that subtracted digit by digit, which gives the wrong answer for umask 037 on a file.
- **A giveaway hint:** a hint that revealed one-character answers.
- **Bugs in the test tools:** two in the test harness itself. Windows text-mode files turned carriage returns into newlines, and a patch script wrote raw control characters into source. Both were caught and fixed before they could hide real problems.

One mistake made it into the chat but not into the product. Claude reported "39 removed, 51 added" questions without counting. When the numbers were needed for this write-up, it recounted against the original list, found the claim was wrong, and corrected it. The real figure is that 26 of 140 questions survived word for word.

## Results

- **152 questions:** 132 from Modules 1-5, 20 from Module 6, with 200 accepted answer variants.
- **Fully traced:** every question has an explanation and a slide source.
- **No setup:** one file, Python standard library only, runs on Windows, macOS and Linux.
- **Open source:** read-only Brightspace helper scripts that work for any student, published under the MIT license.

## Lessons

- **Check against the source, not a summary.** The biggest accuracy gain came from reading the actual slides instead of trusting a study guide built from them.
- **Fair beats strict.** A matcher that accepts `sudo`, any quote style and any flag order keeps the game about knowing the command, not about guessing the exact string.
- **Look at it.** Rendering screens to images caught layout and harness bugs that text output never showed.
- **Count before you claim.** Even a passing remark in chat should be backed by a number someone computed.

## What's next

Modules 7-12 (file management commands, text editing, packages, storage) can be added the same way once their decks are posted: read the slides, write the questions, cite the slide, run the checks.
