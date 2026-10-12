# dcom142-cmdquiz

A Matrix-themed terminal game for drilling the Linux commands from **DCOM 142** (Linux+ part 1, CompTIA Linux+ XK0-006) at the Community College of Baltimore County. You get a task, type the command from memory, and the game tells you exactly what you got wrong and why.

![Intro: the title decodes out of digital rain](docs/intro.png)

Built by a DCOM 142 student with [Claude Code](https://claude.com/claude-code) to study for the midterm. Not affiliated with or endorsed by CCBC.

## Run it

```bash
python cmdquiz.py
```

You need Python 3.8 or newer and nothing else (standard library only). It works on Windows, macOS and Linux and looks best in Windows Terminal or any terminal with 24-bit color.

| Flag | Effect |
|---|---|
| `--no-intro` | skip the digital-rain intro |
| `--no-anim` | turn off all animation |
| `--plain` | ASCII only, for terminals that show boxes instead of symbols |

Progress and XP are saved to `.cmdquiz_progress.json` next to the script.

## How it plays

![Main menu](docs/menu.png)

- **Arrow keys** (or j/k) and Enter move through the menus, or press the option's number.
- **Type the command** at the green prompt. Your text and cursor are Matrix green. Typing `sudo` is optional, quote style doesn't matter, and `-la` counts the same as `-al`, but argument order does matter (`chown file alice` is wrong).
- **One retry.** A wrong answer gets one more try. Press **Enter** on that second try to see the answer straight away. `?` gives a hint and `skip` reveals the answer.
- **On a miss** you get a word-by-word comparison (green matches, red is what you typed wrong, yellow is what was expected), the accepted alternatives, an explanation, and the slide it comes from. If your answer was actually valid, you can count it anyway.

![A wrong answer with the explanation panel](docs/wrong-answer.png)

**Modes:**
- **Quick round:** 10 mixed questions.
- **Midterm blitz:** 20 questions from Modules 1-5.
- **Lightning:** 90 seconds, as many as you can.
- **Pick topics:** a checklist of topics to drill.
- **Permission drills:** endless generated octal / rwx / symbolic chmod / umask / SUID-SGID math, with the working shown step by step.
- **Missed questions:** only the ones you've gotten wrong.

Missed questions come up more often; a question counts as mastered after you get it right twice in a row. Streaks earn bonus points and XP moves you up six ranks, from Script Kiddie to Kernel Hacker.

![Round complete](docs/round-complete.png)
![Progress by topic](docs/progress.png)

## Where the questions come from

All **152 questions** are from the Fall 2026 DCOM 142 course itself: the instructor's Module 1-6 slide decks and their in-class exercises, the Module Learning Objectives pages, and the midterm review deck. Each question records its source, which is shown with the explanation.

| Topic | Course module | Questions |
|---|---|---|
| basics | Module 1: Linux basics, Vim/nano, su/sudo, troubleshooting method | 29 |
| accounts | Module 2: users, groups, /etc/passwd, /etc/shadow, /etc/group, PAM, login history | 28 |
| shell | Module 3: prompt and profile files, variables, chage/passwd policy, sudoers, wheel, polkit | 33 |
| perms | Module 4: chmod (octal and symbolic), umask, chown/chgrp, chattr/lsattr | 23 |
| special | Module 5: SUID, SGID, sticky bit | 11 |
| acl | Module 5: getfacl / setfacl | 8 |
| files, text | Module 6 (taught after the midterm): links, find, stat, echo, tr, wc, sort, cut, sdiff, awk, sed | 20 |

Module 6 questions stay out of the default rounds until you pick them under **Pick topics**.

The repo does **not** include any course files (slides, syllabi, textbook material). The questions and explanations are written from scratch and point to the slide rather than copying it.

## Brightspace helper scripts

`brightspace/` holds three small scripts used while building this. You paste them into the browser console while logged in to your own Brightspace (D2L) session. They only send GET requests, authenticate with the session you are already signed in on, and discover courses from your own enrollments.

- **`thisweek.js`:** lists what's due this week and coming up (calendar events, assignments, quizzes, recent announcements) across all your courses, and marks items that already have a grade.
- **`probe.js`:** checks which Valence API versions your school exposes and lists your enrollments.
- **`harvest.js`:** exports your own course metadata (modules, assignments, grades, announcements, calendar) to JSON and can download course files for offline study. Keep anything it downloads private: course materials belong to your instructors and publishers.

## How it was made with Claude

This was built in one long conversation in the Code tab of the Claude desktop app, with Claude (Opus 5.5 and Sonnet 5.5) writing the code and the student directing, playing and giving feedback.

1. **Starting point.** The session began with the student asking what was due that week. Claude read the course calendars and assignments through Brightspace's read-only API in the app's built-in browser, after the student signed in themselves, and updated a study plan.
2. **First version.** The student asked for a command-line review game to learn the syntax of the commands they needed. Claude wrote a standard-library Python quiz with a command matcher that accepts real-world variations (optional `sudo`, any quote style, flag letters in any order).
3. **Iterating on feedback.** The student asked for:
   - more color and interactivity, plus a Matrix-green cursor and input (which became the rain intro, arrow-key menus, animations, streaks and ranks);
   - explanations for wrong answers;
   - Enter to count as the second attempt.
4. **Checking against the course.** The student asked Claude to make sure every question was actually covered in DCOM 142. Claude pulled the current slide decks and objectives pages through the same read-only API and read them. It then:
   - removed the questions the course hadn't taught (package management, storage, `man -k`, the sticky bit's octal digit and others);
   - added commands the slides do teach (`usermod -e`, `getent`, `killall -u`, `chage -m/-M/-W`, `sudoedit`, `pkexec`, the in-class chmod exercises and more);
   - confirmed each question's key command or phrase in the deck it cites.

   That pass also caught a slide typo: the deck lists `chmod -r` for recursive, but the real option is `-R`.

**How it was tested.** At each step Claude ran checks before handing anything back:
- unit tests on the answer matcher;
- permission math compared against Python's own `stat.filemode` for all 4,096 modes;
- scripted keystroke sessions through every menu, plus a perfect-play bot;
- forced-interactive runs replayed through a tiny terminal emulator.

The screenshots above come from that emulator. The checks caught real bugs along the way, such as a "try again" message that didn't actually allow a retry and a hint that gave away one-character answers.

## Academic integrity

This is a self-study tool. The DCOM 142 syllabus does not allow AI tools on graded work, so don't use this, or any AI, during a quiz, exam, Live Lab or Applied Live Lab.

## License

[MIT](LICENSE)
