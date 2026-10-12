#!/usr/bin/env python3
"""cmdquiz - a Matrix-themed command-line review game for the Linux commands in DCOM 142.

    python tools/cmdquiz.py              full experience
    python tools/cmdquiz.py --no-intro   skip the digital-rain intro
    python tools/cmdquiz.py --no-anim    no animations at all
    python tools/cmdquiz.py --plain      ASCII only, for terminals that show boxes instead of symbols

You get a task ("create user alice with a home directory") and type the command
from memory. Wrong answers come back more often; answers you nail twice in a
row leave the "missed" pool. Progress and XP are saved next to this file.

Self-study only. Do not use it during a graded quiz, exam or lab.
Standard library only, works on Windows, macOS and Linux.
"""
import atexit
import difflib
import json
import os
import random
import re
import shlex
import shutil
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SAVE = os.path.join(HERE, ".cmdquiz_progress.json")

ARGS = set(sys.argv[1:])
if os.name == "nt":
    os.system("")  # turns on ANSI escape handling in the Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()
COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
ANIM = INTERACTIVE and "--no-anim" not in ARGS
PLAIN = "--plain" in ARGS

# --------------------------------------------------------------------------- question bank
# Every question comes from the DCOM 142 Fall 2026 course material on Brightspace: the
# instructor's Module 1-6 slide decks (and their in-class exercises), the Module Learning
# Objectives pages, and the midterm review deck. `src` names where each one is taught.
#
# Q(topic, task, "accepted;;another accepted", explanation, src, tip="", loose=False)
# Typing `sudo` is optional everywhere. Quotes are ignored. Letters in a combined flag
# group can come in any order (-la == -al), but arguments must stay in order.
# loose=True is for word answers ("environment", "Ctrl+O"): case, spaces and punctuation are ignored.
BANK = []


def Q(topic, prompt, answers, explain, src, tip="", loose=False):
    BANK.append({"topic": topic, "prompt": prompt, "answers": [a.strip() for a in answers.split(";;")],
                 "explain": explain, "src": src, "why": tip, "loose": loose})


TOPICS = {
    "basics": "Module 1: Linux basics, editors, su/sudo",
    "accounts": "Module 2: Users and groups",
    "shell": "Module 3: User config, password policy, privilege escalation",
    "perms": "Module 4: Standard permissions, ownership, attributes",
    "special": "Module 5: SUID / SGID / sticky bit",
    "acl": "Module 5: Access control lists",
    "files": "Module 6: File system, links, find (after midterm)",
    "text": "Module 6: Text commands (after midterm)",
}
MIDTERM = ["basics", "accounts", "shell", "perms", "special", "acl"]
M1, M2, M3, M4, M5, M6 = ("Module 1 slides", "Module 2 slides", "Module 3 slides",
                          "Module 4 slides", "Module 5 slides", "Module 6 slides")

# ---- Module 1: Linux basics (CertMaster lessons 1.1 and 1.2)
Q("basics", "Print the current working directory", "pwd",
  "pwd = print working directory. It shows the absolute path of where you are; when you log in it is /home/<username>.",
  M1 + " (Basic Bash Commands, Command - pwd)")
Q("basics", "Show the username you are logged in as", "whoami",
  "whoami displays the current user. Useful after su to confirm which account you are acting as.",
  M1 + " (Basic Bash Commands)")
Q("basics", "Long listing of the current directory, including hidden files", "ls -la;;ls -l -a",
  "ls lists a directory. -l = long listing (permissions, owner, group, size, date) and -a = all, including hidden files that start with a dot. The slides use ls -la as the multiple-option example.",
  M1 + " (Bash Characteristics and Syntax)", tip="-l long format, -a include dotfiles")
Q("basics", "Open the manual page for the chmod command", "man chmod",
  "man {command} opens the manual page, the primary reference for a command's syntax and options. Inside: / searches, n next match, p previous, q quits.",
  M1 + " (Documentation and Manual Pages)")
Q("basics", "In a man page, which key quits?", "q",
  "Man page navigation: q quits, / starts a search, n = next match, p = previous match, Page Up/Down scroll, Home/End jump.",
  M1 + " (Man Page Navigation Keys)", loose=True)
Q("basics", "List the commands you ran previously", "history",
  "history lists the commands you've entered (kept even after rebooting). The arrow keys also scroll through it.",
  M1 + " (Bash Command Strategies)")
Q("basics", "Clear the terminal screen", "clear",
  "clear removes past commands from the screen to cut distractions. It doesn't erase your history.",
  M1 + " (Bash Command Strategies)")
Q("basics", "Change to your home directory using the tilde shortcut", "cd ~;;cd",
  "~ (tilde) represents the current user's home directory. cd ~ goes there, and plain cd does the same.",
  M1 + " (Changing Directories)", tip="cd alone also goes home")
Q("basics", "Move up one directory", "cd ..",
  ".. (two dots) is the parent directory, the one above the current one, so cd .. moves up a level. A single . means the current directory.",
  M1 + " (Changing Directories)")
Q("basics", "Show the directory structure as a tree", "tree",
  "tree displays the directory structure in a tree-like format.",
  M1 + " (Basic Bash Commands)")
Q("basics", "Create an empty file called notes.txt", "touch notes.txt",
  "touch creates a new empty file, or updates the timestamp on an existing one.",
  M1 + " (Basic Bash Commands)", tip="touch also updates a timestamp")
Q("basics", "Display the whole contents of notes.txt", "cat notes.txt",
  "cat displays a file's contents all at once. For long files use less, which shows screen-size sections.",
  M1 + " (Basic Bash Commands)")
Q("basics", "View bigfile.log one screen at a time", "less bigfile.log",
  "less displays file contents in screen-size sections. / searches, q quits.",
  M1 + " (Basic Bash Commands)")
Q("basics", "In vim, which key (from command mode) switches to insert mode?", "i",
  "Vim has three modes: Command (the default), Insert and Execute. i goes from Command to Insert mode, Esc returns to Command mode, and : opens Execute mode.",
  M1 + " (Introducing Vim)", loose=True)
Q("basics", "In vim, the command to write the file and quit", ":wq;;:x",
  "From Command mode (press Esc), :w saves and :q closes, so :wq saves and quits in one step.",
  M1 + " (Vim and nano: Save = ESC and :w, Close = ESC and :q)")
Q("basics", "In nano, which shortcut saves the file?", "Ctrl+O;;^O",
  "nano has no modes; you just type. Save = Ctrl + O, close = Ctrl + X.",
  M1 + " (Vim and nano)", loose=True)
Q("basics", "In nano, which shortcut closes the editor?", "Ctrl+X;;^X",
  "nano: Ctrl + X closes (it asks to save if there are changes). Ctrl + O saves.",
  M1 + " (Vim and nano)", loose=True)
Q("basics", "Which directory holds configuration files?", "/etc",
  "/etc stores configuration files. FHS (Filesystem Hierarchy Standard) key directories: /etc, /home, /root, /var/log.",
  M1 + " (Key Directories)")
Q("basics", "Which directory holds system and service logs?", "/var/log",
  "/var/log holds system and service log files, e.g. /var/log/messages.",
  M1 + " (Key Directories)")
Q("basics", "What is the root user's home directory?", "/root",
  "root's home directory is /root. Standard users get subdirectories of /home.",
  M1 + " (Key Directories)", tip="standard users live under /home")
Q("basics", "Switch to the root user AND load root's profile", "su - root;;su -",
  "su root switches user to root. su - root also switches to root's profile (environment). Both need root's password and grant all admin privileges.",
  M1 + " (Commands: su and sudo)", tip="the dash loads root's profile")
Q("basics", "Run the command 'useradd bob' with admin rights, using your own password", "sudo useradd bob",
  "sudo {command} runs one command with elevated rights and asks for YOUR password. Who may do what is delegated in /etc/sudoers. su asks for root's password instead.",
  M1 + " (Commands: su and sudo)")
Q("basics", "Which file delegates specific admin tasks to specific users?", "/etc/sudoers",
  "/etc/sudoers controls sudo: it delegates specific tasks to specific users. Edit it with visudo.",
  M1 + " (Commands: su and sudo)")
Q("basics", "Which shell uses % instead of $ for its prompt?", "zsh",
  "Shells on the slides: bash (default for most Linux), ksh (older UNIX like AIX/Solaris), zsh (uses % instead of $), fish (for beginners, less common for scripting).",
  M1 + " (Command Shells)", loose=True)
Q("basics", "Which Linux distribution do the CertMaster labs use?", "Rocky Linux;;Rocky",
  "The CertMaster labs run Rocky Linux: free, open source, community-driven, and compatible with Red Hat Enterprise Linux (RHEL).",
  M1 + " (The Linux Distribution - CertMaster Lab)", loose=True)
Q("basics", "Unix versions are called flavors. What are Linux versions called?", "distributions;;distros;;distribution",
  "Unix is closed source and its versions are called flavors. Linux is open source under the GPL and its versions are called distributions (distros): kernel + tools + installation + package management.",
  M1 + " (History and Philosophy of Unix and Linux)", loose=True)
Q("basics", "Which license makes Linux open source?", "GPL;;GNU General Public License;;GNU GPL",
  "Linux is licensed as open source under the GNU General Public License (GPL). Other open-source license examples: Apache License 2.0, Mozilla Public License.",
  M1 + " (Characteristics of Free and Open-Source Software)", loose=True)
Q("basics", "What is step 1 of the CompTIA troubleshooting methodology?", "identify the problem;;identify problem",
  "CompTIA troubleshooting order: 1 identify the problem, 2 establish a theory of probable cause, 3 test the theory, 4 establish a plan of action, 5 implement the solution or escalate, 6 verify full system functionality, 7 determine the root cause, 8 document findings (throughout).",
  M1 + " (The CompTIA Troubleshooting Methodology)", loose=True)
Q("basics", "What is the LAST step of the CompTIA troubleshooting methodology?", "document findings;;document;;documentation",
  "The final step is to document findings, and you do it throughout the process, adding to the internal knowledge base. The step before it is to determine the root cause.",
  M1 + " (The CompTIA Troubleshooting Methodology)", loose=True)

# ---- Module 2: users and groups (CertMaster lessons 2.1 and 2.2)
Q("accounts", "Create a new user named user10", "useradd user10",
  "useradd creates user accounts by adding entries to /etc/passwd and /etc/shadow. This is step 1 of the in-class exercise.",
  M2 + " (Account Management Commands; in-class exercise, s.45)")
