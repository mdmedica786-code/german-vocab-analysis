# Prompt for my AI agent (copy everything in the box)

```
You are helping me (Medica) download the newest version of my German study files from GitHub to my computer.

Repository: https://github.com/mdmedica786-code/german-vocab-analysis
Branch: claude/intelligent-maxwell-ubz9a4   (use this branch, not main)

Steps:
1. If I already have the repo folder on my computer, open a terminal in it and run:
     git fetch origin claude/intelligent-maxwell-ubz9a4
     git checkout claude/intelligent-maxwell-ubz9a4
     git pull origin claude/intelligent-maxwell-ubz9a4
   If I do not have it yet, run:
     git clone --branch claude/intelligent-maxwell-ubz9a4 https://github.com/mdmedica786-code/german-vocab-analysis.git
   If git asks for a login, tell me what to do; do not guess a password.
2. Do not delete or overwrite anything outside this repo folder. If I have my own edits in my Obsidian vault, do not overwrite that vault; copy the new one next to it instead.
3. After the download, open the folders WORD_LISTS and STUDY_HERE and show me these files:
     - German_Study.html            (flashcards; double-click to open in the browser, works offline)
     - (and the folder WORD_LISTS: German_Vault.zip for Obsidian, Word_Lists_by_Level.xlsx, ALL_WORDS.csv, anki_json/)
     - START_HERE.md                (how to use everything)
4. Copy WORD_LISTS/German_Vault.zip to my Desktop (or a folder I tell you) so I can send it to my phone.
5. Check that the numbers are right and tell me: the B2 extra bank should have 4,684 words (vocab_bank/bank_final/b2_vocabulary_bank.csv, 4,685 lines including the header), and the study page should say 13,400 cards in total.
6. Finish with a short list of what you did, in simple words. No technical talk.
```

# Put the vault on my phone (Obsidian mobile)

1. Get `German_Vault.zip` onto the phone: the easiest is to download it directly from GitHub on the phone (open the repo, branch `claude/intelligent-maxwell-ubz9a4`, folder `WORD_LISTS`, tap `German_Vault.zip`, then Download), or send it from the computer by cloud drive / USB / email to yourself.
2. Unzip it on the phone (Files app on Android, Files app on iPhone; tap the zip). You get a folder called `German_Vault`.
3. Android: move the folder to Documents (or any normal folder). iPhone: keep it in "On My iPhone" > Obsidian, or in iCloud Drive > Obsidian.
4. Open Obsidian, tap "Open folder as vault" (Android) or "Create new vault" and pick the existing folder (iPhone), and choose the `German_Vault` folder.
5. Start with the note `00 Home`.

Tip: the vault is large (about 10,000 notes). The first opening on the phone can take a minute while Obsidian indexes it.
