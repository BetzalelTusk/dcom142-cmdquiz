# dcom142-cmdquiz

A Matrix-themed terminal game for drilling the Linux commands from **DCOM 142** (Linux+ part 1, CompTIA Linux+ XK0-006) at the Community College of Baltimore County. You get a task, type the command from memory, and the game tells you exactly what you got wrong and why.

![Intro: the title decodes out of digital rain](docs/intro.png)

Built by a DCOM 142 student with [Claude Code](https://claude.com/claude-code) to study for the midterm. Read the full story in the **[case study](CASE_STUDY.md)**. Not affiliated with or endorsed by CCBC.

## Run it

> **Never used the command line?** Follow the step-by-step **[beginner walkthrough](#beginner-walkthrough)** below. It covers installing Python, downloading the game and running it on Windows or Mac.

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

## Beginner walkthrough

This section is for DCOM 142 classmates who have **never used the command line before**. By the end you'll have the game running on your own computer. It takes about 10 minutes the first time and about 10 seconds after that.

Nothing here can break your computer. If something doesn't match what you see, skip down to [If something goes wrong](#if-something-goes-wrong).

**Contents**
- [What you're about to do](#what-youre-about-to-do)
- [A few words you'll see](#a-few-words-youll-see)
- [One thing that confuses everyone](#one-thing-that-confuses-everyone)
- [Windows](#windows)
- [Mac](#mac)
- [How to play](#how-to-play)
- [Next time you want to play](#next-time-you-want-to-play)
- [If something goes wrong](#if-something-goes-wrong)
- [You just used the command line](#you-just-used-the-command-line)

### What you're about to do

1. Open a **terminal** (a window where you type instead of click).
2. Make sure **Python** is installed (the game is written in Python).
3. **Download** the game from GitHub.
4. Point the terminal at the game's folder and **run** it.

### A few words you'll see

| Word | What it means |
|---|---|
| **Terminal**, **command line**, **CLI** | A window where you control the computer by typing. On Windows it's called *Terminal*, *Command Prompt* or *PowerShell*. On a Mac it's *Terminal*. They all work for this. |
| **Command** | A line you type and then press **Enter** to run. |
| **Prompt** | The text that waits for you to type, e.g. `C:\Users\you>` on Windows or `you@MacBook ~ %` on a Mac. You type after it. |
| **Folder** / **directory** | Same thing. Linux people say "directory". |
| **Python** | A programming language. Installing it lets your computer run `.py` files like this game. |

> In this guide, anything in a gray box like `python --version` is something you **type exactly**, then press **Enter**. Don't type the prompt itself.

### One thing that confuses everyone

The game asks you Linux questions like *"Create a group named hr"*, and you answer with Linux commands like `groupadd hr`.

**You type those answers into the game, not straight into your Windows terminal.** If you typed `groupadd hr` at a normal Windows prompt, Windows wouldn't know what it means, because Windows isn't Linux. That's fine. The game checks your answers itself, so it works on Windows, Mac and Linux.

### Windows

#### Step 1: Open a terminal

1. Click **Start** (or press the **Windows key**).
2. Type `terminal`. If nothing shows up, type `cmd` instead.
3. Press **Enter**.

A window opens with a prompt like `C:\Users\yourname>` or `PS C:\Users\yourname>`. That's it. You're in the command line.

#### Step 2: Check whether you have Python

Type this and press **Enter**:

```
python --version
```

- If you see something like **`Python 3.13.1`** (any version 3.8 or higher), you're set. Skip to Step 3.
- If the **Microsoft Store opens**, or you see **`'python' is not recognized...`** or **`Python was not found`**, you need to install it. Keep going.

**Installing Python:**
1. Go to **https://www.python.org/downloads/** and click the big yellow **Download Python 3.x** button.
2. Open the file you downloaded.
3. ⚠️ **Before you click anything else, tick the box at the bottom that says "Add python.exe to PATH".** This is the step people miss. Without it, the terminal can't find Python.
4. Click **Install Now**, wait for it to finish, then click **Close**.
5. **Close your terminal window and open a new one** (Step 1 again). A terminal that was already open won't notice the new install.
6. Try `python --version` again. You should see a version number now.

#### Step 3: Download the game

1. Go to **https://github.com/BetzalelTusk/dcom142-cmdquiz**.
2. Click the green **`<> Code`** button, then click **Download ZIP**.
3. Open your **Downloads** folder. Right-click **`dcom142-cmdquiz-main.zip`**, choose **Extract All…**, then click **Extract**.
4. A new folder opens called **`dcom142-cmdquiz-main`**. Inside you should see **`cmdquiz.py`**.

> Want to see what you're running first? Right-click `cmdquiz.py` and choose **Open with → Notepad**. It's one readable Python file, and it doesn't install anything or touch the internet.

#### Step 4: Open a terminal *inside* the game's folder

The terminal has to be "standing in" the right folder to find the game. The easiest way:

1. In the **`dcom142-cmdquiz-main`** folder (where you can see `cmdquiz.py`), click the **address bar** at the top of the File Explorer window, where it shows the folder path.
2. Delete what's there, type `cmd` and press **Enter**.

A terminal opens already pointing at that folder.

*(On Windows 11 you can also right-click an empty spot in the folder and choose **Open in Terminal**.)*

#### Step 5: Run the game

```
python cmdquiz.py
```

You should see green "digital rain", then the **CMDQUIZ** menu. 🎉 Jump to [How to play](#how-to-play).

If it says `'python' is not recognized`, try this instead:

```
py cmdquiz.py
```

### Mac

#### Step 1: Open Terminal
Press **Command (⌘) + Space**, type `Terminal` and press **Enter**.

#### Step 2: Check whether you have Python
Type this and press **Enter**:

```
python3 --version
```

(On a Mac it's `python3`, with a 3.)
- If you see **`Python 3.x`**, you're set.
- If a box pops up offering to install **command line developer tools**, click **Install** and wait. That gives you Python. Then run `python3 --version` again.
- Otherwise, install it from **https://www.python.org/downloads/** (open the downloaded file and click through), then open a new Terminal window.

#### Step 3: Download the game
Go to **https://github.com/BetzalelTusk/dcom142-cmdquiz**, click the green **`<> Code`** button, then **Download ZIP**. Safari usually unzips it for you. If not, double-click the zip in **Downloads**. You'll get a folder called **`dcom142-cmdquiz-main`**.

#### Step 4: Point Terminal at the folder
In Terminal, type `cd` followed by **a space** (don't press Enter yet). Then **drag the `dcom142-cmdquiz-main` folder from Finder into the Terminal window**. Its location gets typed for you. Now press **Enter**.

#### Step 5: Run the game

```
python3 cmdquiz.py
```

### How to play

The game gives you a task, like *"Add alice to the group developers WITHOUT removing her other groups"*, and you type the Linux command that does it.

| Key | What it does |
|---|---|
| **↑ / ↓**, then **Enter** | Move around the menus and pick an option (or just press the option's number) |
| Type your answer, then **Enter** | Submit an answer |
| `?` | Get a hint |
| **Enter** on an empty line *after a wrong answer* | Show the answer (that counts as your second try) |
| `skip` | Give up and see the answer |
| `q` | End the round (or quit, from the main menu) |
| **Ctrl + C** | Emergency exit, works anywhere |

**Good to know:**
- You get **two tries** per question. When you miss, the game shows your answer and the correct one word by word, explains why, and tells you **which slide** it's from.
- Typing `sudo` in front is optional, and `-la` counts the same as `-al`.
- Questions you miss come back more often. Your progress is saved automatically.
- Good places to start: **Permission drills** (chmod / umask number practice) and **Midterm blitz** (20 questions from Modules 1-5). **Pick topics** lets you focus on a weak area.

### Next time you want to play

You only do the setup once. After that:

1. Open the **`dcom142-cmdquiz-main`** folder.
2. **Windows:** click the address bar, type `cmd` and press Enter. **Mac:** open Terminal and type `cd ` then drag the folder in.
3. Run `python cmdquiz.py` (Mac: `python3 cmdquiz.py`).

**Tip:** in a terminal, the **↑ (up arrow)** key brings back the last command you typed, so you don't have to retype it.

### If something goes wrong

| What you see | What to do |
|---|---|
| `'python' is not recognized...` | Try `py cmdquiz.py`. If that fails too, reinstall Python and **tick "Add python.exe to PATH"**, then open a **new** terminal. |
| The Microsoft Store opens when you type `python` | Windows is offering to install Python for you. Either install **Python 3.13** from the Store, or use python.org (Windows Step 2). |
| `can't open file ... cmdquiz.py: No such file or directory` | Your terminal isn't in the game's folder. Type `dir` (Windows) or `ls` (Mac) and press Enter. If `cmdquiz.py` isn't in the list, redo Step 4. |
| Boxes, question marks or weird symbols instead of lines and arrows | Run `python cmdquiz.py --plain` for a plain-text version. |
| The colors look odd, or the screen flickers | Try the free **Windows Terminal** app from the Microsoft Store, or run `python cmdquiz.py --no-anim` to turn animations off. |
| You want to skip the rain intro | `python cmdquiz.py --no-intro` |
| You can't install anything (e.g. a school computer) | Use your own computer. School machines often block installs. |
| You want to reset your progress | Delete the file `.cmdquiz_progress.json` in the game's folder. On a Mac it's hidden; press **Cmd + Shift + .** in Finder to show hidden files. |
| You downloaded a newer version of the game | Copy `.cmdquiz_progress.json` from the old folder into the new one to keep your progress. |

### You just used the command line

Without realizing it, you've already used real commands:

| You typed | What it did | The Linux version (DCOM 142!) |
|---|---|---|
| `python --version` | Ran a program with an **option** (`--version`) | Same idea as `ls -la`: a command plus options |
| `dir` / `ls` | Listed the files in a folder | `ls` |
| `cd` + a folder | Changed into a folder | `cd`, as in Module 1 |
| `python cmdquiz.py` | Ran a program and gave it a file as an **argument** | Like `cat notes.txt` |
| **↑ arrow** | Brought back your last command | Bash `history`, from Module 1 |

The syntax you learned in Module 1 is the same thing: **command, option, argument**.

Questions or something unclear in this guide? Open an issue on the [GitHub page](https://github.com/BetzalelTusk/dcom142-cmdquiz/issues).

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