Q("accounts", "Add the comment \"CCBC student\" to the existing user user10", "usermod -c \"CCBC student\" user10",
  "usermod modifies an existing account. -c sets the comment field (usually the user's name), the 5th field of /etc/passwd. Quote it because of the space.",
  M2 + " (Command - usermod: adding comment; in-class exercise, s.45)")
Q("accounts", "Set the password for user10", "passwd user10",
  "passwd {username} sets a user's password (root/sudo needed for someone else's). The hash goes into /etc/shadow.",
  M2 + " (User Account Creation: passwd)")
Q("accounts", "Add alice to the group developers WITHOUT removing her other groups",
  "usermod -aG developers alice;;usermod -a -G developers alice;;usermod -G developers -a alice",
  "Adding a user to a group is a change to the USER, so it's usermod. -G names the group and -a appends. Without -a the user is removed from all other groups and kept only in the one you named.",
  M2 + " (Adding Users to Group; Discussion Question 2)", tip="-a (append) must go with -G")
Q("accounts", "Change alice's login shell to /bin/zsh with usermod", "usermod -s /bin/zsh alice",
  "usermod -s {shell} {user} changes the login shell, the 7th field of /etc/passwd. The slide example changes from bash to zsh.",
  M2 + " (Command - usermod: changing the shell)")
Q("accounts", "The temporary user dcom's contract ends 2027-12-31. Set that account expiration date",
  "usermod -e 2027-12-31 dcom",
  "usermod -e {YYYY-MM-DD} {user} sets the date the account expires. The slide's example is the temp employee dcom whose contract ends December 31, 2027.",
  M2 + " (Command - usermod: account expirations, s.25)")
Q("accounts", "Delete user10 AND their home directory", "userdel -r user10",
  "userdel removes a user. By default it keeps the home directory (the data may need reassigning); -r also removes it. Neither usermod nor userdel works while the account has running processes.",
  M2 + " (Command - userdel)")
Q("accounts", "End all of user10's running processes before deleting the account", "killall -u user10",
  "killall -u {username} ends every process owned by that user. The troubleshooting slide says to do this before deleting, because userdel refuses while processes are running.",
  M2 + " (Troubleshooting User and Group Account Issues)")
Q("accounts", "Display user account information with getent (similar to cat /etc/passwd)", "getent passwd",
  "getent passwd displays the account database, similar to cat /etc/passwd.",
  M2 + " (Command - getent)")
Q("accounts", "Show all accounts currently logged in", "w",
  "w lists the accounts currently logged in and what they're doing. id shows one account's information.",
  M2 + " (Account Configuration Commands)")
Q("accounts", "Show user10's UID, GID and group memberships", "id user10",
  "id {user} shows uid, gid (primary group) and groups (all memberships). Use it to check your usermod changes.",
  M2 + " (Account Configuration Commands)")
Q("accounts", "Create a group named hr", "groupadd hr",
  "groupadd creates a group; its entry goes into /etc/group. It's the first step of the hands-on exercise.",
  M2 + " (Command - groupadd; Hands-on Exercise)")
Q("accounts", "Rename the group hr to csit", "groupmod -n csit hr",
  "groupmod changes a group's attributes. -n renames: groupmod -n NEWNAME OLDNAME (slide example: groupmod -n newsales sales).",
  M2 + " (The groupmod Command; Hands-on Exercise)", tip="-n new name first, then the old name")
Q("accounts", "Change the group ID of the group sales to 123", "groupmod -g 123 sales",
  "groupmod -g changes a group's GID. That exact example (groupmod -g 123 sales) is on the slide.",
  M2 + " (The groupmod Command)")
Q("accounts", "Delete the group dcom", "groupdel dcom",
  "groupdel removes a group. Before deleting: delete or reassign its users and reassign group-linked resources.",
  M2 + " (Group Management Commands; Hands-on Exercise)")
Q("accounts", "View the last 10 groups in /etc/group", "tail /etc/group;;tail -n 10 /etc/group",
  "tail shows the end of a file, 10 lines by default. New groups are added at the bottom, so tail /etc/group is how the exercise checks your work.",
  M2 + " (Group Configuration Files; Hands-on Exercise)")
Q("accounts", "Show the last 10 lines of /etc/passwd, keeping only lines containing user1", "tail /etc/passwd | grep user1",
  "The pipe | sends tail's output into grep, a search utility that keeps only matching lines. That exact command is on the slide.",
  M2 + " (Basic Commands: grep)")
Q("accounts", "Search /etc/passwd for lines containing user1 (without tail)", "grep user1 /etc/passwd",
  "grep {pattern} {file} prints the lines of the file that match the pattern.",
  M2 + " (Basic commands: cat, tail, grep)")
Q("accounts", "Which file stores user accounts and their settings?", "/etc/passwd",
  "/etc/passwd stores the account info with 7 colon-separated fields: user name : password (x = stored elsewhere) : UID : GID : comment : home directory : login shell.",
  M2 + " (User Account Storage; The /etc/passwd File)")
Q("accounts", "Which file stores password information (only root can read it)?", "/etc/shadow",
  "Passwords were moved to /etc/shadow for security; only root can access it. /etc/passwd shows an x where the password used to be.",
  M2 + " (User Configuration Files: /etc/shadow)")
Q("accounts", "Which file stores group information?", "/etc/group",
  "/etc/group stores groups with 4 colon-separated fields: group name : password : GID : member list. Don't edit it by hand; use the group commands.",
  M2 + " (The /etc/group File)")
Q("accounts", "How many colon-separated fields are in an /etc/passwd line?", "7",
  "7: user name, password (x), user ID, group ID, comment, home directory, login shell.",
  M2 + " (The /etc/passwd File)")
Q("accounts", "How many colon-separated fields are in an /etc/group line?", "4",
  "4: group name, password, group ID (GID), and the member list.",
  M2 + " (The /etc/group File)")
Q("accounts", "Display the record of every login and logoff on the system", "last",
  "last shows login history: who logged in, when, from where, how long they stayed, and reboots/shutdowns. It reads /var/log/wtmp.",
  M2 + " (Last command; User Login Commands)")
Q("accounts", "Display the last login time for every account", "lastlog",
  "lastlog displays the last login time for each account, used in audits and security reviews. It uses its own file, /var/log/lastlog.",
  M2 + " (Command - lastlog)")
Q("accounts", "Which file does the last command read?", "/var/log/wtmp",
  "last reads the wtmp file, usually /var/log/wtmp. lastlog uses /var/log/lastlog.",
  M2 + " (Last command)")
Q("accounts", "Which PAM module (current version) locks an account after three failed logins?", "pam_faillock;;faillock",
  "PAM (Pluggable Authentication Modules) adds authentication options beyond /etc/passwd and /etc/shadow. pam_faillock is the current module that locks an account after failed attempts. pam_tally2 is the deprecated older one.",
  M2 + " (Two PAM Modules)", loose=True)
Q("accounts", "Run the user-creation script createusers.sh from the current directory", "./createusers.sh",
  "To run a script: give it execute permission, then run it with ./ in front (./ means the current directory, since it isn't in PATH).",
  M2 + " (Scripting Group Account Commands: execute with ./)")

# ---- Module 3: user configuration and privilege escalation (CertMaster lessons 2.3 and 2.4)
Q("shell", "Which variable sets the primary shell prompt?", "PS1",
  "PS1 = primary shell prompt variable. Change it temporarily at the prompt, or permanently for a user in ~/.bashrc.",
  M3 + " (PS1)", loose=True)
Q("shell", "Show the system's host name", "hostname",
  "hostname prints the machine's name, part of what the prompt shows (user, host, home directory).",
  M3 + " (Customizing shell: whoami, hostname, pwd)")
Q("shell", "List the available shells with chsh", "chsh -l",
  "chsh changes a user's default shell. -l lists available shells and -s gives the path to the shell you want.",
  M3 + " (Changing shell)")
Q("shell", "Change your login shell to /bin/sh with chsh", "chsh -s /bin/sh",
  "chsh -s {path} changes the default shell; that example is on the slide. usermod -s does the same for any user.",
  M3 + " (Changing shell)")
Q("shell", "List all files including hidden ones (names starting with a dot)", "ls -a",
  "ls -a shows hidden files, like .bashrc and .bash_profile, whose names start with a dot.",
  M3 + " (Command - ls)")
Q("shell", "Which system-wide file sets environment variables and startup programs for user shells?", "/etc/profile",
  "/etc/profile is a global settings file read first. User-specific files override it, and editing it directly is not recommended.",
  M3 + " (User Profile Templates: Global Settings)")
Q("shell", "Which directory's contents are copied into a new user's home when the user is added?", "/etc/skel",
  "/etc/skel is the skeleton directory. Its contents are copied when a user is added, which is how new users get a default .bashrc.",
  M3 + " (Global Settings: /etc/skel)")
Q("shell", "Which user file do you edit to customize your prompt permanently?", "~/.bashrc;;.bashrc",
  "~/.bashrc is the user-specific (local) settings file where you customize the prompt and aliases. .bash_profile is used once at initial login.",
  M3 + " (User Profile Templates: Local settings)")
Q("shell", "Which user file is used once when you first log in?", "~/.bash_profile;;.bash_profile",
  ".bash_profile runs once at initial login. ~/.bashrc holds the everyday shell customizations.",
  M3 + " (User Profile Templates: Local settings)")
Q("shell", "Which file sets system-wide functions and aliases for new user shells?", "/etc/bashrc",
  "/etc/bashrc establishes system-wide functions and aliases. /etc/profile.d stores customized scripts.",
  M3 + " (Account Profiles - Global Settings)")
Q("shell", "Which directory stores customized (profile) scripts?", "/etc/profile.d",
  "/etc/profile.d holds customized scripts that run with the global profile.",
  M3 + " (Account Profiles - Global Settings)")
Q("shell", "Which file stores the password policy settings (PASS_MAX_DAYS, PASS_MIN_LEN...)?", "/etc/login.defs",
  "/etc/login.defs holds the general password settings: PASS_MAX_DAYS, PASS_MIN_DAYS, PASS_WARN_AGE, PASS_MIN_LEN. Per-account values are set with passwd and chage.",
  M3 + " (/etc/login.defs; User Password Settings)")
