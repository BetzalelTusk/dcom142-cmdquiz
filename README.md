# dcom142-cmdquiz

A Matrix-themed terminal game for drilling the Linux commands from **DCOM 142** (Linux+ part 1, CompTIA Linux+ XK0-006) at the Community College of Baltimore County. You get a task, type the command from memory, and the game tells you exactly what you got wrong and why.

![Intro: the title decodes out of digital rain](docs/intro.png)

Built by a DCOM 142 student with [Claude Code](https://claude.com/claude-code) to study for the midterm. Read the full story in the **[case study](CASE_STUDY.md)**. Not affiliated with or endorsed by CCBC.

## Run it

> **Never used the command line?** Follow the **[beginner walkthrough](#beginner-walkthrough)** below. It's copy-and-paste, Windows first, then Mac.

```bash
git clone https://github.com/BetzalelTusk/dcom142-cmdquiz.git
cd dcom142-cmdquiz
python cmdquiz.py
```

You need Git, plus Python 3.8 or newer and nothing else (standard library only). It works on Windows, macOS and Linux and looks best in Windows Terminal or any terminal with 24-bit color. Use `python3` instead of `python` on a Mac.

| Option | Effect |
|---|---|
| `--no-intro` | skip the digital-rain intro |
| `--no-anim` | turn off all animation |
| `--plain` | ASCII only, for terminals that show boxes instead of symbols |

Progress and XP are saved to `.cmdquiz_progress.json` in the game's folder.

## Beginner walkthrough

For DCOM 142 classmates who have **never used the command line**. You'll copy and paste a few lines; it takes a few minutes, mostly waiting for installs. After the first time, starting the game takes two commands.

**How to paste into a terminal:** press **Ctrl + V** (Mac: **Cmd + V**), or right-click. Press **Enter** after each line.

**Jump to:** [Windows](#windows) · [Mac](#mac) · [Playing](#playing) · [Next time](#next-time) · [If something goes wrong](#if-something-goes-wrong)

### Windows

**1. Open a terminal.** Press the **Windows key**, type `terminal`, press **Enter**. (If nothing comes up, type `cmd` instead.)

**2. Get Python.** Type this and press Enter:

```
python --version
```

- If you see **`Python 3.x`**, you already have it. Go to step 3.
- If it says **`Python was not found`**, type `python` on its own and press Enter. The **Microsoft Store** opens on the Python page. Click **Get** (or **Install**), wait for it to finish, then come back to the terminal.

**3. Get Git.** Paste this and press Enter:

```
winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
```

If Windows asks *"Do you want to allow this app to make changes?"*, click **Yes**. Wait for **Successfully installed**.
*(Already have Git? `git --version` shows a version number. Then skip this step.)*

**4. Close the terminal and open a new one** (step 1 again). A terminal that was already open doesn't know Git was just installed.

**5. Download the game, go into its folder and start it.** Paste these one at a time, pressing Enter after each:

```
git clone https://github.com/BetzalelTusk/dcom142-cmdquiz.git
```
```
cd dcom142-cmdquiz
```
```
python cmdquiz.py
```

Green "digital rain" falls, then the **CMDQUIZ** menu appears. That's it. 🎉 See [Playing](#playing).

### Mac

**1. Open Terminal.** Press **Cmd (⌘) + Space**, type `Terminal`, press **Enter**.

**2. Get Git and Python together.** Type this and press Enter:

```
git --version
```

- If you see a version number, you already have them. Go to step 3.
- If a box asks to install the **command line developer tools**, click **Install**, then **Agree**, and wait for it to finish. That one install gives you both `git` and `python3`.

**3. Download the game, go into its folder and start it.** Paste these one at a time, pressing Enter after each:

```
git clone https://github.com/BetzalelTusk/dcom142-cmdquiz.git
```
```
cd dcom142-cmdquiz
```
```
python3 cmdquiz.py
```

(On a Mac it's `python3`, with a 3.)

### Playing

The game gives you a task, like *"Add alice to the group developers WITHOUT removing her other groups"*, and you type the Linux command that does it. **You type the Linux commands into the game, not into your terminal.** Windows wouldn't understand `groupadd`, and that's fine, because the game checks your answers itself.

| Key | What it does |
|---|---|
| **↑ / ↓**, then **Enter** | Move around the menus and pick an option (or just press its number) |
| Type your answer, then **Enter** | Submit an answer |
| `?` | Get a hint |
| **Enter** on an empty line *after a wrong answer* | Show the answer (that counts as your second try) |
| `skip` | Give up and see the answer |
| `q` | End the round, or quit from the main menu |
| **Ctrl + C** | Emergency exit, works anywhere |

You get **two tries** per question. When you miss, the game shows your answer next to the correct one, explains it, and names the slide it's from. Good places to start: **Permission drills** (chmod / umask number practice) and **Midterm blitz** (20 questions from Modules 1-5).

### Next time

Open a terminal and run these two lines:

| Windows | Mac |
|---|---|
| `cd dcom142-cmdquiz` | `cd dcom142-cmdquiz` |
| `python cmdquiz.py` | `python3 cmdquiz.py` |

**Get the newest version** whenever the game is updated: `cd dcom142-cmdquiz` and then run `git pull`. Your progress is kept.

**Tip:** the **↑ (up arrow)** key brings back the last command you typed.

### If something goes wrong

| What you see | What to do |
|---|---|
| `'winget' is not recognized` | Update **App Installer** from the Microsoft Store, then try again. Or install Git from **https://git-scm.com/download/win** (run the download and keep clicking **Next**). |
| `'git' is not recognized` right after installing Git | Close the terminal and open a new one (Windows step 4). |
| `'python' is not recognized`, or `Python was not found` | Type `python` and press Enter to open the Microsoft Store page, then click **Get**. Or try `py cmdquiz.py` instead. |
| `fatal: destination path 'dcom142-cmdquiz' already exists` | You already downloaded it. Just run `cd dcom142-cmdquiz`, then start the game. |
| `can't open file ... cmdquiz.py` | You're not in the game's folder. Run `cd dcom142-cmdquiz` first. |
| Boxes or question marks instead of lines and arrows | Start it with `python cmdquiz.py --plain` |
| Colors look odd or the screen flickers | Use the free **Windows Terminal** app from the Microsoft Store, or start with `python cmdquiz.py --no-anim` |
| You can't install anything (e.g. a school computer) | Use your own computer. School machines often block installs. |
| You want to start over | Delete the file `.cmdquiz_progress.json` inside the `dcom142-cmdquiz` folder. |

<details>
<summary><b>What did I just type?</b> (optional, and good Linux+ practice)</summary>

| You typed | What it does | Linux+ connection |
|---|---|---|
| `python --version`, `git --version` | Runs a program with an **option** that asks for its version | Command + option, like `ls -la` (Module 1) |
| `winget install ...` | Asks Windows' package manager to install software | Same idea as `dnf install` / `apt install` (Module 10) |
| `git clone <url>` | Downloads a full copy of a GitHub repository into a new folder | |
| `cd dcom142-cmdquiz` | Moves into that folder | `cd` (Module 1) |
| `python cmdquiz.py` | Runs a program and gives it a file as an **argument** | Command + argument, like `cat notes.txt` |
| **↑ arrow** | Brings back your last command | Bash `history` (Module 1) |

A **terminal** (also called the *command line* or *CLI*) is a window where you control the computer by typing instead of clicking. The text waiting for you, like `C:\Users\you>`, is the **prompt**.

</details>

Questions or something unclear? Open an issue on the [GitHub page](https://github.com/BetzalelTusk/dcom142-cmdquiz/issues).

## How it plays

![Main menu](docs/menu.png)

- **Arrow keys** (or j/k) and Enter move through the menus, or press the option's number.
- **Type the command** at the green prompt. Your text and cursor are Matrix green. Typing `sudo` is optional, quote style doesn't matter, and `-la` counts the same as `-al`, but argument order does matter (`chown file alice` is wrong).
- **One retry.** A wrong answer gets one more try. Press **Enter** on that second try to see the answer straight away. `?` gives a hint and `skip` reveals the answer.
- **On a miss** you get a word-by-word comparison (green matches, red is what you typed wrong, yellow is what was expected), the accepted alternatives, an explanation, and the slide it comes from.

![A wrong answer with the explanation panel](docs/wrong-answer.png)

**Modes:**
- **Quick round:** 10 mixed questions.
- **Midterm blitz:** 20 questions from Modules 1-5.
- **Lightning:** 90 seconds, as many as you can.
- **Pick topics:** a checklist of topics to drill.
- **Permission drills:** endless generated octal / rwx / symbolic chmod / umask / SUID-SGID math, with the working shown step by step.
- **Missed questions:** only the ones you've gotten wrong.
- **About:** four pages on what the game is, how it was made, the numbers, and what the testing caught.

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

The short version is below; the **[case study](CASE_STUDY.md)** has the whole story, including what the checks caught and the lessons learned. The game's **About** screen has a summary too.

![The About screen](docs/about.png)

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