Q("shell", "A variable inherited by child processes is called a(n) ____ variable", "environment",
  "An environment variable is inherited from the parent shell and passed on to child processes. Its name is usually uppercase, e.g. PATH. A shell (local) variable is not inherited.",
  M3 + " (Shell and Environment Variables)", loose=True)
Q("shell", "A variable that is NOT inherited by child processes is a ____ variable", "local;;shell;;shell/local",
  "Shell or local variables are not inherited by child processes. Environment variables are.",
  M3 + " (Shell and Environment Variables)", loose=True)
Q("shell", "Which variable tells Linux where to search for executable files?", "PATH",
  "PATH lists the directories searched for executables. A file in the current directory isn't found that way, so you run it with ./",
  M3 + " (Declaring Variables)", loose=True)
Q("shell", "Print the value of the PATH variable", "echo $PATH",
  "echo prints text and a $ in front of a variable name expands it, so echo $PATH prints the list of search directories.",
  M3 + " (Declaring Variables)")
Q("shell", "Create an alias named ll that runs ls -la", "alias ll='ls -la'",
  "alias makes a short name for a longer command with options and arguments. Quote the command because it contains a space.",
  M3 + " (Command Aliases)")
Q("shell", "Show user1's current password aging values", "chage -l user1",
  "chage manages password requirements. -l lists the current values (last change, expiry, min/max/warning days).",
  M3 + " (User Password Settings: chage)")
Q("shell", "Make user1 change password at least every 120 days (maximum)", "chage -M 120 user1",
  "chage -M = maximum days before the password must change. -m = minimum days between changes, -W = warning days, -E = lock the account after a date.",
  M3 + " (User Password Settings: chage)")
Q("shell", "For user1: 5-day warning, change required within 120 days, no change within 1 day of a new password",
  "chage -m 1 -M 120 -W 5 user1",
  "chage with three options at once is the slide's exact example: -m 1 (minimum 1 day between changes), -M 120 (maximum, about four months), -W 5 (warn 5 days ahead).",
  M3 + " (Displaying password details, s.40)")
Q("shell", "Lock user1's account after 2027-12-31 using chage", "chage -E 2027-12-31 user1",
  "chage -E locks (expires) the account after a specific date. usermod -e does the same.",
  M3 + " (User Password Settings: chage -E)")
Q("shell", "Immediately expire user1's password (force a change at next login)", "passwd -e user1",
  "passwd options from the slide: -d deletes the password, -e immediately expires it, -l locks the account, -u unlocks it.",
  M3 + " (User Password Settings: passwd)")
Q("shell", "Lock user1's account with passwd", "passwd -l user1",
  "passwd -l locks the account (password logins fail) and passwd -u unlocks it.",
  M3 + " (User Password Settings: passwd)")
Q("shell", "Unlock user1's account with passwd", "passwd -u user1",
  "passwd -u unlocks an account that passwd -l locked.",
  M3 + " (User Password Settings: passwd)")
Q("shell", "Delete user1's password with passwd", "passwd -d user1",
  "passwd -d deletes the account's password; the slide lists it as 'deletes password and disables account'.",
  M3 + " (User Password Settings: passwd)")
Q("shell", "Which group gives its members root admin privileges through sudo on Red Hat systems?", "wheel",
  "The wheel group gives root administration privileges to its members through sudo, and is associated with Red Hat distributions (Rocky included).",
  M3 + " (Group - wheel; Privilege Escalation Using sudo)", loose=True)
Q("shell", "Add the user dcom to the wheel group", "usermod -aG wheel dcom",
  "usermod -aG wheel dcom appends wheel to dcom's groups, which gives dcom sudo rights. This is from the Module 4 review exercise.",
  M4 + " (Review exercise, s.6) + " + M3 + " (wheel)")
Q("shell", "Safely edit the /etc/sudoers file", "visudo",
  "visudo is the command for editing /etc/sudoers; it checks the syntax so a typo can't break sudo.",
  M3 + " (Command - visudo)")
Q("shell", "Sudoers entry: kgarcia may run only /sbin/shutdown, as root, on all hosts", "kgarcia ALL=(root) /sbin/shutdown",
  "sudoers syntax: username hostname=(user) command. That exact line is on the slide: kgarcia ALL=(root) /sbin/shutdown.",
  M3 + " (File entries in /etc/sudoers)")
Q("shell", "Sudoers entry: alice may run ALL commands as ANY user on ALL hosts", "alice ALL=(ALL) ALL;;alice ALL=(ALL:ALL) ALL",
  "Same syntax, username hostname=(user) command, with ALL in each position: alice ALL=(ALL) ALL.",
  M3 + " (File entries in /etc/sudoers)")
Q("shell", "Edit the protected file /etc/named.conf with root privileges using sudo's edit command", "sudoedit /etc/named.conf",
  "sudoedit edits protected files with root privileges, letting a user edit a file without a full root shell.",
  M3 + " (Privilege Escalation Using sudo: sudoedit)")
Q("shell", "Use PolicyKit to run nano on /etc/named.conf with privileges", "pkexec nano /etc/named.conf",
  "pkexec executes a polkit (PolicyKit) action: pkexec program argument. That's the slide's example. Polkit decides who may perform privileged actions.",
  M3 + " (PolicyKit Rules)")
Q("shell", "Security principle: grant only the minimum access needed for a task", "principle of least privilege;;least privilege;;polp",
  "The principle of least privilege (PoLP): give users, applications and processes only as much access as they need, which reduces the attack surface. Use a standard account day to day and elevate only when needed.",
  M3 + " (Privilege Escalation Concepts) + " + M4 + " (PoLP)", loose=True)

# ---- Module 4: standard permissions (CertMaster lesson 3.1)
Q("perms", "List files in long format to see their permissions", "ls -l",
  "ls -l (list in long format) shows the permission string. The first character is - for a file or d for a directory, then 3 characters each for user, group and others.",
  M4 + " (View Permissions)")
Q("perms", "First character of the ls -l permission string for a directory?", "d",
  "The first field is the type: - = file, d = directory. Then fields 2-4 = user, 5-7 = group, 8-10 = others.",
  M4 + " (Interpret Permissions Strings)", loose=True)
Q("perms", "Set file1 to user rwx, group r-x, other --- (octal)", "chmod 750 file1",
  "chmod's absolute (octal) mode adds 4=r 2=w 1=x per identity: user rwx = 4+2+1 = 7, group r-x = 4+0+1 = 5, other --- = 0, giving 750. That exact example is on the slide.",
  M4 + " (Absolute Mode Octal Values, s.28)", tip="4=r 2=w 1=x")
Q("perms", "Class exercise: file1 = user read+execute, group read only, other read+write (octal)", "chmod 546 file1",
  "chmod: user r-x = 4+1 = 5, group r-- = 4, other rw- = 4+2 = 6, giving 546.",
  M4 + " (Class Exercise, s.30)")
Q("perms", "Class exercise: file2 = user read only, group read+execute, other read only (octal)", "chmod 454 file2",
  "chmod: user r-- = 4, group r-x = 4+1 = 5, other r-- = 4, giving 454.",
  M4 + " (Class Exercise, s.30)")
Q("perms", "Give others read permission on file1 (symbolic)", "chmod o+r file1",
  "chmod's symbolic mode is identity + operator + permission: o = others, + grants, r = read. That example is on the slide.",
  M4 + " (Symbolic Mode Characters, s.32)")
Q("perms", "Remove read permission for others on file1 (symbolic)", "chmod o-r file1",
  "chmod o-r file1: - removes a permission. Operators: + grants, - removes, = sets exactly.",
  M4 + " (Symbolic Mode Characters, s.32)")
Q("perms", "Give read and write to group and others on file1 (symbolic)", "chmod go+rw file1;;chmod og+rw file1",
  "chmod go+rw file1: go = group and others, + grants, rw = read and write. That example is on the slide.",
  M4 + " (Symbolic Mode Characters, s.32)")
Q("perms", "Set file1 to exactly user rw, group r, others nothing (symbolic, using =)", "chmod u=rw,g=r,o= file1;;chmod u=rw,g=r,o=- file1",
  "chmod with = assigns permissions exactly as given: u=rw, g=r, and o= with nothing after it clears others. Separate the clauses with commas and no spaces.",
  M4 + " (Symbolic Mode: = assigns permissions exactly)")
Q("perms", "Give the owner execute permission on script.sh (symbolic)", "chmod u+x script.sh",
  "chmod u+x: u = user (owner), + grants, x = execute. You need execute permission to run a script with ./",
  M4 + " (Symbolic Mode Characters) + " + M2 + " (Scripting: set executable permission)")
Q("perms", "Give everyone (all identities) read permission on file1", "chmod a+r file1;;chmod ugo+r file1;;chmod +r file1",
  "chmod a+r: a = all (user, group, others). Symbolic mode uses contexts u/g/o/a, operators +/-/= and attributes r/w/x.",
  M4 + " (Absolute and Symbolic Modes: contexts u/g/o/a)")
Q("perms", "Set /data and everything under it to 755 (recursive)", "chmod -R 755 /data",
  "chmod -R applies the change recursively. Heads up: the slide lists it as '-r recursive changes', but the real option is capital -R; lowercase -r would mean 'remove read'.",
  M4 + " (Absolute and Symbolic Modes: chmod options)")
Q("perms", "Show the current umask", "umask",
  "umask controls default permissions: it defines which permissions are masked (cleared) on new files and directories. With no argument it prints the current mask.",
  M4 + " (Default Permissions)")
Q("perms", "Set the umask to 022 for this session", "umask 022",
  "umask 022 sets the mask temporarily. Put it in ~/.bashrc or ~/.profile to keep it permanently. With 022, new files get 666 - 022 = 644.",
  M4 + " (Command - umask; Setting umask)")
Q("perms", "Where do you put the umask command to make it permanent for your user?", "~/.bashrc;;.bashrc;;~/.profile;;.profile",
  "Setting umask at the CLI is temporary. Put it in ~/.bashrc or ~/.profile to keep it.",
  M4 + " (Setting umask)")
Q("perms", "With umask 022, what permissions does a NEW FILE get? (octal)", "644",
  "Non-executable files start at 666 (rw-rw-rw-). The mask 022 removes write from group and others: 666 - 022 = 644 (rw-r--r--). That exact example is on the slide.",
  M4 + " (Command - umask, s.37)", loose=True)
Q("perms", "Change the owner of file1 to alice (keep the group)", "chown alice file1",
  "chown newowner filename changes the owner but not the group. Only root (the superuser) can change ownership of someone else's file.",
  M4 + " (Use the chown Command: Example 1)")
Q("perms", "Change file1's owner to alice AND its group to developers", "chown alice:developers file1",
  "chown newowner:newgroup filename changes both at once.",
  M4 + " (Use the chown Command: Example 2)")
Q("perms", "Change only the group of file1 to developers, using chown", "chown :developers file1",
  "chown :newgroup filename (colon with no owner) changes only the group.",
  M4 + " (Use the chown Command: Example 3)")
Q("perms", "Change only the group of file1 to developers, using chgrp", "chgrp developers file1",
  "chgrp {group} {file} changes the group ownership of a file or directory.",
  M4 + " (The chgrp Command)")
Q("perms", "Set the immutable flag on file1", "chattr +i file1",
  "chattr changes attributes. +i marks the file immutable: no one, not even root, can rename, delete or write to it.",
  M4 + " (The chattr Command; Use Attribute Management Commands)")
Q("perms", "Remove the immutable attribute from file1", "chattr -i file1",
  "chattr -i removes the immutable attribute. chattr -R changes attributes recursively.",
  M4 + " (The chattr Command)")
Q("perms", "Display the attributes of file1", "lsattr file1",
  "lsattr shows file attributes; a lowercase i means the immutable flag is set.",
  M4 + " (Use Attribute Management Commands)")

# ---- Module 5: special permissions (CertMaster lesson 3.2)
Q("special", "Set the SUID bit on /usr/bin/prog (symbolic)", "chmod u+s /usr/bin/prog",
  "chmod u+s sets SUID (Set User ID): users run the file with the privileges of the file's OWNER. passwd uses it to update password files as root.",
  M5 + " (User ID and Group ID Concepts: symbolic +s)", tip="runs as the file's owner")
Q("special", "Set SUID on /usr/bin/prog with permissions 755, in absolute mode", "chmod 4755 /usr/bin/prog",
  "chmod's absolute mode puts the special digit in front: 4 for SUID, 2 for SGID. 4755 = SUID + rwxr-xr-x.",
  M5 + " (User ID and Group ID Concepts: absolute 4 for SUID)")
Q("special", "Set the SGID bit on the directory /projects (symbolic)", "chmod g+s /projects",
  "chmod g+s sets SGID. On a directory, new files and subdirectories inherit the directory's group. It's the exact command from the class demo.",
  M5 + " (Demo - using SGID, s.17)", tip="new files inherit the directory's group")
Q("special", "Set SGID on /projects with permissions 775, in absolute mode", "chmod 2775 /projects",
  "chmod 2775: the leading 2 = SGID, and 775 = rwxrwxr-x.",
  M5 + " (User ID and Group ID Concepts: absolute 2 for SGID)")
Q("special", "Change the group of /projects to Managers (as in the SGID demo)", "chgrp Managers /projects;;chown :Managers /projects",
  "chgrp Managers /projects changes the group from root to Managers, so files created there inherit Managers once SGID is set.",
  M5 + " (Demo - using SGID, s.18)")
Q("special", "Set the sticky bit on the directory /Images", "chmod +t /Images;;chmod o+t /Images",
  "The sticky bit is set with chmod (+t). In that directory only the file owner, the directory owner or root can delete a file; others with write access cannot.",
  M5 + " (Understand Sticky Bit; Demo - sticky bit)", tip="only owner / dir owner / root can delete")
Q("special", "Which letter in the others-execute position shows the sticky bit in ls -al?", "t;;T",
  "The sticky bit shows as t (or T) in the others-execute position, e.g. drwxrwxrwt.",
  M5 + " (Understand Sticky Bit)", loose=True)
Q("special", "In absolute mode, which digit sets SUID?", "4",
  "The special permissions use the same 4-2 pattern as r-w: 4 = SUID, 2 = SGID, written in front of the normal three digits (4755).",
  M5 + " (User ID and Group ID Concepts)", loose=True)
Q("special", "In absolute mode, which digit sets SGID?", "2",
  "2 = SGID (as in 2775). 4 = SUID.",
  M5 + " (User ID and Group ID Concepts)", loose=True)
Q("special", "Remove the SUID bit from /usr/bin/prog (symbolic)", "chmod u-s /usr/bin/prog",
  "chmod u-s removes SUID; the - operator takes a permission away, just like chmod o-r.",
  M5 + " (special permissions) + " + M4 + " (symbolic operators)")
Q("special", "With the sticky bit set, who besides the file owner and root can delete a file?", "directory owner;;the directory owner;;owner of the directory",
  "With the sticky bit, only the file owner, the directory owner or root can delete it. In the demo, User2 could not delete User1's file.",
  M5 + " (Understand Sticky Bit, s.21)", loose=True)

# ---- Module 5: access control lists (CertMaster lesson 3.3)
Q("acl", "Display the ACL of fileA", "getfacl fileA",
  "getfacl {file} displays a file's ACL settings. The key demonstration starts by running getfacl fileA.",
  M5 + " (Demo on ACL; Key Demonstration: Configure ACLs)")
Q("acl", "ACL: give userA read-only access to file1", "setfacl -m u:userA:r file1;;setfacl -m u:userA:r-- file1",
  "setfacl -m modifies the ACL. u:{user}:{perms} is a user entry. The demo gives userA r and userB rw on the same file, which standard permissions can't do.",
  M5 + " (Demo on ACL, s.41)")
Q("acl", "ACL: give userB read and write on file1", "setfacl -m u:userB:rw file1;;setfacl -m u:userB:rw- file1",
  "setfacl -m u:userB:rw file1 gives userB read and write through the ACL, even though userB is in the same group as userA.",
  M5 + " (Demo on ACL, s.41)")
Q("acl", "ACL: change group1's permission to rw on file2", "setfacl -m g:group1:rw file2;;setfacl -m g:group1:rw- file2",
  "setfacl -m with g:{group}:{perms} sets a group entry. This is the exact slide task.",
  M5 + " (The setfacl Command, s.45)")
Q("acl", "Remove userA's entry from the ACL of file1", "setfacl -x u:userA file1",
  "setfacl -x removes entries from the existing ACL. Give the entry without permissions: u:userA.",
  M5 + " (The setfacl Command: -x)")
Q("acl", "Remove ALL ACL entries from file1", "setfacl -b file1",
  "setfacl -b removes all ACL entries, leaving only the standard owner/group/other permissions.",
  M5 + " (The setfacl Command: -b)")
Q("acl", "Recursively give userA rwx on the directory /project via ACL", "setfacl -R -m u:userA:rwx /project;;setfacl -Rm u:userA:rwx /project",
  "setfacl -R recursively sets ACL options for a directory and its contents; -m modifies the entry.",
  M5 + " (The setfacl Command: -R)")
Q("acl", "Which setfacl option sets/replaces the entire existing ACL?", "-s",
  "setfacl options from the slide: -R recursive, -s set (replace) the ACL, -m modify, -x remove entries, -b remove all entries.",
  M5 + " (The setfacl Command)", loose=True)

# ---- Module 6: navigate the file system (CertMaster lesson 4.1, taught after the midterm)
Q("files", "Create a directory named dir1", "mkdir dir1",
  "mkdir creates a directory; the lab creates dir1 and dir2.",
  M6 + " (Creating Directories)")
Q("files", "Show file1's metadata (inode, size, timestamps)", "stat file1",
  "stat {file} displays the file's metadata: size, inode, permissions and timestamps.",
  M6 + " (File Metadata)")
Q("files", "Create a hard link named file2-hl to file2", "ln file2 file2-hl",
  "ln with no option makes a hard link: another name for the same data (same inode). If the original is deleted, the data is still there through the link. Hard links only work for files on the same file system.",
  M6 + " (Hard Link, s.30)")
Q("files", "Create a symbolic (soft) link named file3-sl to file3", "ln -s file3 file3-sl",
  "ln -s creates a symbolic (soft) link, a shortcut. Target first, then the link name. If the original is deleted, the symlink breaks. It can cross file systems.",
  M6 + " (Soft Link, s.34)")
Q("files", "Long listing of file2 and file2-hl showing their inode numbers", "ls -li file2 file2-hl;;ls -il file2 file2-hl",
  "ls -li adds the inode number (-i) to the long listing (-l). Hard links share the same inode number.",
  M6 + " (Hard Link, s.30)")
Q("files", "Search /etc for a file named passwd", "find /etc -name passwd",
  "find {where to search} {option} {criteria}. -name searches by name. That example is on the slide.",
  M6 + " (Command - find)")
Q("files", "Find only regular files, starting from the current directory", "find -type f;;find . -type f",
  "find -type f searches by resource type file; -type d searches for directories. With no path, find starts in the current directory.",
  M6 + " (Command - find)")
Q("files", "Find only directories, starting from the current directory", "find -type d;;find . -type d",
  "find -type d matches directories; -type f matches regular files.",
  M6 + " (Command - find)")
Q("files", "Which directory is the mount point for temporarily mounting file systems?", "/mnt",
  "From the standard directories table: /mnt is for temporary mounts, /media is for removable media, /tmp is for temporary files, and /opt is for optional software packages.",
  M6 + " (Standard Directories)")
Q("files", "Which directory holds temporary files?", "/tmp",
  "/tmp holds temporary files. /var holds variable files that are expected to change constantly.",
  M6 + " (Standard Directories)")

# ---- Module 6: text commands (taught after the midterm)
Q("text", "Write the text hello into file1 using echo (overwrite)", "echo hello > file1;;echo \"hello\" > file1",
  "echo displays a line of text, and with redirection (>) it writes the text into a file, replacing what was there.",
  M6 + " (The echo Command)")
Q("text", "Convert 'Hello World' to uppercase with echo and tr", "echo \"Hello World\" | tr \"a-z\" \"A-Z\";;echo \"Hello World\" | tr a-z A-Z",
  "tr (translate) translates or deletes characters. Pipe echo into tr \"a-z\" \"A-Z\" to turn lowercase into uppercase. That exact command is on the slide.",
  M6 + " (Command - tr)")
Q("text", "Count the lines, words and bytes in file1", "wc file1",
  "wc counts lines, words and bytes (characters) in a file, printed in that order with the file name. With several files it also prints a total.",
  M6 + " (The wc Command)")
Q("text", "Sort the lines of file1", "sort file1",
  "sort arranges the lines in a file. Options: -r descending, -n numeric, -k column, -t delimiter.",
  M6 + " (The sort Command)")
Q("text", "Sort the lines of file1 in descending (reverse) order", "sort -r file1",
  "sort -r sorts in descending order.",
  M6 + " (The sort Command)")
Q("text", "Cut the first space-separated field from each line of file1", "cut -d' ' -f1 file1;;cut -d ' ' -f1 file1;;cut -f1 -d' ' file1",
  "cut extracts text from each line: -d sets the delimiter (here a space) and -f the field number. The slide's command is cut -d' ' -f1 file1.",
  M6 + " (The cut Command, s.54)")
Q("text", "Compare file2 and file3 side by side", "sdiff file2 file3",
  "sdiff shows two files side by side and marks the lines that differ.",
  M6 + " (The sdiff command)")
Q("text", "Print the first field of every line in file1 with awk", "awk '{print $1}' file1",
  "awk does pattern matching: the pattern, then the action in curly braces { }, then the file name. $1 = the first field. Single-quote the action.",
  M6 + " (The awk command)")
Q("text", "Globally replace every 'old' with 'new' in file1 using sed", "sed 's/old/new/g' file1",
  "sed is the stream editor. s substitutes the first occurrence on each line, and s with g substitutes every occurrence globally.",
  M6 + " (The sed Command: s, g)")
Q("text", "Delete the lines matching 'error' from the output of file1 using sed", "sed '/error/d' file1",
  "sed's d command deletes the lines matching a pattern: /error/d.",
  M6 + " (The sed Command: d)")

for _q in BANK:
    _q["id"] = _q["topic"] + "|" + _q["prompt"]

# --------------------------------------------------------------------------- answer checking
CLUSTER = re.compile(r"^-[A-Za-z]{2,}$")


def canon(text):
    """Tokenise like a shell, drop sudo, ignore quote style, sort letters in -la style groups."""
    text = text.strip()
    try:
        toks = shlex.split(text, posix=True)
    except ValueError:
        toks = text.split()
    while toks and toks[0] == "sudo":
        toks = toks[1:]
    out = []
    for t in toks:
        out.append("-" + "".join(sorted(t[1:])) if CLUSTER.match(t) else t)
    return out


def loose_key(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def check_loose(given, accepted):
    g = loose_key(given)
    return bool(g) and any(g == loose_key(a) for a in accepted)


def check_typed(given, accepted):
    g = canon(given)
    return bool(g) and any(g == canon(a) for a in accepted)


# --------------------------------------------------------------------------- generated permission drills
def triple(n):
    return "".join(ch if n & bit else "-" for ch, bit in (("r", 4), ("w", 2), ("x", 1)))


def mode_str(octal4):
    """4-digit octal int like 0o4755 -> 'rwsr-xr-x'."""
    sp, u, g, o = (octal4 >> 9) & 7, (octal4 >> 6) & 7, (octal4 >> 3) & 7, octal4 & 7
    s = [triple(u), triple(g), triple(o)]
    if sp & 4:
        s[0] = s[0][:2] + ("s" if u & 1 else "S")
    if sp & 2:
        s[1] = s[1][:2] + ("s" if g & 1 else "S")
    if sp & 1:
        s[2] = s[2][:2] + ("t" if o & 1 else "T")
    return "".join(s)


def apply_chmod(mode9, expr):
    """Apply 'u+x,g-w,o=r' to a 9-bit mode; returns new 9-bit mode."""
    shifts = {"u": 6, "g": 3, "o": 0}
    for clause in expr.split(","):
        m = re.match(r"^([ugoa]*)([+\-=])([rwx]*)$", clause)
        who, op, perms = m.groups()
        who = "ugo" if who in ("", "a") else who
        bits = sum({"r": 4, "w": 2, "x": 1}[p] for p in perms)
        for w in who:
            sh = shifts[w]
            cur = (mode9 >> sh) & 7
            new = cur | bits if op == "+" else cur & ~bits if op == "-" else bits
            mode9 = (mode9 & ~(7 << sh)) | (new << sh)
    return mode9


def digit_parts(d):
    """7 -> '4+2+1 = rwx', 5 -> '4+1 = r-x', 0 -> '0 = ---'."""
    parts = [str(v) for v in (4, 2, 1) if d & v]
    return f"{'+'.join(parts)} = {triple(d)}" if len(parts) > 1 else f"{d} = {triple(d)}"


def groups_breakdown(o):
    names = ("owner", "group", "other")
    return "   ".join(f"{n} {(o >> sh) & 7}: {digit_parts((o >> sh) & 7)}" for n, sh in zip(names, (6, 3, 0)))


def drill_str_to_octal():
    o = random.choice([0o755, 0o644, 0o640, 0o750, 0o700, 0o600, 0o664, 0o775, 0o754, 0o444, 0o711, 0o660, 0o777, 0o500])
    s = mode_str(o)
    def one(i, sh):
        parts = [str(v) for v, ch in zip((4, 2, 1), s[i:i + 3]) if ch != "-"]
        d = (o >> sh) & 7
        return f"{s[i:i + 3]} = {'+'.join(parts)} = {d}" if len(parts) > 1 else f"{s[i:i + 3]} = {d}"
    steps = "   ".join(one(i, sh) for i, sh in ((0, 6), (3, 3), (6, 0)))
    return ("What octal mode is " + s + " ?", [f"{o:03o}"],
            f"Split into owner/group/other and add r=4 w=2 x=1 in each:  {steps}  ->  {o:03o}")


def drill_octal_to_str():
    o = random.choice([0o755, 0o644, 0o640, 0o750, 0o700, 0o600, 0o664, 0o775, 0o754, 0o444, 0o711, 0o660, 0o740])
    return (f"What does mode {o:03o} look like in ls -l (9 characters, no leading -)?", [mode_str(o)],
            f"Each digit is one group, built from 4=r 2=w 1=x:  {groups_breakdown(o)}  ->  {mode_str(o)}")


def drill_symbolic():
    start = random.choice([0o644, 0o755, 0o640, 0o700, 0o600, 0o664, 0o750])
    expr = random.choice(["u+x", "g+w", "o-r", "go-rx", "a+r", "u=rwx,g=rx,o=", "g=rw", "o+w", "u-w", "ug+x", "a-x", "o=r"])
    res = apply_chmod(start, expr)
    words = {"u": "owner", "g": "group", "o": "other", "a": "everyone", "+": "add", "-": "remove", "=": "set exactly"}
    said = []
    for clause in expr.split(","):
        m = re.match(r"^([ugoa]*)([+\-=])([rwx]*)$", clause)
        who = "+".join(words[w] for w in (m.group(1) or "a"))
        said.append(f"{clause} = {words[m.group(2)]} {m.group(3) or 'nothing'} for {who}")
    return (f"A file is {start:03o}. After chmod {expr} file, what is its octal mode?", [f"{res:03o}"],
            f"{start:03o} is {mode_str(start)}. {'; '.join(said)}. Result: {mode_str(res)} = {res:03o}.")


def drill_umask():
    mask = random.choice([0o022, 0o002, 0o027, 0o077, 0o007, 0o037, 0o026])
    kind = "file"  # the Module 4 slides teach umask from the 666 file default
    base = 0o666 if kind == "file" else 0o777
    res = base & ~mask
    steps = []
    for sh, n in ((6, "owner"), (3, "group"), (0, "other")):
        b, m, r = (base >> sh) & 7, (mask >> sh) & 7, (res >> sh) & 7
        steps.append(f"{n} {triple(b)} minus {triple(m)} = {triple(r)} ({r})")
    note = "" if kind == "directory" or not (mask & 0o111) else " A file has no x to remove, so mask bit 1 changes nothing."
    return (f"umask {mask:03o}: what permissions does a new {kind} get? (octal)", [f"{res:03o}"],
            f"New {kind}s start at {base:03o}; the umask REMOVES its bits:  " + "   ".join(steps) + f"  ->  {res:03o}.{note}")


# Module 5 teaches SUID (4) and SGID (2) in absolute mode, so the drills stick to those.
SPECIAL_MODES = [0o4755, 0o2755, 0o2770, 0o6755, 0o4700, 0o2775, 0o2750, 0o4711]


def special_note(o):
    sp = (o >> 9) & 7
    bits = []
    if sp & 4:
        bits.append("4 = SUID: s replaces the owner's x")
    if sp & 2:
        bits.append("2 = SGID: s replaces the group's x")
    if sp & 1:
        bits.append("1 = sticky: t replaces the others' x")
    parts = [str(v) for v in (4, 2, 1) if sp & v]
    head = f"First digit {sp}" + (f" = {' + '.join(parts)}" if len(parts) > 1 else "")
    return head + ": " + "; ".join(bits) + "."


def drill_special_to_str():
    o = random.choice(SPECIAL_MODES)
    return (f"What does mode {o:04o} look like in ls -l (9 characters)?", [mode_str(o)],
            f"Last three digits {o & 0o777:03o} = {mode_str(o & 0o777)}. {special_note(o)}  ->  {mode_str(o)}")


def drill_str_to_special():
    o = random.choice(SPECIAL_MODES)
    return (f"What 4-digit octal mode is {mode_str(o)} ?", [f"{o:04o}"],
            f"Read the s/t letters first: {special_note(o)} The rest is {mode_str(o & 0o777)} = {o & 0o777:03o}, so {o:04o}.")


DRILLS = [drill_str_to_octal, drill_octal_to_str, drill_symbolic, drill_umask, drill_special_to_str, drill_str_to_special]

# --------------------------------------------------------------------------- progress
def load():
    try:
        with open(SAVE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"q": {}, "best": 0, "sessions": 0}


def save(db):
    try:
        with open(SAVE, "w", encoding="utf-8") as f:
            json.dump(db, f)
    except OSError:
        pass


def rec(db, qid):
    return db["q"].setdefault(qid, {"right": 0, "wrong": 0, "streak": 0})


def is_missed(db, qid):
    r = db["q"].get(qid)
    return bool(r) and r["wrong"] > 0 and r["streak"] < 2


def pick(db, pool, n):
    """Weighted draw without repeats: missed questions come up more, mastered ones less."""
    pool = list(pool)
    chosen = []
    while pool and len(chosen) < n:
        weights = []
        for q in pool:
            r = db["q"].get(q["id"])
            if not r:
                weights.append(3.0)  # unseen
            else:
                weights.append(max(0.4, 1 + 2.5 * min(r["wrong"], 3) - 0.8 * min(r["streak"], 3)))
        q = random.choices(pool, weights)[0]
        pool.remove(q)
        chosen.append(q)
    return chosen


# --------------------------------------------------------------------------- palette and terminal
MATRIX = (0, 255, 65)
MATRIX_HI = (190, 255, 200)
GREEN = (0, 200, 60)
DARK = (0, 110, 30)
DIM = (0, 85, 30)
GREY = (120, 140, 125)
WHITE = (225, 255, 230)
CYAN = (0, 229, 255)
MAGENTA = (255, 60, 200)
YELLOW = (255, 214, 0)
ORANGE = (255, 140, 0)
RED = (255, 50, 80)
PURPLE = (170, 120, 255)
BLUE = (110, 160, 255)

TOPIC_COLOR = {
    "basics": CYAN, "accounts": BLUE, "shell": MAGENTA, "perms": YELLOW, "special": ORANGE,
    "acl": PURPLE, "files": (0, 210, 180), "text": (255, 120, 190), "packages": (150, 255, 120),
    "storage": (200, 200, 210), "drill": MATRIX,
}

RANKS = [(0, "Script Kiddie"), (300, "Shell Rookie"), (800, "Sudoer"), (1600, "Sysadmin"),
         (3000, "Root"), (5000, "Kernel Hacker")]

if PLAIN:
    SYM = dict(ok="OK", bad="X", arrow=">", prompt=">", full="#", empty=".", star="*", bolt="!",
               tl="+", tr="+", bl="+", br="+", h="-", v="|", dot="*", sel=">")
else:
    SYM = dict(ok="✔", bad="✘", arrow="▶", prompt="❯", full="█", empty="░", star="★", bolt="⚡",
               tl="╭", tr="╮", bl="╰", br="╯", h="─", v="│", dot="•", sel="▶")

RESET = "\033[0m" if COLOR else ""
BOLD = "\033[1m" if COLOR else ""
ANSI_RE = re.compile(r"\033\[[0-9;?]*[A-Za-z]|\033\][^\a]*\a")


def fg(rgb):
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m" if COLOR else ""


def bg(rgb):
    return f"\033[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m" if COLOR else ""


def paint(text, rgb, bold=False):
    if not COLOR:
        return text
    return (BOLD if bold else "") + fg(rgb) + text + RESET


def gradient(text, a, b, bold=False):
    if not COLOR:
        return text
    n = max(1, len(text) - 1)
    out = [BOLD] if bold else []
    for i, ch in enumerate(text):
        t = i / n
        out.append(fg(tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))) + ch)
    return "".join(out) + RESET


def vlen(s):
    return len(ANSI_RE.sub("", s))


def out(s=""):
    sys.stdout.write(s)
    sys.stdout.flush()


def width():
    return max(44, min(78, shutil.get_terminal_size((80, 24)).columns - 2))


def clear():
    if INTERACTIVE:
        out("\033[2J\033[H")


def term_setup():
    if INTERACTIVE and COLOR:
        out("\033]12;#00ff41\a\033[1 q")  # Matrix-green blinking block cursor


def term_restore():
    if INTERACTIVE:
        out("\033[0m\033]112\a\033[0 q\033[?25h")


atexit.register(term_restore)

# --------------------------------------------------------------------------- keyboard
if os.name == "nt":
    import msvcrt

    def getkey():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(msvcrt.getwch(), "")
        if ch == "\x03":
            raise KeyboardInterrupt
        return {"\r": "enter", "\n": "enter", "\x1b": "esc", " ": "space", "\x08": "backspace"}.get(ch, ch)

    def kbhit():
        return msvcrt.kbhit()

    def flush_keys():
        while msvcrt.kbhit():
            msvcrt.getwch()

    class cbreak:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
else:
    import select
    import termios
    import tty

    def getkey():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = os.read(fd, 1).decode(errors="ignore")
            if ch == "\x1b":
                if select.select([fd], [], [], 0.03)[0]:
                    seq = os.read(fd, 2).decode(errors="ignore")
                    return {"[A": "up", "[B": "down", "[C": "right", "[D": "left"}.get(seq, "esc")
                return "esc"
            if ch == "\x03":
                raise KeyboardInterrupt
            return {"\r": "enter", "\n": "enter", " ": "space", "\x7f": "backspace"}.get(ch, ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def kbhit():
        return bool(select.select([sys.stdin], [], [], 0)[0])

    def flush_keys():
        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)

    class cbreak:
        """Lets kbhit() see single keypresses during animations."""

        def __enter__(self):
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            return self

        def __exit__(self, *a):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
            return False


def pause(seconds):
    """Sleep, but any key cuts it short."""
    if not ANIM:
        return
    end = time.time() + seconds
    with cbreak():
        while time.time() < end:
            if kbhit():
                flush_keys()
                return
            time.sleep(0.02)


def wait_key(msg="press any key"):
    if not INTERACTIVE:
        return
    out(paint(f"  {SYM['arrow']} {msg}", DARK))
    flush_keys()
    try:
        getkey()
    except KeyboardInterrupt:
        pass
    out("\r\033[2K")


# --------------------------------------------------------------------------- effects
GLYPHS = "0123456789ABCDEFXZ$#@%&*+=-<>/\\|{}[]?!:;"

LOGO = {
    "C": [" ████ ", "██    ", "██    ", "██    ", " ████ "],
    "M": ["██   ██", "███ ███", "██ █ ██", "██   ██", "██   ██"],
    "D": ["█████ ", "██  ██", "██  ██", "██  ██", "█████ "],
    "Q": [" ████ ", "██  ██", "██  ██", "██ ██ ", " ██ ██"],
    "U": ["██  ██", "██  ██", "██  ██", "██  ██", " ████ "],
    "I": ["██", "██", "██", "██", "██"],
    "Z": ["██████", "   ██ ", "  ██  ", " ██   ", "██████"],
}


def logo_lines():
    rows = ["  ".join(LOGO[ch][r] for ch in "CMDQUIZ") for r in range(5)]
    return [r.replace("█", "#") for r in rows] if PLAIN else rows


def typewrite(text, delay=0.007):
    """Print text a character at a time (instant if a key is pressed or animations are off)."""
    if not ANIM:
        out(text)
        return
    plain = ANSI_RE.split(text)
    codes = ANSI_RE.findall(text)
    with cbreak():
        for k, chunk in enumerate(plain):
            for ch in chunk:
                out(ch)
                if kbhit():
                    delay = 0
                if delay:
                    time.sleep(delay)
            if k < len(codes):
                out(codes[k])


def matrix_rain(seconds=1.8):
    cols, rows = shutil.get_terminal_size((80, 24))
    if cols < 50 or rows < 14:
        return
    trail = 10
    xs = list(range(0, cols - 1, 2))
    drops = {x: random.randint(-rows, 0) for x in xs}
    out("\033[?1049h\033[?25l\033[2J")
    try:
        end = time.time() + seconds
        with cbreak():
            while time.time() < end and not kbhit():
                buf = []
                for x in xs:
                    y = drops[x]
                    for yy, col in ((y, MATRIX_HI), (y - 1, MATRIX), (y - 4, GREEN), (y - 7, DARK)):
                        if 1 <= yy < rows:
                            buf.append(f"\033[{yy};{x + 1}H{fg(col)}{random.choice(GLYPHS)}")
                    if 1 <= y - trail < rows:
                        buf.append(f"\033[{y - trail};{x + 1}H ")
                    drops[x] += 1
                    if y - trail > rows:
                        drops[x] = random.randint(-rows // 2, 0)
                out("".join(buf))
                time.sleep(0.035)
            # decode the title out of the rain
            lines = logo_lines()
            w = len(lines[0])
            top = max(1, rows // 2 - 4)
            left = max(1, (cols - w) // 2 + 1)
            for frame in range(14):
                buf = []
                for r, line in enumerate(lines):
                    buf.append(f"\033[{top + r};{left - 2}H{' ' * (w + 4)}")
                    buf.append(f"\033[{top + r};{left}H")
                    for c_i, ch in enumerate(line):
                        if ch == " ":
                            buf.append(" ")
                        elif random.random() < frame / 13:
                            t = c_i / max(1, w - 1)
                            buf.append(fg((0, round(255 - 90 * t), round(65 + 120 * t))) + BOLD + ch + RESET)
                        else:
                            buf.append(fg(DARK) + random.choice(GLYPHS))
                out("".join(buf))
                time.sleep(0.045)
            tag = "DCOM 142 // LINUX COMMAND TRAINER"
            out(f"\033[{top + 6};{max(1, (cols - len(tag)) // 2 + 1)}H")
            typewrite(paint(tag, WHITE, True), 0.012)
            flush_keys()
        pause(0.9)
    finally:
        out(RESET + "\033[?25h\033[?1049l")


def glitch(text, rgb):
    """Flicker random glyphs before settling on the text."""
    if not ANIM:
        out(paint(text, rgb, True) + "\n")
        return
    for _ in range(4):
        noise = "".join(random.choice(GLYPHS) if ch != " " else " " for ch in text)
        out("\r\033[2K" + paint(noise, rgb))
        time.sleep(0.04)
    out("\r\033[2K" + paint(text, rgb, True) + "\n")


def bar(frac, n, on=MATRIX, off=DIM):
    k = max(0, min(n, round(frac * n)))
    return paint(SYM["full"] * k, on) + paint(SYM["empty"] * (n - k), off)


def box(title, right, body):
    """A rounded box: title on the top border, one or more body lines."""
    w = width()
    t = f"{SYM['h']} {title} "
    r = f" {right} {SYM['h']}" if right else SYM["h"]
    fill = max(1, w - 2 - vlen(t) - vlen(r))
    print(paint(SYM["tl"], DARK) + paint(t, MATRIX, True) + paint(SYM["h"] * fill, DARK) + paint(r, GREY) + paint(SYM["tr"], DARK))
    for line in body:
        pad = max(0, w - 4 - vlen(line))
        print(paint(SYM["v"], DARK) + " " + line + " " * pad + " " + paint(SYM["v"], DARK))
    print(paint(SYM["bl"] + SYM["h"] * (w - 2) + SYM["br"], DARK))


def streak_txt(s):
    if s >= 10:
        return paint(f"{SYM['bolt']}x{s} UNSTOPPABLE", MAGENTA, True)
    if s >= 5:
        return paint(f"{SYM['bolt']}x{s} ON FIRE", ORANGE, True)
    if s >= 2:
        return paint(f"x{s} streak", YELLOW, True)
    return paint("no streak", GREY)


def rank_for(xp):
    cur, nxt = RANKS[0], None
    for i, r in enumerate(RANKS):
        if xp >= r[0]:
            cur, nxt = r, (RANKS[i + 1] if i + 1 < len(RANKS) else None)
    return cur, nxt


def rank_line(db):
    xp = db.get("xp", 0)
    (lo, name), nxt = rank_for(xp)
    if nxt:
        frac = (xp - lo) / (nxt[0] - lo)
        prog = f"{bar(frac, 16, CYAN)} {paint(f'{xp}/{nxt[0]} XP', GREY)}"
    else:
        prog = paint(f"{xp} XP  MAX RANK", MAGENTA, True)
    return f"{paint('RANK', GREY)} {paint(name.upper(), CYAN, True)}  {prog}"


# --------------------------------------------------------------------------- input
def ask(prompt):
    """Read a line with a Matrix-green prompt and Matrix-green typed text."""
    out(paint(prompt, MATRIX, True) + (BOLD + fg(MATRIX) if COLOR else ""))
    try:
        return input()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    finally:
        out(RESET)


def yes_no(prompt):
    if INTERACTIVE:
        out(paint(prompt + " [y/N] ", GREY))
        flush_keys()
        try:
            k = getkey()
        except KeyboardInterrupt:
            k = "n"
        print(paint("y", MATRIX, True) if k in ("y", "Y") else paint("n", GREY))
        return k in ("y", "Y")
    a = ask(prompt + " (y/N) ")
    return bool(a) and a.strip().lower() == "y"


def menu(options, title=None):
    """Arrow-key menu. options: list of (key, label, note). Returns a key, or None for quit."""
    if not INTERACTIVE:
        for key, label, note in options:
            print(f"  {key}) {label:<18} {note}")
        a = ask(f"{SYM['prompt']} ")
        if a is None:
            return None
        a = a.strip().lower()
        return a if a in [o[0] for o in options] else ""
    sel = 0

    def draw(first):
        if not first:
            out(f"\033[{len(options)}A")
        for i, (key, label, note) in enumerate(options):
            out("\r\033[2K")
            if i == sel:
                line = f" {SYM['sel']} {key}  {label:<20}"
                out(bg((0, 70, 20)) + BOLD + fg(MATRIX_HI) + line + RESET + "  " + paint(note, MATRIX) + "\n")
            else:
                out(f"   {paint(key, DARK)}  {paint(f'{label:<20}', GREEN)}  {paint(note, GREY)}\n")

    out("\033[?25l")
    try:
        draw(True)
        out(paint(f"\n  {SYM['h'] * 2} arrows/j/k move  {SYM['dot']}  enter or number picks  {SYM['dot']}  q quits", DARK))
        out("\033[1A\r")
        while True:
            k = getkey()
            if k in ("up", "k"):
                sel = (sel - 1) % len(options)
            elif k in ("down", "j"):
                sel = (sel + 1) % len(options)
            elif k == "enter":
                return options[sel][0]
            elif k in ("q", "esc"):
                return None
            else:
                for i, o in enumerate(options):
                    if k == o[0]:
                        sel = i
                        draw(False)
                        return o[0]
                continue
            draw(False)
    except KeyboardInterrupt:
        return None
    finally:
        out("\033[?25h\n\n")


def checklist(options):
    """Space toggles, a = all, enter confirms. options: list of (key, label, note). Returns keys."""
    if not INTERACTIVE:
        for i, (key, label, note) in enumerate(options, 1):
            print(f"  {i:>2}) {key:<9} {note}")
        s = ask("Topic number(s), e.g. 3 or 3,4,5 > ")
        picked = []
        for part in re.split(r"[,\s]+", (s or "").strip()):
            if part.isdigit() and 1 <= int(part) <= len(options):
                picked.append(options[int(part) - 1][0])
        return picked
    sel, on = 0, set()

    def draw(first):
        if not first:
            out(f"\033[{len(options)}A")
        for i, (key, label, note) in enumerate(options):
            box_ = f"[{SYM['ok'] if key in on else ' '}]"
            col = TOPIC_COLOR.get(key, GREEN)
            row = f" {box_} {key:<9} {note}"
            out("\r\033[2K")
            if i == sel:
                out(bg((0, 70, 20)) + BOLD + fg(MATRIX_HI) + f" {SYM['sel']}" + row + " " + RESET + "\n")
            else:
                out("   " + paint(box_, MATRIX if key in on else DARK) + " " + paint(f"{key:<9}", col, key in on) + " " + paint(note, GREY) + "\n")

    out("\033[?25l")
    try:
        draw(True)
        out(paint(f"\n  {SYM['h'] * 2} space toggles  {SYM['dot']}  a = all midterm topics  {SYM['dot']}  enter starts  {SYM['dot']}  q back", DARK))
        out("\033[1A\r")
        while True:
            k = getkey()
            if k in ("up", "k"):
                sel = (sel - 1) % len(options)
            elif k in ("down", "j"):
                sel = (sel + 1) % len(options)
            elif k == "space":
                on ^= {options[sel][0]}
            elif k == "a":
                on = set(MIDTERM) if on != set(MIDTERM) else set()
            elif k == "enter":
                return [o[0] for o in options if o[0] in on] or [options[sel][0]]
            elif k in ("q", "esc"):
                return []
            draw(False)
    except KeyboardInterrupt:
        return []
    finally:
        out("\033[?25h\n\n")


# --------------------------------------------------------------------------- answer feedback
def raw_tokens(text):
    try:
        toks = shlex.split(text.strip(), posix=True)
    except ValueError:
        toks = text.split()
    while toks and toks[0] == "sudo":
        toks = toks[1:]
    return toks


def show_tok(t):
    """Re-quote a token for display the way you'd type it: ll='ls -la', '{print $1}'."""
    if not re.search(r"[\s{}]", t):
        return t
    name, eq, val = t.partition("=")
    if eq and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return f"{name}='{val}'"
    return f"'{t}'"


def show_diff(given, accepted):
    """Colour-code your answer against the closest accepted answer, token by token."""
    g_raw = [show_tok(t) for t in raw_tokens(given)]
    g = canon(given)
    best = max(accepted, key=lambda a: difflib.SequenceMatcher(None, g, canon(a)).ratio())
    c_raw, c = [show_tok(t) for t in raw_tokens(best)], canon(best)
    you, ans = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, g, c).get_opcodes():
        if op == "equal":
            you += [paint(t, MATRIX) for t in g_raw[i1:i2]]
            ans += [paint(t, MATRIX) for t in c_raw[j1:j2]]
        else:
            you += [paint(t, RED, True) for t in g_raw[i1:i2]]
            ans += [paint(t, YELLOW, True) for t in c_raw[j1:j2]]
    print(f"  {paint('you   ', GREY)} {' '.join(you) or paint('(nothing)', GREY)}")
    print(f"  {paint('answer', GREY)} {' '.join(ans)}")


def show_explanation(q):
    text = q.get("explain") or q.get("why")
    if not text:
        return
    w = width() - 6
    print()
    print("  " + paint(f"{SYM['h'] * 2} WHY ", CYAN, True) + paint(SYM["h"] * max(4, w - 6), DARK))
    for line in textwrap.wrap(text, w, break_on_hyphens=False):
        print(paint(f"  {SYM['v']} ", DARK) + paint(line, WHITE))
    if q.get("src"):
        print(paint(f"  {SYM['v']} ", DARK) + paint(f"source: {q['src']}", GREY))


# --------------------------------------------------------------------------- game loop
def play(db, source, title, time_limit=None):
    """source: a list of questions, or a callable returning the next one (None = done)."""
    if callable(source):
        nxt, total = source, None
    else:
        if not source:
            print(paint("Nothing to ask here yet.", YELLOW))
            wait_key()
            return
        it = iter(source)
        nxt, total = (lambda: next(it, None)), len(source)
    score = streak = best_streak = right = asked = 0
    t0 = time.time()
    if not INTERACTIVE:
        print(f"\n{title}  ({total or 'timed'} questions)")
        print("Type the command. ?=hint  skip=give up  q=end round. sudo and quote style don't matter.\n")
    while True:
        if time_limit and time.time() - t0 >= time_limit:
            return finish(db, title, score, right, asked, best_streak, t0, note="TIME UP")
        q = nxt()
        if q is None:
            break
        globals()["_current"] = q
        clear()
        i = asked + 1
        if time_limit:
            right_lbl = f"Q{i}  {SYM['bolt']} {max(0, int(time_limit - (time.time() - t0)))}s left"
            frac = max(0.0, 1 - (time.time() - t0) / time_limit)
        else:
            right_lbl = f"Q {i}/{total}"
            frac = asked / total
        box(title.upper(), right_lbl, [
            f"{bar(frac, 22, CYAN if time_limit else MATRIX)}   {paint('score', GREY)} {paint(str(score), WHITE, True)}   {streak_txt(streak)}",
        ])
        col = TOPIC_COLOR.get(q["topic"], GREEN)
        tag = paint(f"[{q['topic'].upper()}]", col, True)
        print()
        typewrite(f"  {tag} " + paint(q["prompt"], WHITE, True) + "\n\n")
        hinted, tries, ok, given, skipped = False, 0, False, None, False
        while True:
            ans = ask(f"  {SYM['prompt']} ")
            if ans is None or ans.strip().lower() in ("q", "quit", "exit"):
                return finish(db, title, score, right, asked, best_streak, t0, note="ENDED EARLY")
            a = ans.strip()
            if a == "?":
                hinted = True
                if q.get("loose"):
                    ans0 = q["answers"][0]
                    n = len(ans0)
                    if n <= 2:  # revealing the first character would give the whole answer away
                        print(paint(f"    hint: the answer is {n} character{'s' if n != 1 else ''} long", YELLOW))
                    else:
                        print(paint(f"    hint: starts with '{ans0[0]}' ({n} characters)", YELLOW))
                elif q.get("typed", True):
                    first = raw_tokens(q["answers"][0])
                    first = first[0] if first else q["answers"][0]
                    n_tok = len(raw_tokens(q["answers"][0]))
                    print(paint(f"    hint: starts with '{first}' ({n_tok} word{'s' if n_tok != 1 else ''})", YELLOW))
                else:
                    print(paint("    hint: r=4 w=2 x=1; special digit in front: 4=SUID 2=SGID; new files start at 666 minus the umask", YELLOW))
                continue
            if a == "" and tries == 0:
                if INTERACTIVE:
                    out("\033[1A\r\033[2K")  # redraw the prompt on the same line instead of adding a blank one
                continue
            if a.lower() in ("skip", "s", "idk", ""):
                skipped = True  # a bare Enter after a miss counts as the second attempt
                break
            given = a
            if q.get("loose"):
                ok = check_loose(a, q["answers"])
            elif q.get("typed", True):
                ok = check_typed(a, q["answers"])
            else:
                ok = a.lower().replace(" ", "") in [x.lower().replace(" ", "") for x in q["answers"]]
            if ok:
                break
            tries += 1
            if tries >= 2:
                break
            print(paint(f"    {SYM['bad']} not quite", RED, True) + paint(" - one more try  (Enter = show answer, ? = hint)", GREY))
        asked = i
        print()
        if ok:
            pts = 5 if hinted else 10
            bonus = min(streak, 5)
            streak += 1
            best_streak = max(best_streak, streak)
            score += pts + bonus
            right += 1
            glitch(f"  {SYM['ok']} ACCESS GRANTED   +{pts}" + (f"  +{bonus} streak" if bonus else ""), MATRIX)
            if q.get("why"):
                print(paint("    " + q["why"], GREY))
            if q["id"]:
                r = rec(db, q["id"]); r["right"] += 1; r["streak"] += 1
            if streak in (5, 10, 20):
                print(paint(f"\n  {SYM['bolt'] * 3} {streak} IN A ROW {SYM['bolt'] * 3}", MAGENTA, True))
            pause(0.9 if q.get("why") else 0.6)
        else:
            streak = 0
            glitch(f"  {SYM['bad']} ACCESS DENIED", RED)
            if given and q.get("typed", True):
                show_diff(given, q["answers"])
            else:
                if given:
                    print(f"  {paint('you   ', GREY)} {paint(given, RED, True)}")
                print(f"  {paint('answer', GREY)} {paint(q['answers'][0], YELLOW, True)}")
            if len(q["answers"]) > 1:
                print(paint("  also accepted: ", GREY) + paint("  |  ".join(q["answers"][1:]), DARK))
            show_explanation(q)
            counted = False
            if given and not skipped and q.get("typed", True):
                print()
                counted = yes_no("  Was yours actually valid? Count it anyway")
            if counted:
                score += 8
                right += 1
                if q["id"]:
                    r = rec(db, q["id"]); r["right"] += 1; r["streak"] += 1
                print(paint(f"  {SYM['ok']} counted", MATRIX))
                pause(0.6)
            else:
                if q["id"]:
                    r = rec(db, q["id"]); r["wrong"] += 1; r["streak"] = 0
                print()
                wait_key("study it, then press any key")
        if not INTERACTIVE:
            print()
    finish(db, title, score, right, asked, best_streak, t0)


def finish(db, title, score, right, asked, best_streak, t0, note=None):
    before = rank_for(db.get("xp", 0))[0]
    db["xp"] = db.get("xp", 0) + score
    after = rank_for(db["xp"])[0]
    new_best = score > db.get("best", 0)
    db["sessions"] = db.get("sessions", 0) + 1
    db["best"] = max(db.get("best", 0), score)
    save(db)
    secs = int(time.time() - t0)
    acc = right / asked if asked else 0
    clear()
    print()
    if not INTERACTIVE:
        print("Round over" if not note else f"Round over ({note})")
        print(f"  Correct: {right}/{asked}   Score: {score}   Best streak: {best_streak}   Time: {secs}s")
    else:
        head = "ROUND COMPLETE" if not note else note
        box(head, title, [
            f"{paint('correct ', GREY)} {paint(f'{right}/{asked}', WHITE, True)}   {bar(acc, 20, MATRIX if acc >= 0.8 else YELLOW if acc >= 0.5 else RED)} {paint(f'{acc:.0%}', WHITE)}",
            f"{paint('score   ', GREY)} {paint(str(score), WHITE, True)}" + (paint(f"   {SYM['star']} NEW BEST", MAGENTA, True) if new_best and score else ""),
            f"{paint('streak  ', GREY)} {paint(str(best_streak), WHITE, True)} best this round",
            f"{paint('time    ', GREY)} {secs}s",
            "",
            rank_line(db),
        ])
    if after != before:
        print()
        glitch(f"  {SYM['star']} RANK UP: {after[1].upper()} {SYM['star']}", MAGENTA)
    if asked:
        msg = ("Perfect. Root access confirmed." if acc == 1 else
               "Solid. Hit the missed ones next." if acc >= 0.8 else
               "Run it again - the ones you missed come back more often.")
        print(paint("\n  " + msg, MATRIX if acc >= 0.8 else YELLOW))
    print()
    wait_key("press any key for the menu")


def as_items(qs):
    return [dict(q, typed=not q.get("loose")) for q in qs]


def drill_items(n):
    items = []
    for _ in range(n):
        prompt, answers, why = random.choice(DRILLS)()
        items.append({"id": None, "topic": "drill", "prompt": prompt, "answers": answers, "why": "", "explain": why, "typed": False})
    return items


def lightning_source(db):
    """Endless weighted stream from the midterm topics, no repeats within the last 15."""
    pool = [q for q in BANK if q["topic"] in MIDTERM]
    recent = []

    def nxt():
        q = pick(db, [p for p in pool if p["id"] not in recent], 1)[0]
        recent.append(q["id"])
        del recent[:-15]
        return dict(q, typed=not q.get("loose"))
    return nxt


def show_stats(db):
    clear()
    seen = sum(1 for q in BANK if q["id"] in db["q"])
    mastered = sum(1 for q in BANK if db["q"].get(q["id"], {}).get("streak", 0) >= 2)
    missed = sum(1 for q in BANK if is_missed(db, q["id"]))
    rows = [rank_line(db), "",
            f"{paint('seen', GREY)} {paint(f'{seen}/{len(BANK)}', WHITE, True)}   {paint('mastered', GREY)} {paint(str(mastered), MATRIX, True)}   "
            f"{paint('still missed', GREY)} {paint(str(missed), RED if missed else GREY, True)}   {paint('rounds', GREY)} {db.get('sessions', 0)}   {paint('best', GREY)} {db.get('best', 0)}",
            ""]
    for key, label in TOPICS.items():
        qs = [q for q in BANK if q["topic"] == key]
        m = sum(1 for q in qs if db["q"].get(q["id"], {}).get("streak", 0) >= 2)
        col = TOPIC_COLOR.get(key, GREEN)
        star = paint(SYM["star"], YELLOW) if key in MIDTERM else " "
        rows.append(f"{star} {paint(f'{key:<9}', col, True)} {bar(m / len(qs), 18, col)} {paint(f'{m:>2}/{len(qs):<2}', WHITE)}")
    rows.append(paint(f"{SYM['star']} = on the midterm", GREY))
    box("PROGRESS", "", rows)
    weak = [q for q in BANK if is_missed(db, q["id"])]
    if weak:
        print(paint("\n  Still shaky:", YELLOW, True))
        for q in weak[:10]:
            print(paint(f"   {SYM['dot']} ", RED) + q["prompt"])
    print()
    wait_key()


def topic_menu(db):
    clear()
    box("PICK TOPICS", "", [paint("Choose one or more topics to drill.", GREY)])
    print()
    opts = [(k, k, f"{TOPICS[k]} ({sum(1 for q in BANK if q['topic'] == k)})") for k in TOPICS]
    chosen = checklist(opts)
    if not chosen:
        return
    pool = [q for q in BANK if q["topic"] in chosen]
    n = ask(f"  How many? (1-{len(pool)}, enter = 10) {SYM['prompt']} ")
    n = int(n) if n and n.strip().isdigit() else 10
    play(db, as_items(pick(db, pool, max(1, min(n, len(pool))))), "Topics: " + ", ".join(chosen))


def home(db):
    clear()
    if INTERACTIVE and width() >= 60:
        print()
        lines = logo_lines()
        pad = " " * max(0, (width() - len(lines[0])) // 2)
        for line in lines:
            print(pad + gradient(line, MATRIX, (0, 170, 185), bold=True))
        print(pad + paint("  DCOM 142 // LINUX COMMAND TRAINER", GREY))
        print()
    else:
        print(paint("\nDCOM 142 command trainer", MATRIX, True))
        print("Type the command from memory. Midterm is about modules 1-5.")
    if INTERACTIVE:
        print("  " + rank_line(db))
        print()


def main():
    db = load()
    term_setup()
    if ANIM and "--no-intro" not in ARGS:
        matrix_rain()
    while True:
        home(db)
        miss = sum(1 for q in BANK if is_missed(db, q["id"]))
        options = [
            ("1", "Quick round", "10 mixed, modules 1-5"),
            ("2", "Midterm blitz", "20 from modules 1-5"),
            ("3", "Lightning", "90 seconds, as many as you can"),
            ("4", "Pick topics", "choose what to drill"),
            ("5", "Permission drills", "octal / rwx / umask / SUID math"),
            ("6", "Missed questions", f"{miss} waiting"),
            ("7", "Progress", "rank, mastery by topic"),
            ("q", "Quit", "jack out"),
        ]
        ch = menu(options)
        if ch is None or ch == "q":
            clear()
            print(paint("\n  Connection closed. Good luck on the exam.\n", MATRIX, True))
            return
        if ch == "1":
            play(db, as_items(pick(db, [q for q in BANK if q["topic"] in MIDTERM], 10)), "Quick round")
        elif ch == "2":
            pool = [q for q in BANK if q["topic"] in MIDTERM]
            play(db, as_items(pick(db, pool, 20)), "Midterm blitz")
        elif ch == "3":
            play(db, lightning_source(db), "Lightning", time_limit=90)
        elif ch == "4":
            topic_menu(db)
        elif ch == "5":
            play(db, drill_items(10), "Permission drills")
        elif ch == "6":
            pool = [q for q in BANK if is_missed(db, q["id"])]
            if pool:
                play(db, as_items(pick(db, pool, 15)), "Missed questions")
            else:
                print(paint("\n  No missed questions. Play a round first.", MATRIX))
                wait_key()
        elif ch == "7":
            show_stats(db)
        else:
            print(paint("Pick 1-7 or q.", YELLOW))
        save(db)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        term_restore()
        print(paint("\n  Connection closed.", MATRIX))
